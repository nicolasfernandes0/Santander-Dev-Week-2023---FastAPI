"""
Rotas de autenticação
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user
)

router = APIRouter()

# Modelos Pydantic
class Token(BaseModel):
    access_token: str
    token_type: str

class UserRegister(BaseModel):
    email: str
    password: str
    name: str

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register_user(user: UserRegister, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    
    return {
        "message": "User registered successfully",
        "email": user.email,
        "name": user.name
    }

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    return current_user

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_active_user)):
    return {
        "message": "You have accessed a protected route!",
        "user": current_user
    }