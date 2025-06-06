```python
from typing import List, Optional, ForwardRef

from sqlmodel import Field, Relationship, SQLModel, create_engine, Session, select
from fastapi import FastAPI, Depends, HTTPException, Header

# --- Model Definitions ---

# ForwardRef để giải quyết việc tham chiếu vòng (circular dependency)
# nếu Role và Permission tham chiếu lẫn nhau trước khi cả hai được định nghĩa đầy đủ.
# Tuy nhiên, trong trường hợp này, chỉ Permission tham chiếu Role,
# nên có thể không cần ForwardRef nếu Role được định nghĩa trước.
# Nhưng để an toàn, chúng ta vẫn dùng.
_Role = ForwardRef("Role")
_User = ForwardRef("User")

class RolePermissionLink(SQLModel, table=True):
    """Bảng trung gian cho Role và Permission"""
    __tablename__ = "role_permission_link"
    role_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="roles.id")
    permission_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="permissions.id")

class UserRoleLink(SQLModel, table=True):
    """Bảng trung gian cho User và Role"""
    __tablename__ = "user_role_link"
    user_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="users.id")
    role_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="roles.id")

class Permission(SQLModel, table=True):
    __tablename__ = 'permissions'
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True, index=True) # name nên có index
    display_name: Optional[str] = Field(default=None, max_length=100)
    desc: Optional[str] = Field(default=None, nullable=True)
    module: str = Field(nullable=False, max_length=50) # Bỏ Optional đi vì nullable=False

    roles: List["Role"] = Relationship(back_populates="permissions", link_model=RolePermissionLink)

class Role(SQLModel, table=True):
    __tablename__ = 'roles'
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True, index=True)
    display_name: Optional[str] = Field(default=None, max_length=100)

    permissions: List[Permission] = Relationship(back_populates="roles", link_model=RolePermissionLink)
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)

class User(SQLModel, table=True):
    __tablename__ = 'users'
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str # Trong thực tế sẽ lưu mật khẩu đã hash

    roles: List[Role] = Relationship(back_populates="users", link_model=UserRoleLink)

# --- Database Setup ---
DATABASE_URL = "sqlite:///./test.db" # Sử dụng SQLite cho ví dụ
engine = create_engine(DATABASE_URL, echo=True) # echo=True để xem câu lệnh SQL

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# --- Dependency để lấy DB Session ---
def get_session():
    with Session(engine) as session:
        yield session

# --- Logic kiểm tra quyền ---
def user_has_permission(user: User, permission_name: str) -> bool:
    if not user or not user.roles:
        return False
    for role in user.roles:
        if not role.permissions: # Cần load permissions cho role nếu chưa load
            # Trong một số ORM, bạn có thể cần load tường minh,
            # hoặc đảm bảo query đã eager load.
            # Với SQLModel và FastAPI, khi bạn query user và join roles,
            # rồi join permissions, chúng sẽ được load.
            # Tuy nhiên, nếu bạn chỉ load user và roles, permissions có thể chưa có.
            # Giả sử ở đây permissions của role đã được load.
            pass
        for perm in role.permissions:
            if perm.name == permission_name:
                return True
    return False

# --- Dependency để kiểm tra quyền ---
# Đây là một class dependency, cho phép truyền tham số (permission_name) vào
class PermissionChecker:
    def __init__(self, permission_name: str):
        self.permission_name = permission_name

    def __call__(self, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
        # Tải lại user với các relationship cần thiết nếu chưa có
        # Điều này quan trọng để đảm bảo roles và permissions của roles được load
        db_user = session.get(User, current_user.id)
        if not db_user: # Nên có check này trong get_current_user
            raise HTTPException(status_code=401, detail="Invalid user")

        if not user_has_permission(db_user, self.permission_name):
            raise HTTPException(
                status_code=403,
                detail=f"User does not have permission: '{self.permission_name}'"
            )
        return db_user # Trả về user nếu có quyền, hoặc không trả gì cũng được

# --- Mockup hàm lấy user hiện tại (trong thực tế sẽ dùng OAuth2, JWT, ...) ---
async def get_current_user(user_id: Optional[int] = Header(None, alias="X-User-ID"), session: Session = Depends(get_session)) -> User:
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated, missing X-User-ID header")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")
    return user

# --- FastAPI App ---
app = FastAPI()

# --- Route ví dụ ---
# Giả sử chúng ta cần quyền 'article:create' để tạo bài viết
REQUIRE_CREATE_ARTICLE_PERMISSION = "article:create"

@app.post("/articles/", summary="Create a new article")
async def create_article(
    article_data: dict, # Dữ liệu bài viết gửi lên
    current_user: User = Depends(PermissionChecker(REQUIRE_CREATE_ARTICLE_PERMISSION)),
    session: Session = Depends(get_session)
):
    # Nếu code chạy đến đây, nghĩa là user đã có quyền 'article:create'
    # (do PermissionChecker đã kiểm tra và không raise HTTPException)
    print(f"User '{current_user.username}' (ID: {current_user.id}) is creating an article.")
    # Logic tạo bài viết ở đây...
    # new_article = Article(**article_data, author_id=current_user.id)
    # session.add(new_article)
    # session.commit()
    # session.refresh(new_article)
    return {"message": "Article created successfully (simulated)", "data": article_data, "created_by": current_user.username}

@app.get("/articles/protected-view", summary="View protected article info")
async def view_protected_article(
    current_user: User = Depends(PermissionChecker("article:view_protected"))
):
    return {"message": "You have access to protected article info!", "user": current_user.username}


# --- Setup dữ liệu mẫu (chạy một lần khi khởi động) ---
def setup_sample_data(session: Session):
    # Xóa dữ liệu cũ (nếu có, cho mục đích demo)
    # Trong thực tế không nên làm thế này tự động
    session.query(UserRoleLink).delete()
    session.query(RolePermissionLink).delete()
    session.query(User).delete()
    session.query(Role).delete()
    session.query(Permission).delete()
    session.commit()


    # Tạo Permissions
    perm_create_article = Permission(name="article:create", display_name="Tạo Bài Viết", module="Bài Viết")
    perm_edit_article = Permission(name="article:edit", display_name="Sửa Bài Viết", module="Bài Viết")
    perm_publish_article = Permission(name="article:publish", display_name="Xuất Bản Bài Viết", module="Bài Viết")
    perm_view_protected = Permission(name="article:view_protected", display_name="Xem Thông Tin Bảo Mật", module="Bài Viết")
    perm_manage_users = Permission(name="user:manage", display_name="Quản Lý Người Dùng", module="Người Dùng")

    session.add_all([perm_create_article, perm_edit_article, perm_publish_article, perm_view_protected, perm_manage_users])
    session.commit() # Commit để permissions có ID

    # Tạo Roles
    role_editor = Role(name="editor", display_name="Biên Tập Viên")
    role_admin = Role(name="admin", display_name="Quản Trị Viên")
    role_viewer = Role(name="viewer", display_name="Người Xem")

    # Gán Permissions cho Roles
    role_editor.permissions.extend([perm_create_article, perm_edit_article])
    role_admin.permissions.extend([perm_create_article, perm_edit_article, perm_publish_article, perm_manage_users, perm_view_protected])
    role_viewer.permissions.append(perm_view_protected) # Viewer chỉ có thể xem protected

    session.add_all([role_editor, role_admin, role_viewer])
    session.commit() # Commit để roles có ID và link tables được cập nhật

    # Tạo Users
    user_alice = User(username="alice", hashed_password="hashed_password_alice") # Editor
    user_bob = User(username="bob", hashed_password="hashed_password_bob")       # Admin
    user_charlie = User(username="charlie", hashed_password="hashed_password_charlie") # Viewer
    user_dave = User(username="dave", hashed_password="hashed_password_dave")     # No roles, no specific permissions

    # Gán Roles cho Users
    user_alice.roles.append(role_editor)
    user_bob.roles.append(role_admin)
    user_charlie.roles.append(role_viewer)
    # user_dave không có role nào

    session.add_all([user_alice, user_bob, user_charlie, user_dave])
    session.commit()

    print("Sample data created.")
    print(f"Alice (ID: {user_alice.id}) is an Editor.")
    print(f"Bob (ID: {user_bob.id}) is an Admin.")
    print(f"Charlie (ID: {user_charlie.id}) is a Viewer.")
    print(f"Dave (ID: {user_dave.id}) has no roles.")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    with Session(engine) as session:
        # Kiểm tra xem có user nào chưa để tránh tạo lại dữ liệu mỗi lần start
        # Điều này chỉ nên làm cho demo
        if not session.exec(select(User)).first():
            setup_sample_data(session)
        else:
            print("Database already contains data. Skipping sample data setup.")

# Để chạy: uvicorn ten_file:app --reload
# Ví dụ: uvicorn main:app --reload
```