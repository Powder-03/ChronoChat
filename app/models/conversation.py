"""
MongoDB models for conversation and message storage
These are Pydantic models for MongoDB documents
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom type for MongoDB ObjectId"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class MessageDocument(BaseModel):
    """MongoDB document for a message"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    conversation_id: str
    role: str  # 'user', 'assistant', or 'system'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # AI metadata
    model: Optional[str] = None
    provider: Optional[str] = None
    tokens: Optional[int] = None
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ConversationDocument(BaseModel):
    """MongoDB document for a conversation"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    conversation_id: str  # UUID string for easy reference
    user_id: str  # Clerk user ID
    
    # Conversation details
    title: Optional[str] = None
    summary: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Stats
    message_count: int = 0
    total_tokens: int = 0
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None
    
    # Tags for organization
    tags: List[str] = []
    
    # Archived status
    is_archived: bool = False
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
