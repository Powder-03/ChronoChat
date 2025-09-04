"""
Chat model definitions
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ChatThread(Base):
    """Chat thread model"""
    __tablename__ = "chat_threads"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), default="New Chat")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_threads")
    messages = relationship("ChatMessage", back_populates="thread", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatThread(id='{self.id}', title='{self.title}')>"


class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(36), ForeignKey("chat_threads.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)  # Store tool call information
    metadata = Column(JSON, nullable=True)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    thread = relationship("ChatThread", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role='{self.role}', thread_id='{self.thread_id}')>"


class ToolCall(Base):
    """Tool call model for tracking tool usage"""
    __tablename__ = "tool_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    tool_input = Column(JSON, nullable=False)
    tool_output = Column(JSON, nullable=True)
    execution_time = Column(Integer, nullable=True)  # milliseconds
    success = Column(String(10), default="pending")  # 'pending', 'success', 'error'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ToolCall(id={self.id}, tool_name='{self.tool_name}', status='{self.success}')>"
