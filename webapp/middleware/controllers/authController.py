from fastapi import APIRouter, HTTPException
from webapp.middleware.services.authService import AuthService
from webapp.middleware.serializers.authSerializer import AuthSerializer

router = APIRouter(tags=["Session API"])


@router.post("/login", response_model=AuthSerializer.AuthResponse)
async def login(auth: AuthSerializer.AuthRequest):
    token = AuthService.login(auth.login, auth.password)
    if not token:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return {"session_token": token}
