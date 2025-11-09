"""
Chat service for handling AI chatbot interactions
Integrates with LangChain, LangGraph, and LangSmith
Uses MongoDB for conversation storage
"""
from typing import Dict, Any, List, Optional
import logging

from app.services.ai_service import AIService
from app.services.chat_agent import ChatAgent
from app.repositories.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class ChatService:
    """
    Chat service for processing AI chatbot messages
    Uses LangGraph for agent workflow and MongoDB for storage
    """
    
    def __init__(self):
        self.ai_service = AIService()
        self.chat_agent = ChatAgent(self.ai_service)
        self.conversation_repo = ConversationRepository()
        
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
        try:
            # Create new conversation if needed
            if not conversation_id:
                conversation_id = await self.conversation_repo.create_conversation(
                    user_id=user_id,
                    metadata=metadata
                )
            
            # Get existing messages for context
            existing_messages = await self.conversation_repo.get_conversation_messages(
                conversation_id=conversation_id
            )
            
            # Save user message to MongoDB
            await self.conversation_repo.add_message(
                conversation_id=conversation_id,
                role="user",
                content=message,
                metadata=metadata
            )
            
            # Process message through LangGraph agent
            agent_result = await self.chat_agent.process_message(
                user_id=user_id,
                conversation_id=conversation_id,
                message=message,
                existing_messages=existing_messages,
                metadata=metadata
            )
            
            ai_response = agent_result["response"]
            response_metadata = agent_result["metadata"]
            
            # Save AI response to MongoDB
            await self.conversation_repo.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=ai_response,
                model=response_metadata.get("model"),
                provider=response_metadata.get("provider"),
                tokens=response_metadata.get("tokens"),
                metadata=response_metadata
            )
            
            # Update conversation title if it's the first exchange
            if len(existing_messages) == 0:
                title = self.chat_agent.get_conversation_summary([{"content": message}])
                await self.conversation_repo.update_conversation(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    update_data={"title": title}
                )
            
            logger.info(f"Processed message for user {user_id}, conversation {conversation_id}")
            
            return {
                "response": ai_response,
                "conversation_id": conversation_id,
                "metadata": response_metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise
    
    async def get_user_conversations(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user
        
        Args:
            user_id: User ID from Clerk
            skip: Number of conversations to skip
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation summaries
        """
        try:
            conversations = await self.conversation_repo.get_user_conversations(
                user_id=user_id,
                skip=skip,
                limit=limit
            )
            return conversations
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            raise
    
    async def get_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific conversation with messages
        
        Args:
            user_id: User ID from Clerk
            conversation_id: Conversation ID
            
        Returns:
            Conversation data with messages or None
        """
        try:
            result = await self.conversation_repo.get_conversation(
                user_id=user_id,
                conversation_id=conversation_id
            )
            return result
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            raise
    
    async def delete_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> bool:
        """
        Delete a conversation and all its messages
        
        Args:
            user_id: User ID from Clerk
            conversation_id: Conversation ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            result = await self.conversation_repo.delete_conversation(
                user_id=user_id,
                conversation_id=conversation_id
            )
            return result
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            raise
    
    async def search_conversations(
        self,
        user_id: str,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search user's conversations
        
        Args:
            user_id: User ID from Clerk
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching conversations
        """
        try:
            results = await self.conversation_repo.search_conversations(
                user_id=user_id,
                query=query,
                limit=limit
            )
            return results
        except Exception as e:
            logger.error(f"Error searching conversations: {str(e)}")
            raise
