"""
Chat service for handling AI chatbot interactions
Integrates with LangChain, LangGraph, and LangSmith
"""
import uuid
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.core.config import settings
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class ChatService:
    """
    Chat service for processing AI chatbot messages
    Supports both Gemini and OpenAI through AIService
    """
    
    def __init__(self):
        self.conversations: Dict[str, List[Dict]] = {}
        self.ai_service = AIService()
        
        logger.info(f"ChatService initialized with provider: {self.ai_service.provider.value}")
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and generate AI response
        
        Args:
            user_id: User ID from Clerk
            message: User's message
            conversation_id: Optional conversation ID
            metadata: Optional metadata
            
        Returns:
            Dictionary with response and conversation ID
        """
        # Generate or use existing conversation ID
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Create conversation key
        conv_key = f"{user_id}:{conversation_id}"
        
        # Initialize conversation if needed
        if conv_key not in self.conversations:
            self.conversations[conv_key] = []
        
        # Add user message to conversation
        user_message = {
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.conversations[conv_key].append(user_message)
        
        # Get conversation history for context
        conversation_history = self.conversations[conv_key]
        
        # Generate AI response
        ai_result = await self.ai_service.generate_response(
            message=message,
            conversation_history=conversation_history
        )
        
        ai_response = ai_result["response"]
        
        # Add AI response to conversation
        assistant_message = {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.utcnow().isoformat(),
            "model": ai_result.get("model"),
            "tokens": ai_result.get("tokens")
        }
        self.conversations[conv_key].append(assistant_message)
        
        logger.info(f"Processed message for user {user_id}, conversation {conversation_id}, provider: {ai_result.get('provider')}")
        
        # Prepare response metadata
        response_metadata = metadata or {}
        response_metadata.update({
            "model": ai_result.get("model"),
            "provider": ai_result.get("provider"),
            "tokens": ai_result.get("tokens")
        })
        
        return {
            "response": ai_response,
            "conversation_id": conversation_id,
            "metadata": response_metadata
        }
    
    async def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user
        
        Args:
            user_id: User ID from Clerk
            
        Returns:
            List of conversation summaries
        """
        user_convs = []
        for conv_key, messages in self.conversations.items():
            if conv_key.startswith(f"{user_id}:"):
                conversation_id = conv_key.split(":", 1)[1]
                user_convs.append({
                    "conversation_id": conversation_id,
                    "message_count": len(messages),
                    "last_message": messages[-1] if messages else None
                })
        
        return user_convs
    
    async def get_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific conversation
        
        Args:
            user_id: User ID from Clerk
            conversation_id: Conversation ID
            
        Returns:
            Conversation data or None
        """
        conv_key = f"{user_id}:{conversation_id}"
        messages = self.conversations.get(conv_key)
        
        if not messages:
            return None
        
        return {
            "conversation_id": conversation_id,
            "messages": messages
        }
    
    async def delete_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> bool:
        """
        Delete a conversation
        
        Args:
            user_id: User ID from Clerk
            conversation_id: Conversation ID
            
        Returns:
            True if deleted, False if not found
        """
        conv_key = f"{user_id}:{conversation_id}"
        if conv_key in self.conversations:
            del self.conversations[conv_key]
            return True
        return False
