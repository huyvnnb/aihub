# Thiết kế DB và Xóa Mềm với SQLModel, FastAPI & PostgreSQL

Tài liệu này tổng kết các phương pháp tốt nhất để thiết kế model SQLModel bao gồm các trường timestamp (`created_at`, `updated_at`) và chức năng xóa mềm (`deleted_at`), cùng với cách sử dụng chúng trong ứng dụng FastAPI.

## 1. Thiết kế Base Model trong SQLModel

Chúng ta sẽ tạo các base model để quản lý các trường chung một cách nhất quán.

### `core/db_base_model.py`

```python
from datetime import datetime
from typing import Optional, TypeVar, Type, cast, List # Sửa lại List

from sqlmodel import Field, SQLModel, Session, select
from sqlalchemy import Column, DateTime, func # Import cho sa_column và func.now()

# Generic TypeVar để sử dụng trong các phương thức class
# Cần định nghĩa lại cho từng base class nếu bound khác nhau
TimestampedModelType = TypeVar("TimestampedModelType", bound="TimestampedSQLModel")
SoftDeleteModelType = TypeVar("SoftDeleteModelType", bound="SoftDeleteBase")

class TimestampedSQLModel(SQLModel):
    """
    Base model cung cấp các trường created_at và updated_at.
    Sử dụng server_default và onupdate của SQLAlchemy/DB để đảm bảo tính nhất quán.
    """
    # Sử dụng sa_column để định nghĩa cột SQLAlchemy một cách rõ ràng,
    # đặc biệt khi cần các tùy chọn như timezone=True.
    created_at: datetime = Field(
        default=None, # Sẽ được set bởi server_default
        nullable=False,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        default=None, # Sẽ được set bởi server_default và onupdate
        nullable=False,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )

class SoftDeleteBase(TimestampedSQLModel): # Kế thừa từ TimestampedSQLModel
    """
    Base model cung cấp chức năng xóa mềm và kế thừa các trường timestamp.
    """
    deleted_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        index=True,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True) # Rõ ràng hơn với timezone
    )

    def soft_delete(self: SoftDeleteModelType, db_session: Session) -> SoftDeleteModelType:
        """Đánh dấu bản ghi là đã xóa mềm."""
        # self.deleted_at = datetime.now(timezone.utc) # Nếu muốn set từ Python với timezone
        # Hoặc để DB tự set nếu dùng trigger (phức tạp hơn)
        # Với cách này, ta set thủ công từ Python
        self.deleted_at = db_session.execute(select(func.now())).scalar_one() # Lấy thời gian hiện tại từ DB
        # updated_at sẽ tự động cập nhật bởi DB do onupdate=func.now()
        db_session.add(self)
        return self

    def restore(self: SoftDeleteModelType, db_session: Session) -> SoftDeleteModelType:
        """Khôi phục một bản ghi đã bị xóa mềm."""
        self.deleted_at = None
        # updated_at sẽ tự động cập nhật bởi DB
        db_session.add(self)
        return self

    @classmethod
    def query_active(cls: Type[SoftDeleteModelType], db_session: Session):
        """Tạo statement để truy vấn các bản ghi đang hoạt động."""
        return select(cls).where(cls.deleted_at == None)

    @classmethod
    def query_deleted(cls: Type[SoftDeleteModelType], db_session: Session):
        """Tạo statement để truy vấn các bản ghi đã bị xóa mềm."""
        return select(cls).where(cls.deleted_at != None)

    @classmethod
    def get_active_by_id(cls: Type[SoftDeleteModelType], db_session: Session, obj_id: int) -> Optional[SoftDeleteModelType]:
        """Lấy một bản ghi đang hoạt động theo ID."""
        # Giả sử các model kế thừa sẽ có một trường 'id'
        # Cần đảm bảo 'id' được định nghĩa trong model con hoặc một base class khác
        statement = cls.query_active(db_session).where(cast(SQLModel, cls).id == obj_id)
        return db_session.exec(statement).first()

    @classmethod
    def get_all_active(cls: Type[SoftDeleteModelType], db_session: Session, offset: int = 0, limit: int = 100) -> List[SoftDeleteModelType]:
        """Lấy danh sách các bản ghi đang hoạt động."""
        statement = cls.query_active(db_session).offset(offset).limit(limit)
        results = db_session.exec(statement).all()
        return results # Đã sửa lại

    # models/user_model.py

    from typing import Optional
    from sqlmodel import Field, SQLModel # SQLModel được dùng làm base cho UserBase
    from datetime import datetime # Import datetime
    
    from core.db_base_model import SoftDeleteBase # Import base model
    
    # Pydantic schemas (cũng là SQLModel) cho API
    class UserBase(SQLModel):
        username: str = Field(unique=False, index=True) # Sửa unique=False để partial index xử lý
        email: str = Field(unique=False, index=True)    # Sửa unique=False để partial index xử lý
        full_name: Optional[str] = None
    
    class UserCreate(UserBase):
        password: str
    
    class UserRead(UserBase):
        id: int
        created_at: datetime # Thêm vào schema đọc nếu muốn expose
        updated_at: datetime # Thêm vào schema đọc nếu muốn expose
    
    class UserReadWithSoftDelete(UserRead): # Schema có thể bao gồm cả deleted_at nếu cần
        deleted_at: Optional[datetime] = None
    
    # DB Model
    class User(SoftDeleteBase, UserBase, table=True):
        # created_at, updated_at, deleted_at đã được kế thừa từ SoftDeleteBase
        # username, email, full_name được kế thừa từ UserBase
    
        id: Optional[int] = Field(default=None, primary_key=True)
        hashed_password: str
    
        # QUAN TRỌNG: Partial Unique Indexes
        # Phải được tạo trong DB migration (ví dụ: Alembic)
        # CREATE UNIQUE INDEX uq_users_active_email ON users (email) WHERE deleted_at IS NULL;
        # CREATE UNIQUE INDEX uq_users_active_username ON users (username) WHERE deleted_at IS NULL;

    # service

    from typing import List, Optional
    from sqlmodel import Session, select
    
    from models.user import User, UserCreate # Model và schema
    # from core.security import get_password_hash # Hàm băm mật khẩu thực tế
    
    def get_password_hash(password: str) -> str: # Dummy function
        return f"hashed_{password}"
    
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Lấy user đang hoạt động theo ID."""
        return User.get_active_by_id(db, user_id)
    
    def get_active_user_by_email(db: Session, email: str) -> Optional[User]:
        """Kiểm tra email đã tồn tại với user đang hoạt động."""
        statement = User.query_active(db).where(User.email == email)
        return db.exec(statement).first()
    
    def get_active_user_by_username(db: Session, username: str) -> Optional[User]:
        """Kiểm tra username đã tồn tại với user đang hoạt động."""
        statement = User.query_active(db).where(User.username == username)
        return db.exec(statement).first()
    
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Lấy danh sách user đang hoạt động."""
        return User.get_all_active(db, offset=skip, limit=limit)
    
    def create_user(db: Session, user_in: UserCreate) -> User:
        """Tạo user mới."""
        if get_active_user_by_email(db, email=user_in.email):
            raise ValueError(f"Email '{user_in.email}' is already registered by an active user.")
        if get_active_user_by_username(db, username=user_in.username):
            raise ValueError(f"Username '{user_in.username}' is already registered by an active user.")
    
        hashed_password = get_password_hash(user_in.password)
        user_data = user_in.model_dump(exclude={"password"})
        db_user = User(**user_data, hashed_password=hashed_password)
        # created_at và updated_at sẽ được DB tự động xử lý
    
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def soft_delete_user(db: Session, user_id: int) -> Optional[User]:
        """Xóa mềm user."""
        db_user = get_user_by_id(db, user_id)
        if db_user:
            db_user.soft_delete(db) # updated_at sẽ được DB tự động cập nhật
            db.commit()
            db.refresh(db_user)
        return db_user
    
    def restore_user(db: Session, user_id: int) -> Optional[User]:
        """Khôi phục user đã xóa mềm."""
        # Lấy user đã bị xóa (không dùng get_user_by_id vì nó chỉ lấy active)
        statement = User.query_deleted(db).where(User.id == user_id)
        db_user = db.exec(statement).first()
        if db_user:
            db_user.restore(db) # updated_at sẽ được DB tự động cập nhật
            db.commit()
            db.refresh(db_user)
        return db_user
    
    def get_any_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Lấy user bất kể trạng thái xóa (dùng db.get)."""
        return db.get(User, user_id)

    # endpoint

    from fastapi import APIRouter, Depends, HTTPException
    from sqlmodel import Session
    from typing import List
    
    from models.user import UserCreate, UserRead, UserReadWithSoftDelete # Schemas
    from services import user_service
    from core.dependencies import get_db # Dependency để inject DB session
    
    router = APIRouter(prefix="/users", tags=["users"])
    
    @router.post("/", response_model=UserRead)
    def create_user_endpoint(user_in: UserCreate, db: Session = Depends(get_db)):
        try:
            return user_service.create_user(db=db, user_in=user_in)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/", response_model=List[UserRead])
    def read_users_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        return user_service.get_users(db, skip=skip, limit=limit)
    
    @router.get("/{user_id}", response_model=UserRead)
    def read_user_endpoint(user_id: int, db: Session = Depends(get_db)):
        db_user = user_service.get_user_by_id(db, user_id=user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="Active user not found")
        return db_user
    
    @router.delete("/{user_id}", response_model=UserReadWithSoftDelete) # Trả về chi tiết cả deleted_at
    def soft_delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
        deleted_user = user_service.soft_delete_user(db, user_id=user_id)
        if not deleted_user:
            raise HTTPException(status_code=404, detail="Active user not found to delete")
        return deleted_user
    
    @router.post("/{user_id}/restore", response_model=UserRead)
    def restore_user_endpoint(user_id: int, db: Session = Depends(get_db)):
        restored_user = user_service.restore_user(db, user_id=user_id)
        if not restored_user:
            raise HTTPException(status_code=404, detail="User not found or not in a deleted state to restore")
        return restored_user
```