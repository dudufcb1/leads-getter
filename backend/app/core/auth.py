"""
Módulo de autenticación y autorización para la API.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de seguridad HTTP Bearer
security = HTTPBearer()

class TokenData:
    """Datos del token de autenticación."""
    def __init__(self, username: Optional[str] = None):
        self.username = username

class User:
    """Modelo de usuario."""
    def __init__(self, username: str, hashed_password: str, disabled: bool = False):
        self.username = username
        self.hashed_password = hashed_password
        self.disabled = disabled

# Usuarios de ejemplo (en producción, esto debería estar en una base de datos)
users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PZvO.S",  # "adminpassword"
        "disabled": False,
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña plana coincide con su hash.
    
    - **plain_password**: Contraseña en texto plano
    - **hashed_password**: Contraseña hasheada
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña.
    
    - **password**: Contraseña en texto plano
    """
    return pwd_context.hash(password)

def get_user(db: dict, username: str) -> Optional[User]:
    """
    Obtiene un usuario de la base de datos.
    
    - **db**: Base de datos de usuarios
    - **username**: Nombre de usuario
    """
    if username in db:
        user_dict = db[username]
        return User(**user_dict)
    return None

def authenticate_user(db: dict, username: str, password: str) -> Optional[User]:
    """
    Autentica un usuario.
    
    - **db**: Base de datos de usuarios
    - **username**: Nombre de usuario
    - **password**: Contraseña
    """
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token de acceso JWT.
    
    - **data**: Datos a incluir en el token
    - **expires_delta**: Tiempo de expiración del token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Obtiene el usuario actual a partir del token de autorización.
    
    - **credentials**: Credenciales de autorización
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Obtiene el usuario actual si está activo.
    
    - **current_user**: Usuario actual
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def is_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Verifica si el usuario actual es administrador.
    
    - **current_user**: Usuario actual
    """
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user