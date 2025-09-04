"""
User routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import UserResponse, PasswordChange
from app.services.auth import auth_service
from app.utils.dependencies import get_current_user
from app.models.user import User
from app.core.security import security

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get user profile
    """
    return UserResponse.from_orm(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    full_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user profile
    """
    try:
        current_user.full_name = full_name
        await db.commit()
        await db.refresh(current_user)
        
        return UserResponse.from_orm(current_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password
    """
    try:
        # Verify current password
        if not security.verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.hashed_password = security.get_password_hash(password_data.new_password)
        await db.commit()
        
        # Logout from all sessions for security
        await auth_service.logout_all_sessions(db, current_user.id)
        
        return {"message": "Password changed successfully. Please login again."}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user account
    """
    try:
        # Logout from all sessions
        await auth_service.logout_all_sessions(db, current_user.id)
        
        # Deactivate account instead of deleting
        current_user.is_active = False
        await db.commit()
        
        return {"message": "Account deactivated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )
