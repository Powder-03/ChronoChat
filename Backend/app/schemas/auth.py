"""
Authentication schemas/models for request/response validation
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('password must contain at least one digit')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('username must be at least 3 characters long')
        if not v.isalnum():
            raise ValueError('username must contain only alphanumeric characters')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str
    remember_me: Optional[bool] = False


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh schema"""
    refresh_token: str


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str
    confirm_new_password: str
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')
        return v


class PasswordReset(BaseModel):
    """Password reset schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')
        return v


class LogoutResponse(BaseModel):
    """Logout response schema"""
    message: str
    logged_out_at: datetime
