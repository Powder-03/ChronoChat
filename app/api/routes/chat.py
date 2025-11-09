"""
Chat endpoints for AI chatbot functionality
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging

from app.core.clerk import get_current_user
from app.services.chat_service import ChatService
from app.schemas.chat import (
    ChatMessage, 
    ChatResponse, 
    ConversationListResponse,
    ConversationDetailSchema
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize chat service
chat_service = ChatService()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_message: ChatMessage,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a message to the AI chatbot
    
    Requires: Bearer token in Authorization header
    """
    try:
        logger.info(f"User {current_user['user_id']} sent message")
        
        # Process message with chat service
        response = await chat_service.process_message(
            user_id=current_user["user_id"],
            message=chat_message.message,
            conversation_id=chat_message.conversation_id,
            metadata=chat_message.metadata
        )
        
        return response
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing your message"
        )


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user's conversation history
    
    Requires: Bearer token in Authorization header
    """
    try:
        conversations = await chat_service.get_user_conversations(
            user_id=current_user["user_id"]
        )
        return {
            "conversations": conversations,
            "total": len(conversations)
        }
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching conversations"
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailSchema)
async def get_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get specific conversation details
    
    Requires: Bearer token in Authorization header
    """
    try:
        conversation = await chat_service.get_conversation(
            user_id=current_user["user_id"],
            conversation_id=conversation_id
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching conversation"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a conversation
    
    Requires: Bearer token in Authorization header
    """
    try:
        await chat_service.delete_conversation(
            user_id=current_user["user_id"],
            conversation_id=conversation_id
        )
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting conversation"
        )


@router.get("/search")
async def search_conversations(
    q: str,
    limit: int = 20,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Search conversations by title or content
    
    Requires: Bearer token in Authorization header
    """
    try:
        results = await chat_service.search_conversations(
            user_id=current_user["user_id"],
            query=q,
            limit=limit
        )
        return {"results": results, "total": len(results)}
    except Exception as e:
        logger.error(f"Error searching conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching conversations"
        )
