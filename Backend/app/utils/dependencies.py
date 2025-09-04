"""
Utility functions and dependencies
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import security
from app.services.auth import auth_service
from app.models.user import User


async def get_current_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = authorization.split(" ")[1]
    
    try:
        payload = security.verify_token(token, "access")
        username = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user = await auth_service.get_user_by_username(db, username)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_optional_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get current user if authenticated, None otherwise
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        return await get_current_user(authorization, db)
    except HTTPException:
        return None


def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Get user agent from request"""
    return request.headers.get("User-Agent", "unknown")
