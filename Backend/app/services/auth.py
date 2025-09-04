"""
Authentication service for user management
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import HTTPException, status
import uuid

from app.models.user import User, UserSession
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.core.security import security
from app.core.config import settings
from app.core.redis import redis_client


class AuthService:
    """Authentication service class"""
    
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        
        # Check if username exists
        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = security.get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return UserResponse.from_orm(db_user)
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, login_data: UserLogin) -> Optional[User]:
        """Authenticate user login"""
        
        # Get user by username
        result = await db.execute(select(User).where(User.username == login_data.username))
        user = result.scalar_one_or_none()
        
        if not user or not security.verify_password(login_data.password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )
        
        # Update last login
        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(last_login=datetime.utcnow())
        )
        await db.commit()
        
        return user
    
    @staticmethod
    async def create_user_session(
        db: AsyncSession, 
        user: User, 
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        remember_me: bool = False
    ) -> Token:
        """Create user session and return tokens"""
        
        # Clean up old sessions if user has too many
        result = await db.execute(
            select(UserSession)
            .where(UserSession.user_id == user.id, UserSession.is_active == True)
            .order_by(UserSession.created_at.desc())
        )
        active_sessions = result.scalars().all()
        
        if len(active_sessions) >= settings.MAX_SESSIONS_PER_USER:
            # Deactivate oldest sessions
            oldest_sessions = active_sessions[settings.MAX_SESSIONS_PER_USER-1:]
            for session in oldest_sessions:
                session.is_active = False
        
        # Create tokens
        token_data = {"sub": user.username, "user_id": user.id}
        
        if remember_me:
            expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        else:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        access_token = security.create_access_token(token_data, expires_delta)
        refresh_token = security.create_refresh_token(token_data)
        
        # Create session record
        session_token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + expires_delta
        
        db_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(db_session)
        await db.commit()
        
        # Store session in Redis
        redis = await redis_client.get_client()
        await redis.setex(
            f"session:{session_token}",
            int(expires_delta.total_seconds()),
            user.username
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(expires_delta.total_seconds())
        )
    
    @staticmethod
    async def refresh_token(db: AsyncSession, refresh_token: str) -> Token:
        """Refresh access token"""
        
        # Verify refresh token
        try:
            payload = security.verify_token(refresh_token, "refresh")
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user session
        result = await db.execute(
            select(UserSession)
            .where(UserSession.refresh_token == refresh_token, UserSession.is_active == True)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        result = await db.execute(select(User).where(User.id == session.user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        token_data = {"sub": user.username, "user_id": user.id}
        new_access_token = security.create_access_token(token_data)
        new_refresh_token = security.create_refresh_token(token_data)
        
        # Update session
        session.refresh_token = new_refresh_token
        session.last_activity = datetime.utcnow()
        await db.commit()
        
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    @staticmethod
    async def logout_user(db: AsyncSession, session_token: str) -> bool:
        """Logout user by deactivating session"""
        
        # Deactivate session in database
        await db.execute(
            update(UserSession)
            .where(UserSession.session_token == session_token)
            .values(is_active=False)
        )
        await db.commit()
        
        # Remove session from Redis
        redis = await redis_client.get_client()
        await redis.delete(f"session:{session_token}")
        
        return True
    
    @staticmethod
    async def logout_all_sessions(db: AsyncSession, user_id: int) -> bool:
        """Logout user from all sessions"""
        
        # Get all active sessions
        result = await db.execute(
            select(UserSession)
            .where(UserSession.user_id == user_id, UserSession.is_active == True)
        )
        sessions = result.scalars().all()
        
        # Deactivate all sessions
        await db.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id, UserSession.is_active == True)
            .values(is_active=False)
        )
        await db.commit()
        
        # Remove sessions from Redis
        redis = await redis_client.get_client()
        for session in sessions:
            await redis.delete(f"session:{session.session_token}")
        
        return True
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def verify_session(db: AsyncSession, session_token: str) -> Optional[User]:
        """Verify user session"""
        
        # Check Redis first
        redis = await redis_client.get_client()
        username = await redis.get(f"session:{session_token}")
        
        if not username:
            return None
        
        # Get user from database
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
        
        # Update last activity in session
        await db.execute(
            update(UserSession)
            .where(UserSession.session_token == session_token)
            .values(last_activity=datetime.utcnow())
        )
        await db.commit()
        
        return user


# Create auth service instance
auth_service = AuthService()
