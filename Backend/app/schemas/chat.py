"""
Chat schemas/models for request/response validation
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatMessageBase(BaseModel):
    """Base chat message schema"""
    role: str
    content: str


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating chat message"""
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatMessage(ChatMessageBase):
    """Schema for chat message response"""
    id: int
    thread_id: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for chat request"""
    message: str
    thread_id: Optional[str] = None
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    """Schema for chat response"""
    response: str
    thread_id: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    message_id: int


class ChatThreadBase(BaseModel):
    """Base chat thread schema"""
    title: str


class ChatThreadCreate(ChatThreadBase):
    """Schema for creating chat thread"""
    pass


class ChatThread(ChatThreadBase):
    """Schema for chat thread response"""
    id: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatThreadWithMessages(ChatThread):
    """Schema for chat thread with messages"""
    messages: List[ChatMessage]


class ChatHistory(BaseModel):
    """Schema for chat history response"""
    thread: ChatThread
    messages: List[ChatMessage]
    total_messages: int


class ToolCallBase(BaseModel):
    """Base tool call schema"""
    tool_name: str
    tool_input: Dict[str, Any]


class ToolCall(ToolCallBase):
    """Schema for tool call response"""
    id: int
    message_id: int
    tool_output: Optional[Dict[str, Any]] = None
    execution_time: Optional[int] = None
    success: str
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ToolInfo(BaseModel):
    """Schema for tool information"""
    name: str
    description: str
    parameters: Dict[str, Any]


class AvailableTools(BaseModel):
    """Schema for available tools response"""
    tools: List[ToolInfo]
    total_tools: int
