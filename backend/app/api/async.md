# ====== SQLMODEL SETUP ======
```python
from sqlmodel import SQLModel, Field, create_engine, Session, select, Relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import Optional, List, AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from abc import ABC, abstractmethod
import asyncio

# Models
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    name: str
    is_active: bool = True

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    orders: List["Order"] = Relationship(back_populates="user")

class OrderBase(SQLModel):
    title: str
    description: Optional[str] = None
    price: float

class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="orders")

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine("sqlite:///./test.db", echo=True)
SyncSessionLocal = sessionmaker(bind=sync_engine)


# ====== UNIT OF WORK PATTERN ======

class BaseUnitOfWork(ABC):
    """Abstract Unit of Work"""
    
    @abstractmethod
    async def __aenter__(self):
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    @abstractmethod
    async def commit(self):
        pass
    
    @abstractmethod
    async def rollback(self):
        pass

class AsyncSQLModelUnitOfWork(BaseUnitOfWork):
    """Async Unit of Work cho SQLModel"""
    
    def __init__(self):
        self.session: Optional[AsyncSession] = None
        self._user_repo: Optional["AsyncUserRepository"] = None
        self._order_repo: Optional["AsyncOrderRepository"] = None
    
    async def __aenter__(self):
        self.session = AsyncSessionLocal()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()
    
    async def commit(self):
        await self.session.commit()
    
    async def rollback(self):
        await self.session.rollback()
    
    @property
    def user_repo(self):
        if self._user_repo is None:
            self._user_repo = AsyncUserRepository(self.session)
        return self._user_repo
    
    @property  
    def order_repo(self):
        if self._order_repo is None:
            self._order_repo = AsyncOrderRepository(self.session)
        return self._order_repo

# Sync version cho trường hợp cần
class SyncSQLModelUnitOfWork:
    def __init__(self):
        self.session: Optional[Session] = None
        self._user_repo: Optional["SyncUserRepository"] = None
        self._order_repo: Optional["SyncOrderRepository"] = None
    
    def __enter__(self):
        self.session = SyncSessionLocal()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
    
    @property
    def user_repo(self):
        if self._user_repo is None:
            self._user_repo = SyncUserRepository(self.session)
        return self._user_repo


# ====== REPOSITORY PATTERN ======

class AsyncUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        statement = select(User).where(User.id == user_id)
        result = await self.session.exec(statement)
        return result.first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        result = await self.session.exec(statement)
        return result.first()
    
    async def get_with_orders(self, user_id: int) -> Optional[User]:
        """Lấy user với orders để tránh N+1 queries"""
        statement = select(User).where(User.id == user_id)
        result = await self.session.exec(statement)
        user = result.first()
        if user:
            # Eager load orders
            await self.session.refresh(user, ["orders"])
        return user
    
    async def create(self, user_data: UserBase) -> User:
        user = User.model_validate(user_data)
        self.session.add(user)
        await self.session.flush()  # Để lấy ID
        return user
    
    async def update(self, user_id: int, user_data: dict) -> Optional[User]:
        user = await self.get_by_id(user_id)
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            await self.session.flush()
        return user
    
    async def delete(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            return True
        return False

class AsyncOrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, order_data: OrderBase, user_id: int) -> Order:
        order_dict = order_data.model_dump()
        order_dict["user_id"] = user_id
        order = Order(**order_dict)
        self.session.add(order)
        await self.session.flush()
        return order
    
    async def get_by_user(self, user_id: int) -> List[Order]:
        statement = select(Order).where(Order.user_id == user_id)
        result = await self.session.exec(statement)
        return result.all()

class SyncUserRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, user_data: UserBase) -> User:
        user = User.model_validate(user_data)
        self.session.add(user)
        self.session.flush()
        return user


# ====== SERVICE LAYER ======

class UserService:
    """Service sử dụng UnitOfWork pattern"""
    
    async def register_user(self, user_data: UserBase) -> User:
        async with AsyncSQLModelUnitOfWork() as uow:
            # Kiểm tra email đã tồn tại
            existing_user = await uow.user_repo.get_by_email(user_data.email)
            if existing_user:
                raise ValueError("Email already exists")
            
            user = await uow.user_repo.create(user_data)
            # UnitOfWork tự động commit khi exit context
            return user
    
    async def create_user_with_order(
        self, 
        user_data: UserBase, 
        order_data: OrderBase
    ) -> tuple[User, Order]:
        """Complex transaction với multiple operations"""
        async with AsyncSQLModelUnitOfWork() as uow:
            # Tạo user
            user = await uow.user_repo.create(user_data)
            
            # Tạo order cho user vừa tạo
            order = await uow.order_repo.create(order_data, user.id)
            
            # Cả 2 operations trong cùng transaction
            return user, order
    
    async def get_user_profile(self, user_id: int) -> Optional[User]:
        """Lấy user với tất cả orders"""
        async with AsyncSQLModelUnitOfWork() as uow:
            return await uow.user_repo.get_with_orders(user_id)
    
    async def update_user_status(self, user_id: int, is_active: bool) -> Optional[User]:
        async with AsyncSQLModelUnitOfWork() as uow:
            return await uow.user_repo.update(user_id, {"is_active": is_active})

class OrderService:
    async def create_order_for_user(
        self, 
        user_id: int, 
        order_data: OrderBase
    ) -> Order:
        async with AsyncSQLModelUnitOfWork() as uow:
            # Kiểm tra user tồn tại
            user = await uow.user_repo.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
                
            return await uow.order_repo.create(order_data, user_id)


# ====== FASTAPI DEPENDENCY INJECTION ======

from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated

app = FastAPI()

# Dependency providers
def get_user_service() -> UserService:
    return UserService()

def get_order_service() -> OrderService:
    return OrderService()

# Type aliases
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]

# Request/Response models
class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    user_id: int


# ====== ROUTES ======

@app.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    user_service: UserServiceDep
):
    try:
        user = await user_service.register_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/users/{user_id}/orders", response_model=OrderResponse)
async def create_order(
    user_id: int,
    order_data: OrderCreate,
    order_service: OrderServiceDep
):
    try:
        order = await order_service.create_order_for_user(user_id, order_data)
        return order
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/users-with-order")
async def create_user_with_order(
    user_data: UserCreate,
    order_data: OrderCreate,
    user_service: UserServiceDep
):
    """Complex transaction example"""
    try:
        user, order = await user_service.create_user_with_order(user_data, order_data)
        return {
            "user": user,
            "order": order
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: int,
    user_service: UserServiceDep
):
    user = await user_service.get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    user_service: UserServiceDep
):
    user = await user_service.update_user_status(user_id, is_active)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ====== TESTING ======

import pytest
from unittest.mock import AsyncMock

class MockAsyncUnitOfWork(AsyncSQLModelUnitOfWork):
    def __init__(self):
        self.committed = False
        self.rolled_back = False
        self.user_repo = AsyncMock()
        self.order_repo = AsyncMock()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rolled_back = True
        else:
            self.committed = True
    
    async def commit(self):
        self.committed = True
    
    async def rollback(self):
        self.rolled_back = True

@pytest.mark.asyncio
async def test_user_service_register():
    # Test với mock UoW
    mock_uow = MockAsyncUnitOfWork()
    
    # Mock repository behavior
    mock_uow.user_repo.get_by_email.return_value = None
    mock_user = User(id=1, email="test@example.com", name="Test")
    mock_uow.user_repo.create.return_value = mock_user
    
    # Test
    service = UserService()
    # Trong thực tế, bạn sẽ cần dependency injection cho UoW
    user_data = UserCreate(email="test@example.com", name="Test")
    
    # Verify mock calls
    assert mock_uow.user_repo.get_by_email.called
    assert mock_uow.user_repo.create.called

# ====== ERROR HANDLING & PATTERNS ======

class DatabaseError(Exception):
    """Custom database exception"""
    pass

class UserNotFoundError(Exception):
    """User not found exception"""
    pass

# Enhanced service với error handling
class EnhancedUserService:
    async def safe_register_user(self, user_data: UserBase) -> User:
        try:
            async with AsyncSQLModelUnitOfWork() as uow:
                existing_user = await uow.user_repo.get_by_email(user_data.email)
                if existing_user:
                    raise ValueError("Email already exists")
                
                user = await uow.user_repo.create(user_data)
                return user
                
        except Exception as e:
            # Log error here
            raise DatabaseError(f"Failed to create user: {str(e)}")

# ====== PERFORMANCE OPTIMIZATION ======

class OptimizedUserService:
    """Service với các optimization patterns"""
    
    async def bulk_create_users(self, users_data: List[UserBase]) -> List[User]:
        """Bulk operations trong single transaction"""
        async with AsyncSQLModelUnitOfWork() as uow:
            created_users = []
            for user_data in users_data:
                user = await uow.user_repo.create(user_data)
                created_users.append(user)
            
            # Tất cả users được tạo trong 1 transaction
            return created_users
    
    async def get_users_with_orders_optimized(
        self, 
        user_ids: List[int]
    ) -> List[User]:
        """Tránh N+1 queries"""
        async with AsyncSQLModelUnitOfWork() as uow:
            # Single query với eager loading
            statement = (
                select(User)
                .where(User.id.in_(user_ids))
                .options(selectinload(User.orders))
            )
            result = await uow.session.exec(statement)
            return result.all()
```