"""
Chat service for handling chat operations
"""
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.chat import ChatThread, ChatMessage, ToolCall
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, ChatThread as ChatThreadSchema, ChatMessage as ChatMessageSchema
from app.core.redis import redis_client
from app.core.config import settings


class ChatService:
    """Chat service class"""
    
    @staticmethod
    async def create_thread(db: AsyncSession, user: User, title: Optional[str] = None) -> ChatThread:
        """Create a new chat thread"""
        thread_id = str(uuid.uuid4())
        
        thread = ChatThread(
            id=thread_id,
            user_id=user.id,
            title=title or "New Chat"
        )
        
        db.add(thread)
        await db.commit()
        await db.refresh(thread)
        
        return thread
    
    @staticmethod
    async def get_user_threads(db: AsyncSession, user: User, limit: int = 50) -> List[ChatThread]:
        """Get user's chat threads"""
        result = await db.execute(
            select(ChatThread)
            .where(ChatThread.user_id == user.id)
            .order_by(ChatThread.updated_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_thread(db: AsyncSession, thread_id: str, user: User) -> Optional[ChatThread]:
        """Get a specific chat thread"""
        result = await db.execute(
            select(ChatThread)
            .where(ChatThread.id == thread_id, ChatThread.user_id == user.id)
            .options(selectinload(ChatThread.messages))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete_thread(db: AsyncSession, thread_id: str, user: User) -> bool:
        """Delete a chat thread"""
        result = await db.execute(
            select(ChatThread)
            .where(ChatThread.id == thread_id, ChatThread.user_id == user.id)
        )
        thread = result.scalar_one_or_none()
        
        if not thread:
            return False
        
        await db.delete(thread)
        await db.commit()
        
        # Remove from Redis
        redis = await redis_client.get_client()
        await redis.delete(f"chat_history:{thread_id}")
        
        return True
    
    @staticmethod
    async def add_message(
        db: AsyncSession, 
        thread: ChatThread, 
        role: str, 
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Add a message to a chat thread"""
        message = ChatMessage(
            thread_id=thread.id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            metadata=metadata
        )
        
        db.add(message)
        
        # Update thread timestamp
        thread.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(message)
        
        return message
    
    @staticmethod
    async def get_thread_messages(
        db: AsyncSession, 
        thread: ChatThread, 
        limit: int = 100
    ) -> List[ChatMessage]:
        """Get messages from a chat thread"""
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.thread_id == thread.id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def store_session_data(thread_id: str, messages: List[Dict[str, Any]]) -> None:
        """Store chat session data in Redis"""
        redis = await redis_client.get_client()
        await redis.setex(
            f"chat_history:{thread_id}",
            settings.SESSION_EXPIRE_HOURS * 3600,
            json.dumps(messages, default=str)
        )
    
    @staticmethod
    async def get_session_data(thread_id: str) -> List[Dict[str, Any]]:
        """Get chat session data from Redis"""
        redis = await redis_client.get_client()
        data = await redis.get(f"chat_history:{thread_id}")
        
        if data:
            return json.loads(data)
        return []
    
    @staticmethod
    async def update_thread_title(db: AsyncSession, thread: ChatThread, title: str) -> ChatThread:
        """Update thread title"""
        thread.title = title
        thread.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(thread)
        return thread
    
    @staticmethod
    async def log_tool_call(
        db: AsyncSession,
        message: ChatMessage,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Optional[Dict[str, Any]] = None,
        execution_time: Optional[int] = None,
        success: str = "pending",
        error_message: Optional[str] = None
    ) -> ToolCall:
        """Log a tool call"""
        tool_call = ToolCall(
            message_id=message.id,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
            execution_time=execution_time,
            success=success,
            error_message=error_message
        )
        
        db.add(tool_call)
        await db.commit()
        await db.refresh(tool_call)
        
        return tool_call
    
    @staticmethod
    async def get_user_stats(db: AsyncSession, user: User) -> Dict[str, Any]:
        """Get user chat statistics"""
        # Count threads
        thread_result = await db.execute(
            select(ChatThread).where(ChatThread.user_id == user.id)
        )
        thread_count = len(thread_result.scalars().all())
        
        # Count messages
        message_result = await db.execute(
            select(ChatMessage)
            .join(ChatThread)
            .where(ChatThread.user_id == user.id)
        )
        message_count = len(message_result.scalars().all())
        
        # Count tool calls
        tool_result = await db.execute(
            select(ToolCall)
            .join(ChatMessage)
            .join(ChatThread)
            .where(ChatThread.user_id == user.id)
        )
        tool_count = len(tool_result.scalars().all())
        
        return {
            "total_threads": thread_count,
            "total_messages": message_count,
            "total_tool_calls": tool_count,
            "user_since": user.created_at
        }


# Create chat service instance
chat_service = ChatService()
