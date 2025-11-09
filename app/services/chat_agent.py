"""
LangGraph-based chatbot agent
Implements a conversational AI agent with memory and state management
"""
from typing import TypedDict, Annotated, Sequence, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
import logging

from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the conversational agent"""
    messages: Annotated[Sequence[BaseMessage], "The conversation messages"]
    user_id: str
    conversation_id: str
    current_query: str
    response: Optional[str]
    metadata: Dict[str, Any]


class ChatAgent:
    """
    LangGraph-based conversational agent
    Manages conversation flow with state and memory
    """
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.graph = self._build_graph()
        self.memory = ConversationBufferMemory()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Define the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("process_input", self._process_input)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("format_output", self._format_output)
        
        # Define edges
        workflow.set_entry_point("process_input")
        workflow.add_edge("process_input", "generate_response")
        workflow.add_edge("generate_response", "format_output")
        workflow.add_edge("format_output", END)
        
        return workflow.compile()
    
    async def _process_input(self, state: AgentState) -> AgentState:
        """Process and validate user input"""
        logger.info(f"Processing input for conversation {state['conversation_id']}")
        
        # Add system message if this is the first message
        if not state.get("messages"):
            system_message = SystemMessage(content=(
                "You are ChronoChat, a helpful and friendly AI assistant. "
                "Provide accurate, concise, and helpful responses. "
                "Be conversational and engaging while maintaining professionalism."
            ))
            state["messages"] = [system_message]
        
        # Add user message
        user_message = HumanMessage(content=state["current_query"])
        state["messages"].append(user_message)
        
        return state
    
    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate AI response using the AI service"""
        logger.info(f"Generating response for conversation {state['conversation_id']}")
        
        try:
            # Convert messages to history format for AI service
            conversation_history = [
                {
                    "role": self._get_role(msg),
                    "content": msg.content
                }
                for msg in state["messages"]
            ]
            
            # Generate response
            ai_result = await self.ai_service.generate_response(
                message=state["current_query"],
                conversation_history=conversation_history
            )
            
            # Update state with response
            state["response"] = ai_result["response"]
            state["metadata"]["model"] = ai_result.get("model")
            state["metadata"]["provider"] = ai_result.get("provider")
            state["metadata"]["tokens"] = ai_result.get("tokens")
            
            # Add AI message to conversation
            ai_message = AIMessage(content=ai_result["response"])
            state["messages"].append(ai_message)
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            state["response"] = "I apologize, but I encountered an error. Please try again."
            state["metadata"]["error"] = str(e)
        
        return state
    
    async def _format_output(self, state: AgentState) -> AgentState:
        """Format the final output"""
        logger.info(f"Formatting output for conversation {state['conversation_id']}")
        
        # Add any final formatting or post-processing here
        # For now, just return the state as-is
        return state
    
    def _get_role(self, message: BaseMessage) -> str:
        """Get role from message type"""
        if isinstance(message, HumanMessage):
            return "user"
        elif isinstance(message, AIMessage):
            return "assistant"
        elif isinstance(message, SystemMessage):
            return "system"
        return "user"
    
    async def process_message(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
        existing_messages: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message through the agent
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            message: User message
            existing_messages: Previous messages in the conversation
            metadata: Additional metadata
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Prepare initial state
            initial_state: AgentState = {
                "messages": [],
                "user_id": user_id,
                "conversation_id": conversation_id,
                "current_query": message,
                "response": None,
                "metadata": metadata or {}
            }
            
            # Add existing messages if provided
            if existing_messages:
                for msg in existing_messages:
                    if msg["role"] == "user":
                        initial_state["messages"].append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        initial_state["messages"].append(AIMessage(content=msg["content"]))
                    elif msg["role"] == "system":
                        initial_state["messages"].append(SystemMessage(content=msg["content"]))
            
            # Run the graph
            result = await self.graph.ainvoke(initial_state)
            
            return {
                "response": result["response"],
                "metadata": result["metadata"]
            }
            
        except Exception as e:
            logger.error(f"Error in chat agent: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error processing your message.",
                "metadata": {"error": str(e)}
            }
    
    def get_conversation_summary(self, messages: list) -> str:
        """Generate a summary of the conversation for the title"""
        if not messages:
            return "New Conversation"
        
        first_message = messages[0]
        if isinstance(first_message, dict):
            content = first_message.get("content", "")
        else:
            content = first_message.content
        
        # Simple summary: first 50 characters of first message
        return content[:50] + "..." if len(content) > 50 else content
