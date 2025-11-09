"""
Pydantic schemas for authentication-related requests and responses
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any


class UserResponse(BaseModel):
    """User response schema"""
    user_id: str = Field(..., description="Clerk user ID")
    email: Optional[EmailStr] = Field(None, description="User email")
    user_info: Optional[Dict[str, Any]] = Field(None, description="Additional user information from Clerk")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_2abc123xyz",
                "email": "user@example.com",
                "user_info": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "image_url": "https://..."
                }
            }
        }


class TokenVerifyResponse(BaseModel):
    """Token verification response schema"""
    valid: bool = Field(..., description="Whether the token is valid")
    user_id: str = Field(..., description="User ID from token")
    email: Optional[EmailStr] = Field(None, description="User email")
    
    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "user_id": "user_2abc123xyz",
                "email": "user@example.com"
            }
        }


class SessionVerifyResponse(BaseModel):
    """Session verification response schema"""
    valid: bool = Field(..., description="Whether the session is valid")
    session: Dict[str, Any] = Field(..., description="Session information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "session": {
                    "id": "sess_123",
                    "user_id": "user_2abc123xyz",
                    "status": "active"
                }
            }
        }
