"""
Chat routes
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ChatThread, ChatHistory
from app.services.chat import chat_service
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a chat message
    """
    try:
        # Get or create thread
        if request.thread_id:
            thread = await chat_service.get_thread(db, request.thread_id, current_user)
            if not thread:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Thread not found"
                )
        else:
            # Create new thread
            thread = await chat_service.create_thread(db, current_user, "New Chat")
        
        # Add user message
        user_message = await chat_service.add_message(
            db=db,
            thread=thread,
            role="user",
            content=request.message
        )
        
        # TODO: Integrate with AI service to generate response
        # For now, return a mock response
        ai_response = f"I received your message: {request.message}"
        
        # Add AI message
        ai_message = await chat_service.add_message(
            db=db,
            thread=thread,
            role="assistant",
            content=ai_response
        )
        
        # Store in Redis for quick access
        messages = [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": ai_response}
        ]
        await chat_service.store_session_data(thread.id, messages)
        
        return ChatResponse(
            response=ai_response,
            thread_id=thread.id,
            message_id=ai_message.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/threads", response_model=List[ChatThread])
async def get_threads(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's chat threads
    """
    try:
        threads = await chat_service.get_user_threads(db, current_user)
        return [ChatThread.from_orm(thread) for thread in threads]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get threads: {str(e)}"
        )


@router.get("/threads/{thread_id}", response_model=ChatHistory)
async def get_thread_history(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get chat thread history
    """
    try:
        thread = await chat_service.get_thread(db, thread_id, current_user)
        
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found"
            )
        
        messages = await chat_service.get_thread_messages(db, thread)
        
        return ChatHistory(
            thread=ChatThread.from_orm(thread),
            messages=[ChatMessage.from_orm(msg) for msg in messages],
            total_messages=len(messages)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get thread history: {str(e)}"
        )


@router.delete("/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a chat thread
    """
    try:
        success = await chat_service.delete_thread(db, thread_id, current_user)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found"
            )
        
        return {"message": "Thread deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete thread: {str(e)}"
        )


@router.put("/threads/{thread_id}/title")
async def update_thread_title(
    thread_id: str,
    title: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update thread title
    """
    try:
        thread = await chat_service.get_thread(db, thread_id, current_user)
        
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found"
            )
        
        updated_thread = await chat_service.update_thread_title(db, thread, title)
        
        return ChatThread.from_orm(updated_thread)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update thread title: {str(e)}"
        )


@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user chat statistics
    """
    try:
        stats = await chat_service.get_user_stats(db, current_user)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}"
        )
