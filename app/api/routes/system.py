"""
System and configuration endpoints
"""
from fastapi import APIRouter
from typing import Dict, Any

from app.services.chat_service import ChatService

router = APIRouter()

# Initialize chat service to access AI service
chat_service = ChatService()


@router.get("/ai-provider")
async def get_ai_provider() -> Dict[str, Any]:
    """
    Get current AI provider information
    
    Returns information about which AI provider is currently active
    """
    return chat_service.ai_service.get_provider_info()
