"""
Endpoints para autenticación y autorización.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..core.auth import authenticate_user, create_access_token, users_db, TokenData
from datetime import timedelta
from typing import Optional

router = APIRouter()

class Token(BaseModel):
    """Modelo para el token de acceso."""
    access_token: str
    token_type: str

class TokenRequest(BaseModel):
    """Modelo para la solicitud de token."""
    username: str
    password: str

class UserResponse(BaseModel):
    """Modelo para la respuesta de usuario."""
    username: str
    disabled: bool

@router.post("/token", response_model=Token)
async def login_for_access_token(request: TokenRequest):
    """
    Inicia sesión y devuelve un token de acceso.
    
    - **request**: Credenciales de usuario
    """
    user = authenticate_user(users_db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(TokenData)):
    """
    Obtiene información del usuario actual.
    
    - **current_user**: Usuario actual
    """
    return current_user