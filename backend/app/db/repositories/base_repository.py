# file: app/repositories/base.py

from typing import TypeVar, Generic, Optional, Any, List

from psycopg.errors import UniqueViolation
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import DuplicateEntryError, ApplicationError
from app.utils.logger import get_logger, Module

ModelType = TypeVar("ModelType")

logger = get_logger(Module.BASE_REPO)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
        # try:
        #     await self.session.commit()
        #     await self.session.refresh(instance)
        #     return instance
        # except IntegrityError as e:
        #     await self.session.rollback()
        #     orig = e.orig
        #     if isinstance(orig, UniqueViolation):
        #         raise DuplicateEntryError(f"Entry for {self.model.__name__} already exists.") from e
        #     else:
        #         raise e

    async def create_many(self, instances: List[dict]) -> List[ModelType]:
        if not instances:
            return []
        stm = insert(self.model).values(instances).returning(self.model)
        result = await self.session.execute(stm)
        return result.scalars().all()
        # if not instances:
        #     return []
        #
        # try:
        #     stm = insert(self.model).values(instances).returning(self.model)
        #     logger.info(stm)
        #
        #     result = await self.session.execute(stm)
        #     await self.session.commit()
        #     return result.scalars().all()
        # except IntegrityError as e:
        #     await self.session.rollback()
        #     orig = e.orig
        #     if isinstance(orig, UniqueViolation):
        #         raise DuplicateEntryError(f"Entry for {self.model.__name__} already exists.") from e
        #     else:
        #         raise e

    async def get_by_id(self, instance_id: Any, load_options: Optional[List] = None) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == instance_id)
        if load_options:
            query.options(*load_options)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()
        # return await self.session.get(self.model, instance_id)

    async def get_all(self, *, offset: int, size: int, order_by: Optional[Any] = None) -> List[ModelType]:
        query = select(self.model)

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(offset).limit(size)
        result = await self.session.scalars(query)
        return result.all()

    async def update(self, instance: ModelType):
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
        # self.session.add(instance)
        # try:
        #     await self.session.commit()
        #     await self.session.refresh(instance)
        #     return instance
        # except IntegrityError as e:
        #     await self.session.rollback()
        #     orig = e.orig
        #     if isinstance(orig, UniqueViolation):
        #         raise DuplicateEntryError(f"Update failed: entry for {self.model.__name__} already exists.") from e
        #     else:
        #         raise e

    async def delete(self, instance_id):
        instance = await self.get_by_id(instance_id)
        if instance:
            await self.session.delete(instance)
            await self.session.flush()  # Để đảm bảo thao tác delete được đưa vào session
            return True
        return False
        # instance = await self.get_by_id(instance_id)
        # if instance:
        #     await self.session.delete(instance)
        #     await self.session.commit()
        #     return True
