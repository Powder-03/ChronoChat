"""
Authentication endpoints using Clerk
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging

from app.core.clerk import get_current_user, get_optional_user, clerk_auth

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/me")
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Requires: Bearer token in Authorization header
    """
    try:
        # Fetch full user details from Clerk
        user_info = await clerk_auth.get_user_info(current_user["user_id"])
        return {
            "user_id": current_user["user_id"],
            "email": current_user.get("email"),
            "user_info": user_info
        }
    except Exception as e:
        logger.error(f"Error fetching user info: {str(e)}")
        # Return basic info if Clerk API fails
        return {
            "user_id": current_user["user_id"],
            "email": current_user.get("email")
        }


@router.post("/verify")
async def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Verify authentication token
    
    Requires: Bearer token in Authorization header
    """
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "email": current_user.get("email")
    }


@router.get("/session/{session_id}")
async def verify_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Verify Clerk session
    
    Requires: Bearer token in Authorization header
    """
    try:
        session_info = await clerk_auth.verify_session(session_id)
        return {
            "valid": True,
            "session": session_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying session"
        )
