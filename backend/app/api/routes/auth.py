"""Authentication endpoints: register, login, logout, and me."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.schemas.user import UserResponse, UserUpdate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a user account, hashes credentials using PBKDF2, and returns a JWT access token.",
)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    return AuthService.register_user(db, request)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate and receive JWT token",
    description="Validates email and password, issuing an authentication JWT.",
)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    return AuthService.login_user(db, request)


@router.post(
    "/logout",
    summary="Invalidate client session",
    description="Acknowledges client session termination.",
)
def logout(current_user: User = Depends(get_current_user)) -> dict:
    return {"message": "Logged out successfully."}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns profile details of the currently authenticated account.",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    description="Updates user profile attributes such as name, role, bio, and avatar.",
)
def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, val in update_dict.items():
        setattr(current_user, key, val)
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)
