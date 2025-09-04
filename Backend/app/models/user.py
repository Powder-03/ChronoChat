"""
User model definitions
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    chat_threads = relationship("ChatThread", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class UserSession(Base):
    """User session model for tracking active sessions"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    refresh_token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"
