"""
Pydantic schemas for chat-related requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ChatMessage(BaseModel):
    """Chat message request schema"""
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for continuing a chat")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is the capital of France?",
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "metadata": {"source": "web"}
            }
        }


class ChatResponse(BaseModel):
    """Chat response schema"""
    response: str = Field(..., description="AI assistant response")
    conversation_id: str = Field(..., description="Conversation ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Response metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "The capital of France is Paris.",
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "metadata": {"model": "gemini-2.0-flash-exp", "tokens": 150}
            }
        }


class MessageSchema(BaseModel):
    """Message schema for conversation history"""
    id: str
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    created_at: datetime
    token_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class ConversationSchema(BaseModel):
    """Conversation schema"""
    conversation_id: str
    user_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message: Optional[MessageSchema] = None
    
    class Config:
        from_attributes = True


class ConversationDetailSchema(BaseModel):
    """Detailed conversation schema with messages"""
    conversation_id: str
    user_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageSchema] = []
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Response schema for conversation list"""
    conversations: List[ConversationSchema]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversations": [
                    {
                        "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "user_123",
                        "title": "Python Programming Help",
                        "created_at": "2025-11-09T10:00:00",
                        "updated_at": "2025-11-09T10:30:00",
                        "message_count": 5,
                        "last_message": {
                            "id": "msg_123",
                            "role": "assistant",
                            "content": "I can help you with that!",
                            "created_at": "2025-11-09T10:30:00"
                        }
                    }
                ],
                "total": 1
            }
        }
