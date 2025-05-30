# messages.py

# --- General Messages ---
SUCCESS = "Operation completed successfully."
ERROR_UNEXPECTED = "An unexpected error occurred. Please try again later."
INVALID_INPUT = "Invalid input provided. Please check your data."
RESOURCE_NOT_FOUND = "The requested resource was not found."
UNAUTHORIZED_ACCESS = "You are not authorized to perform this action."
FORBIDDEN_ACCESS = "You do not have permission to access this resource."
VALIDATION_ERROR = "Input validation failed. Please check the errors."
RATE_LIMIT_EXCEEDED = "Too many requests. Please try again later."
SERVICE_UNAVAILABLE = "The service is temporarily unavailable. Please try again later."


# --- Authentication (Auth) Module Messages ---
class Auth:
    LOGIN_SUCCESS = "Login successful. Welcome back!"
    LOGIN_FAILED = "Invalid credentials. Please check your email/username and password."
    LOGOUT_SUCCESS = "You have been successfully logged out."
    REGISTRATION_SUCCESS = "Registration successful. A verification link has been sent to your email."
    REGISTRATION_FAILED = "Registration failed. Please try again."
    EMAIL_VERIFICATION_SUCCESS = "Your email has been successfully verified. You can now log in."
    EMAIL_VERIFICATION_FAILED = "Email verification failed. The link may be invalid or expired."
    EMAIL_ALREADY_VERIFIED = "This email address has already been verified."
    VERIFICATION_EMAIL_SENT = "A new verification email has been sent. Please check your inbox."
    PASSWORD_RESET_REQUEST_SUCCESS = "If an account with that email exists, password reset instructions have been sent."
    PASSWORD_RESET_SUCCESS = "Your password has been successfully reset. You can now log in with your new password."
    INVALID_TOKEN = "Invalid or expired token. Please request a new one."
    TOKEN_REFRESH_SUCCESS = "Access token refreshed successfully."
    TOKEN_REQUIRED = "Authentication token is required."
    TOKEN_EXPIRED = "Authentication token has expired. Please log in again."
    TOKEN_INVALID_SIGNATURE = "Invalid token signature."
    MFA_CHALLENGE_ISSUED = "Multi-Factor Authentication required. Please enter the code from your authenticator app."
    MFA_CODE_INVALID = "Invalid Multi-Factor Authentication code."
    MFA_SETUP_SUCCESS = "Multi-Factor Authentication has been set up successfully."
    MFA_DISABLED_SUCCESS = "Multi-Factor Authentication has been disabled."
    ACCOUNT_LOCKED = "Your account has been locked due to too many failed login attempts. Please try again later or reset your password."
    ACCOUNT_DISABLED = "Your account has been disabled. Please contact support."
    ACCOUNT_NOT_YET_ACTIVE = "Your account is not yet active. Please verify your email first."


# --- User Module Messages ---
class User:
    CREATED_SUCCESS = "User created successfully."
    UPDATED_SUCCESS = "User profile updated successfully."
    DELETED_SUCCESS = "User account deleted successfully."
    FETCHED_SUCCESS = "User details retrieved successfully."
    LIST_FETCHED_SUCCESS = "List of users retrieved successfully."
    USER_NOT_FOUND = "User not found."
    EMAIL_ALREADY_EXISTS = "This email address is already in use by another account."
    USERNAME_ALREADY_EXISTS = "This username is already taken. Please choose another one."
    PASSWORD_CHANGE_SUCCESS = "Password changed successfully."
    CURRENT_PASSWORD_INVALID = "The current password you entered is incorrect."
    CANNOT_DELETE_SELF = "You cannot delete your own account through this action."
    PROFILE_PICTURE_UPDATED = "Profile picture updated successfully."
    PROFILE_PICTURE_REMOVED = "Profile picture removed successfully."


# --- Role Module Messages ---
class Role:
    CREATED_SUCCESS = "Role '{role_name}' created successfully."
    UPDATED_SUCCESS = "Role '{role_name}' updated successfully."
    DELETED_SUCCESS = "Role '{role_name}' deleted successfully."
    FETCHED_SUCCESS = "Role details retrieved successfully."
    LIST_FETCHED_SUCCESS = "List of roles retrieved successfully."
    ROLE_NOT_FOUND = "Role not found."
    ROLE_ALREADY_EXISTS = "A role with the name '{role_name}' already exists."
    ROLE_IN_USE = "Cannot delete role '{role_name}' as it is currently assigned to one or more users."
    PERMISSION_ASSIGNED_SUCCESS = "Permission '{permission_name}' assigned to role '{role_name}'."
    PERMISSION_REMOVED_SUCCESS = "Permission '{permission_name}' removed from role '{role_name}'."
    PERMISSION_NOT_FOUND = "Permission not found."
    INVALID_PERMISSION_FOR_ROLE = "Permission '{permission_name}' is not valid for assignment."
    DEFAULT_ROLE_MODIFICATION_RESTRICTED = "Default roles cannot be modified or deleted."


# --- Admin Module Messages (Actions performed by an Admin, often on other entities) ---
class Admin:
    FETCH_USER = "Fetch user successfully."
    FETCH_USER_LIST = "Fetch user list successfully"
    USER_BANNED_SUCCESS = "User '{username}' has been successfully banned."
    USER_UNBANNED_SUCCESS = "User '{username}' has been successfully unbanned."
    USER_ROLE_UPDATED_SUCCESS = "Roles for user '{username}' updated successfully."
    USER_ACCOUNT_ACTIVATED = "User account for '{username}' has been activated."
    USER_ACCOUNT_DEACTIVATED = "User account for '{username}' has been deactivated."
    SETTINGS_UPDATED_SUCCESS = "System settings updated successfully."
    BULK_ACTION_SUCCESS = "{count} items processed successfully."
    BULK_ACTION_PARTIAL_SUCCESS = "{success_count} items processed successfully, {fail_count} items failed."
    BULK_ACTION_FAILED = "Bulk action failed for all items."
    AUDIT_LOG_RETRIEVED = "Audit logs retrieved successfully."
    CACHE_CLEARED_SUCCESS = "System cache cleared successfully."
    SYSTEM_HEALTH_OK = "System health check passed. All services are operational."
    SYSTEM_HEALTH_WARNING = "System health check has warnings. Please review."
    SYSTEM_HEALTH_CRITICAL = "System health check critical. Immediate attention required."


# --- Generic placeholders / Helper functions ---
def item_created(item_name: str) -> str:
    return f"{item_name.capitalize()} created successfully."


def item_updated(item_name: str) -> str:
    return f"{item_name.capitalize()} updated successfully."


def item_deleted(item_name: str) -> str:
    return f"{item_name.capitalize()} deleted successfully."


def item_not_found(item_name: str) -> str:
    return f"{item_name.capitalize()} not found."


def item_already_exists(item_name: str, value: str) -> str:
    return f"A {item_name.lower()} with the {value} already exists."


def field_required(field_name: str) -> str:
    return f"{field_name.capitalize()} is required."


def invalid_value_for_field(field_name: str, value: str) -> str:
    return f"Invalid value '{value}' for {field_name.lower()}."
