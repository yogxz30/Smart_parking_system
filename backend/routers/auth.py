from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, UserRole, UserStatus
from backend.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from backend.services.auth_service import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account with hashed password.
    Rejects duplicate email addresses.
    """
    existing_user = db.query(User).filter(User.email == user_in.email.strip().lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    new_user = User(
        name=user_in.name.strip(),
        email=user_in.email.strip().lower(),
        password=hash_password(user_in.password),
        phone=user_in.phone.strip() if user_in.phone else None,
        role=UserRole.USER,
        status=UserStatus.ACTIVE
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
def login_user(login_in: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user credentials, verify active status, and return JWT access token.
    """
    user = db.query(User).filter(User.email == login_in.email.strip().lower()).first()
    if not user or not verify_password(login_in.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from backend.services.auth_service import SEED_TEST_HASH
    if user.password == SEED_TEST_HASH:
        user.password = hash_password(login_in.password)
        db.commit()

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been deactivated"
        )

    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.user_id,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
