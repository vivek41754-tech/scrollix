from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    oauth2_scheme
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: str = "customer"  # customer, merchant, admin

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user

def require_current_user(user: Optional[User] = Depends(get_current_user)) -> User:
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    return user

def require_role(allowed_roles: list[str]):
    def role_checker(user: User = Depends(require_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions.")
        return user
    return role_checker

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter((User.email == req.email) | (User.username == req.username)).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already registered.")
    
    user = User(
        email=req.email,
        username=req.username,
        hashed_password=get_password_hash(req.password),
        role=req.role if req.role in ["customer", "merchant", "admin"] else "customer",
        avatar_url="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "avatar_url": user.avatar_url
        }
    }

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == req.username_or_email) | (User.email == req.username_or_email)
    ).first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "merchant_id": user.merchant.id if user.merchant else None
        }
    }

@router.get("/me")
def get_me(user: User = Depends(require_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "avatar_url": user.avatar_url,
        "merchant_id": user.merchant.id if user.merchant else None,
        "preferences": user.get_preferences()
    }

class DemoSwitchRequest(BaseModel):
    role: str  # customer, merchant, admin

@router.post("/demo-switch", response_model=TokenResponse)
def demo_switch_role(req: DemoSwitchRequest, request: Request, db: Session = Depends(get_db)):
    """
    Dedicated local demonstration endpoint: issues an authentic JWT token and user context
    for the selected demo role (customer, merchant, admin) with zero password or credential prompts.
    Scoped strictly to local client hosts to prevent remote administrative privilege escalation.
    """
    # Security guardrail: remote IP clients cannot use demo-switch
    client_host = request.client.host if request.client else "127.0.0.1"
    if client_host not in ["127.0.0.1", "::1", "localhost", "testclient"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo role switching is restricted to local demonstration instances."
        )

    role_key = req.role.lower().strip()
    if role_key in ["customer", "shopper"]:
        target_username = "alex_shopper"
        expected_role = "customer"
    elif role_key == "merchant":
        target_username = "pulse_kicks"
        expected_role = "merchant"
    elif role_key == "admin":
        target_username = "admin"
        expected_role = "admin"
    else:
        raise HTTPException(status_code=400, detail=f"Invalid demo role '{req.role}'. Choose customer, merchant, or admin.")

    user = db.query(User).filter(User.username == target_username).first()
    if not user:
        # Fallback to any user with matching role
        user = db.query(User).filter(User.role == expected_role).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"No demonstration user found for role '{expected_role}'.")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "merchant_id": user.merchant.id if user.merchant else None
        }
    }

