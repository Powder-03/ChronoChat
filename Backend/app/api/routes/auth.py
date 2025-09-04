"""
Authentication routes
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token, TokenRefresh, LogoutResponse
from app.services.auth import auth_service
from app.utils.dependencies import get_current_user, get_client_ip, get_user_agent
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    """
    try:
        # Create user
        user_response = await auth_service.register_user(db, user_data)
        
        # Get user object for session creation
        user = await auth_service.get_user_by_username(db, user_data.username)
        
        # Create session and return tokens
        token = await auth_service.create_user_session(
            db=db,
            user=user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        return token
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Login user
    """
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(db, login_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create session and return tokens
        token = await auth_service.create_user_session(
            db=db,
            user=user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            remember_me=login_data.remember_me
        )
        
        return token
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token
    """
    try:
        token = await auth_service.refresh_token(db, token_data.refresh_token)
        return token
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout current user
    """
    try:
        # Extract session token from authorization header
        authorization = request.headers.get("Authorization", "")
        if authorization.startswith("Bearer "):
            session_token = authorization.split(" ")[1]
            await auth_service.logout_user(db, session_token)
        
        return LogoutResponse(
            message="Successfully logged out",
            logged_out_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.post("/logout-all", response_model=LogoutResponse)
async def logout_all_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user from all sessions
    """
    try:
        await auth_service.logout_all_sessions(db, current_user.id)
        
        return LogoutResponse(
            message="Successfully logged out from all sessions",
            logged_out_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout all sessions failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    return UserResponse.from_orm(current_user)


@router.get("/verify")
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    """
    Verify if token is valid
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username
    }
