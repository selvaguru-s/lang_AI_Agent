from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from utils.auth import verify_firebase_token, get_or_create_user, get_current_user
from models.user import User


router = APIRouter()


class FirebaseTokenRequest(BaseModel):
    id_token: str


class AuthResponse(BaseModel):
    api_key: str
    user_id: str
    email: str
    name: str


@router.post("/login", response_model=AuthResponse)
async def login_with_firebase(request: FirebaseTokenRequest):
    """
    Authenticate user with Firebase ID token and return API key
    """
    try:
        # Verify Firebase token
        firebase_user = await verify_firebase_token(request.id_token)
        
        if not firebase_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Firebase token"
            )
        
        # Get or create user
        user = await get_or_create_user(firebase_user)
        
        return AuthResponse(
            api_key=user.api_key,
            user_id=str(user.id),
            email=user.email,
            name=user.name
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/refresh")
async def refresh_token(request: FirebaseTokenRequest):
    """
    Refresh user session with new Firebase token
    """
    return await login_with_firebase(request)


@router.get("/me", response_model=AuthResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information including API key
    """
    try:
        return AuthResponse(
            api_key=current_user.api_key,
            user_id=str(current_user.id),
            email=current_user.email,
            name=current_user.name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )