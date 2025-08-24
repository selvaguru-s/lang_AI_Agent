import secrets
import string
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.firebase import firebase_config
from config.database import get_database
from models.user import User


security = HTTPBearer()


def generate_api_key(length: int = 32) -> str:
    """Generate a secure random API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


async def verify_firebase_token(token: str) -> Optional[dict]:
    """Verify Firebase ID token"""
    return await firebase_config.verify_token(token)


async def get_or_create_user(firebase_user: dict) -> User:
    """Get existing user or create new user with API key"""
    db = await get_database()
    
    # Check if user exists
    existing_user = await db.users.find_one({"firebase_uid": firebase_user["uid"]})
    
    if existing_user:
        # Update last login
        await db.users.update_one(
            {"firebase_uid": firebase_user["uid"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        return User(**existing_user)
    
    # Create new user with API key
    api_key = generate_api_key()
    new_user = User(
        firebase_uid=firebase_user["uid"],
        email=firebase_user["email"],
        name=firebase_user["name"],
        api_key=api_key
    )
    
    await db.users.insert_one(new_user.dict(by_alias=True))
    return new_user


async def verify_api_key(api_key: str) -> Optional[User]:
    """Verify API key and return user"""
    db = await get_database()
    user_data = await db.users.find_one({"api_key": api_key, "is_active": True})
    
    if user_data:
        return User(**user_data)
    return None


async def get_current_user_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Dependency to get current user from API key (for client connections)"""
    api_key = credentials.credentials
    user = await verify_api_key(api_key)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_firebase(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Dependency to get current user from Firebase ID token (for frontend)"""
    firebase_token = credentials.credentials
    firebase_user = await verify_firebase_token(firebase_token)
    
    if not firebase_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database by firebase_uid
    db = await get_database()
    user_data = await db.users.find_one({"firebase_uid": firebase_user["uid"], "is_active": True})
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(**user_data)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Flexible dependency that tries both Firebase and API key authentication"""
    token = credentials.credentials
    
    # Try Firebase authentication first
    firebase_user = await verify_firebase_token(token)
    if firebase_user:
        db = await get_database()
        user_data = await db.users.find_one({"firebase_uid": firebase_user["uid"], "is_active": True})
        if user_data:
            return User(**user_data)
    
    # Try API key authentication
    user = await verify_api_key(token)
    if user:
        return user
    
    # Neither worked
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )