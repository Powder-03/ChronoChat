"""
Clerk authentication utilities and middleware
"""
import jwt
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize HTTP Bearer security scheme
security = HTTPBearer()


class ClerkAuth:
    """Clerk authentication handler"""
    
    def __init__(self):
        self.secret_key = settings.CLERK_SECRET_KEY
        self.jwt_key = settings.CLERK_JWT_KEY
        self.publishable_key = settings.CLERK_PUBLISHABLE_KEY
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Clerk JWT token
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            # Decode and verify JWT token
            payload = jwt.decode(
                token,
                self.jwt_key,
                algorithms=["RS256"],
                options={"verify_signature": True}
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get user information from Clerk API
        
        Args:
            user_id: Clerk user ID
            
        Returns:
            User information dictionary
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.clerk.com/v1/users/{user_id}",
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error fetching user info: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching user information"
            )
    
    async def verify_session(self, session_id: str) -> Dict[str, Any]:
        """
        Verify Clerk session
        
        Args:
            session_id: Clerk session ID
            
        Returns:
            Session information dictionary
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.clerk.com/v1/sessions/{session_id}",
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error verifying session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session"
            )


# Create ClerkAuth instance
clerk_auth = ClerkAuth()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = None
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user
    
    Args:
        request: FastAPI request object
        credentials: HTTP Bearer credentials
        
    Returns:
        Current user information
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        # Try to get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        token = auth_header.replace("Bearer ", "")
    else:
        token = credentials.credentials
    
    # Verify token
    payload = await clerk_auth.verify_token(token)
    
    # Get user information
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "payload": payload
    }


async def get_optional_user(
    request: Request
) -> Optional[Dict[str, Any]]:
    """
    Dependency to get current user if authenticated (optional)
    
    Args:
        request: FastAPI request object
        
    Returns:
        Current user information or None
    """
    try:
        return await get_current_user(request)
    except HTTPException:
        return None
