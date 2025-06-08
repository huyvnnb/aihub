# file: app/repositories/base.py

from typing import TypeVar, Generic, Optional, Any, List

from psycopg.errors import UniqueViolation
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import DuplicateEntryError, ApplicationError

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        try:
            await self.session.commit()
            await self.session.refresh(instance)
            return instance
        except IntegrityError as e:
            await self.session.rollback()
            orig = e.orig
            if isinstance(orig, UniqueViolation):
                raise DuplicateEntryError(f"Entry for {self.model.__name__} already exists.") from e
            else:
                raise e

    async def get_by_id(self, instance_id: Any) -> Optional[ModelType]:
        """Phương thức get_by_id chung."""
        return await self.session.get(self.model, instance_id)

    async def get_all(self, *, offset: int, size: int, order_by: Optional[Any] = None) -> List[ModelType]:
        query = select(self.model)

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(offset).limit(size)
        result = await self.session.scalars(query)
        return result.all()

    async def update(self, instance: ModelType):
        self.session.add(instance)
        try:
            await self.session.commit()
            await self.session.refresh(instance)
            return instance
        except IntegrityError as e:
            await self.session.rollback()
            orig = e.orig
            if isinstance(orig, UniqueViolation):
                raise DuplicateEntryError(f"Update failed: entry for {self.model.__name__} already exists.") from e
            else:
                raise e

    async def soft_delete(self, instance_id: Any):
        instance = await self.get_by_id(instance_id)
        if not instance:
            return False
        if hasattr(instance, 'deleted'):
            instance.deleted = True
            self.session.add(instance)
            try:
                await self.session.commit()
                return True
            except IntegrityError as e:
                await self.session.rollback()
                orig = e.orig
                if isinstance(orig, UniqueViolation):
                    raise DuplicateEntryError(f"Delete failed: entry for {self.model.__name__} already exists.") from e
                else:
                    raise e

    async def hard_delete(self, instance_id):
        instance = await self.get_by_id(instance_id)
        if instance:
            await self.session.delete(instance)
            await self.session.commit()
            return True


