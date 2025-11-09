"""
AI Service for handling different AI providers (Gemini, OpenAI)
"""
import os
import logging
from typing import Optional, Dict, Any
from enum import Enum

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """AI Provider options"""
    GEMINI = "gemini"
    OPENAI = "openai"


class AIService:
    """
    AI Service to manage different AI providers
    Supports Google Gemini and OpenAI
    """
    
    def __init__(self):
        self.provider = AIProvider(settings.AI_PROVIDER.lower())
        self.model = None
        self.chain = None
        
        # Setup LangSmith tracing if configured
        if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
            os.environ["LANGCHAIN_TRACING_V2"] = str(settings.LANGCHAIN_TRACING_V2)
            os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
            os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
            logger.info("LangSmith tracing enabled")
        
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the selected AI provider"""
        try:
            if self.provider == AIProvider.GEMINI:
                self._initialize_gemini()
            elif self.provider == AIProvider.OPENAI:
                self._initialize_openai()
            else:
                raise ValueError(f"Unsupported AI provider: {self.provider}")
        except Exception as e:
            logger.error(f"Error initializing AI provider: {str(e)}")
            # Fall back to placeholder mode
            logger.warning("Running in placeholder mode without AI")
    
    def _initialize_gemini(self):
        """Initialize Google Gemini"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain.chains import ConversationChain
            from langchain.memory import ConversationBufferMemory
            
            if not settings.GOOGLE_API_KEY:
                logger.warning("GOOGLE_API_KEY not set, AI features will be limited")
                return
            
            self.model = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.7,
                convert_system_message_to_human=True
            )
            
            self.memory = ConversationBufferMemory()
            self.chain = ConversationChain(
                llm=self.model,
                memory=self.memory,
                verbose=True if settings.DEBUG else False
            )
            
            logger.info(f"Initialized Gemini with model: {settings.GEMINI_MODEL}")
            
        except ImportError as e:
            logger.error(f"Failed to import Gemini dependencies: {str(e)}")
            logger.warning("Install with: pip install langchain-google-genai google-generativeai")
        except Exception as e:
            logger.error(f"Error initializing Gemini: {str(e)}")
    
    def _initialize_openai(self):
        """Initialize OpenAI"""
        try:
            from langchain_openai import ChatOpenAI
            from langchain.chains import ConversationChain
            from langchain.memory import ConversationBufferMemory
            
            if not settings.OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY not set, AI features will be limited")
                return
            
            self.model = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=0.7
            )
            
            self.memory = ConversationBufferMemory()
            self.chain = ConversationChain(
                llm=self.model,
                memory=self.memory,
                verbose=True if settings.DEBUG else False
            )
            
            logger.info(f"Initialized OpenAI with model: {settings.OPENAI_MODEL}")
            
        except ImportError as e:
            logger.error(f"Failed to import OpenAI dependencies: {str(e)}")
            logger.warning("Install with: pip install langchain-openai")
        except Exception as e:
            logger.error(f"Error initializing OpenAI: {str(e)}")
    
    async def generate_response(
        self,
        message: str,
        conversation_history: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response
        
        Args:
            message: User message
            conversation_history: Optional conversation history
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            if self.chain is None:
                # Fallback to placeholder response
                return {
                    "response": f"Echo: {message} (AI provider not configured)",
                    "model": "placeholder",
                    "tokens": 0
                }
            
            # Generate response using LangChain
            response = await self.chain.arun(message)
            
            return {
                "response": response,
                "model": settings.GEMINI_MODEL if self.provider == AIProvider.GEMINI else settings.OPENAI_MODEL,
                "provider": self.provider.value,
                "tokens": len(response.split())  # Rough token count
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return {
                "response": f"I apologize, but I encountered an error processing your message. Please try again.",
                "model": "error",
                "tokens": 0,
                "error": str(e)
            }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current AI provider"""
        return {
            "provider": self.provider.value,
            "model": settings.GEMINI_MODEL if self.provider == AIProvider.GEMINI else settings.OPENAI_MODEL,
            "initialized": self.model is not None,
            "langsmith_enabled": settings.LANGCHAIN_TRACING_V2
        }
