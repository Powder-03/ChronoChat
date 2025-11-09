"""
MongoDB repository for conversation and message operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from app.core.database import get_mongodb
from app.models.conversation import ConversationDocument, MessageDocument

logger = logging.getLogger(__name__)


class ConversationRepository:
    """Repository for conversation operations in MongoDB"""
    
    def __init__(self):
        self.db = get_mongodb()
        self.conversations = self.db.conversations
        self.messages = self.db.messages
    
    async def create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new conversation"""
        try:
            conversation_id = str(uuid.uuid4())
            conversation_doc = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "title": title,
                "summary": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "message_count": 0,
                "total_tokens": 0,
                "metadata": metadata or {},
                "tags": [],
                "is_archived": False
            }
            
            await self.conversations.insert_one(conversation_doc)
            logger.info(f"Created conversation {conversation_id} for user {user_id}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise
    
    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a message to a conversation"""
        try:
            message_doc = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "created_at": datetime.utcnow(),
                "model": model,
                "provider": provider,
                "tokens": tokens,
                "metadata": metadata or {}
            }
            
            result = await self.messages.insert_one(message_doc)
            
            # Update conversation stats
            update_data = {
                "$set": {"updated_at": datetime.utcnow()},
                "$inc": {"message_count": 1}
            }
            if tokens:
                update_data["$inc"]["total_tokens"] = tokens
            
            await self.conversations.update_one(
                {"conversation_id": conversation_id},
                update_data
            )
            
            logger.info(f"Added message to conversation {conversation_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            raise
    
    async def get_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a conversation with its messages"""
        try:
            # Get conversation
            conversation = await self.conversations.find_one({
                "conversation_id": conversation_id,
                "user_id": user_id
            })
            
            if not conversation:
                return None
            
            # Get messages
            messages_cursor = self.messages.find(
                {"conversation_id": conversation_id}
            ).sort("created_at", 1)
            
            messages = await messages_cursor.to_list(length=None)
            
            # Convert ObjectId to string for JSON serialization
            conversation["_id"] = str(conversation["_id"])
            for msg in messages:
                msg["_id"] = str(msg["_id"])
            
            return {
                "conversation": conversation,
                "messages": messages
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            raise
    
    async def get_user_conversations(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all conversations for a user"""
        try:
            query = {"user_id": user_id}
            if not include_archived:
                query["is_archived"] = False
            
            conversations_cursor = self.conversations.find(query).sort(
                "updated_at", -1
            ).skip(skip).limit(limit)
            
            conversations = await conversations_cursor.to_list(length=limit)
            
            # Get last message for each conversation
            for conv in conversations:
                conv["_id"] = str(conv["_id"])
                
                last_message = await self.messages.find_one(
                    {"conversation_id": conv["conversation_id"]},
                    sort=[("created_at", -1)]
                )
                
                if last_message:
                    last_message["_id"] = str(last_message["_id"])
                    conv["last_message"] = last_message
                else:
                    conv["last_message"] = None
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            raise
    
    async def get_conversation_messages(
        self,
        conversation_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get messages for a conversation"""
        try:
            messages_cursor = self.messages.find(
                {"conversation_id": conversation_id}
            ).sort("created_at", 1).skip(skip).limit(limit)
            
            messages = await messages_cursor.to_list(length=limit)
            
            for msg in messages:
                msg["_id"] = str(msg["_id"])
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting conversation messages: {str(e)}")
            raise
    
    async def update_conversation(
        self,
        user_id: str,
        conversation_id: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """Update a conversation"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.conversations.update_one(
                {"conversation_id": conversation_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating conversation: {str(e)}")
            raise
    
    async def delete_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> bool:
        """Delete a conversation and its messages"""
        try:
            # Delete messages
            await self.messages.delete_many({"conversation_id": conversation_id})
            
            # Delete conversation
            result = await self.conversations.delete_one({
                "conversation_id": conversation_id,
                "user_id": user_id
            })
            
            logger.info(f"Deleted conversation {conversation_id}")
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            raise
    
    async def archive_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> bool:
        """Archive a conversation"""
        return await self.update_conversation(
            user_id,
            conversation_id,
            {"is_archived": True}
        )
    
    async def search_conversations(
        self,
        user_id: str,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search conversations by title or content"""
        try:
            # Search in conversation titles
            conversations = await self.conversations.find({
                "user_id": user_id,
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"summary": {"$regex": query, "$options": "i"}}
                ]
            }).sort("updated_at", -1).limit(limit).to_list(length=limit)
            
            for conv in conversations:
                conv["_id"] = str(conv["_id"])
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error searching conversations: {str(e)}")
            raise
