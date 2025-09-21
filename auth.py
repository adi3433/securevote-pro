"""
SecureVote Pro - Authentication System
JWT-based authentication with role-based access control
"""

import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import Config

# Security configuration
SECRET_KEY = Config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Predefined users (in production, use database)
USERS_DB = {
    "admin": {
        "username": "admin",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "full_name": "System Administrator"
    },
    "election_officer": {
        "username": "election_officer", 
        "password_hash": hashlib.sha256("officer123".encode()).hexdigest(),
        "role": "admin",
        "full_name": "Election Officer"
    },
    "voter": {
        "username": "voter",
        "password_hash": hashlib.sha256("voter123".encode()).hexdigest(), 
        "role": "voter",
        "full_name": "Registered Voter"
    }
}

security = HTTPBearer()

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict]:
        """Authenticate user credentials."""
        user = USERS_DB.get(username)
        if not user:
            return None
        if not AuthService.verify_password(password, user["password_hash"]):
            return None
        return user
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials", 
                headers={"WWW-Authenticate": "Bearer"},
            )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    username = payload.get("sub")
    user = USERS_DB.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def require_admin(current_user: dict = Depends(get_current_user)):
    """Require admin role for access."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_voter(current_user: dict = Depends(get_current_user)):
    """Require voter role for access."""
    if current_user.get("role") != "voter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Voter access required"
        )
    return current_user
