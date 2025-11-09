"""
PostgreSQL models for user data and analytics
Uses SQLAlchemy with async support
"""
from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.core.database import Base


class User(Base):
    """User model for PostgreSQL - stores Clerk user data and app-specific info"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_user_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)
    
    # Subscription & Usage
    subscription_tier = Column(String, default="free")  # free, pro, enterprise
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Metadata
    metadata = Column(JSONB, nullable=True)
    
    def __repr__(self):
        return f"<User(clerk_id={self.clerk_user_id}, email={self.email})>"


class UserUsageStats(Base):
    """Track user usage statistics"""
    __tablename__ = "user_usage_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_user_id = Column(String, nullable=False, index=True)
    
    # Usage metrics
    total_messages = Column(Integer, default=0)
    total_conversations = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    
    # Monthly metrics (reset monthly)
    monthly_messages = Column(Integer, default=0)
    monthly_tokens = Column(Integer, default=0)
    month_year = Column(String, nullable=False)  # Format: "2025-11"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserUsageStats(user={self.clerk_user_id}, messages={self.total_messages})>"


class UserSession(Base):
    """Track user sessions for analytics"""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, unique=True, index=True)
    
    # Session info
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    device_type = Column(String, nullable=True)  # desktop, mobile, tablet
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    # Session metadata
    metadata = Column(JSONB, nullable=True)
    
    def __repr__(self):
        return f"<UserSession(user={self.clerk_user_id}, session={self.session_id})>"


class APILog(Base):
    """Log API requests for monitoring and analytics"""
    __tablename__ = "api_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_user_id = Column(String, nullable=True, index=True)
    
    # Request info
    endpoint = Column(String, nullable=False, index=True)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    
    # Timing
    response_time_ms = Column(Float, nullable=True)
    
    # Metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<APILog(endpoint={self.endpoint}, status={self.status_code})>"


class UserPreferences(Base):
    """Store user preferences and settings"""
    __tablename__ = "user_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_user_id = Column(String, unique=True, nullable=False, index=True)
    
    # AI Preferences
    preferred_ai_provider = Column(String, default="gemini")  # gemini, openai
    preferred_model = Column(String, nullable=True)
    temperature = Column(Float, default=0.7)
    
    # Chat Preferences
    chat_theme = Column(String, default="light")  # light, dark
    language = Column(String, default="en")
    
    # Notification Preferences
    email_notifications = Column(Boolean, default=True)
    
    # Other preferences stored as JSON
    preferences = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserPreferences(user={self.clerk_user_id})>"
