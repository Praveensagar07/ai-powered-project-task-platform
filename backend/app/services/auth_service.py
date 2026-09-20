"""Authentication service managing registration, credentials, and token issuance."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.activity import Activity
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse


class AuthService:
    """Handles user authentication workflows and credential management."""

    @staticmethod
    def register_user(db: Session, request: RegisterRequest) -> AuthResponse:
        """Register a new user account if email is not already taken."""
        existing = db.query(User).filter(User.email == request.email.lower()).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists.",
            )

        hashed = hash_password(request.password)
        new_user = User(
            name=request.name.strip(),
            email=request.email.lower().strip(),
            password_hash=hashed,
            role=request.role or "Full Stack Developer",
            avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={request.name.strip()}",
            bio="Full Stack Developer focused on building high-impact digital applications.",
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Log registration activity
        activity = Activity(
            user_id=new_user.id,
            user_name=new_user.name,
            user_avatar=new_user.avatar,
            type="user_registered",
            title=f"{new_user.name} joined the platform",
            description="Created account and initialized workspace.",
            target_type="user",
            target_id=new_user.id,
        )
        db.add(activity)
        db.commit()

        token = create_access_token({"sub": new_user.id, "email": new_user.email})
        return AuthResponse(
            user=UserResponse.model_validate(new_user),
            token=TokenResponse(access_token=token, expires_in=1440 * 60),
        )

    @staticmethod
    def login_user(db: Session, request: LoginRequest) -> AuthResponse:
        """Authenticate user credentials and issue a fresh JWT access token."""
        user = db.query(User).filter(User.email == request.email.lower()).first()
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token({"sub": user.id, "email": user.email})
        return AuthResponse(
            user=UserResponse.model_validate(user),
            token=TokenResponse(access_token=token, expires_in=1440 * 60),
        )

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User:
        """Retrieve user entity by primary ID."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found.",
            )
        return user
