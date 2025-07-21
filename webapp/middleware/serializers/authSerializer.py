from pydantic import BaseModel


class AuthSerializer(BaseModel):
    class AuthRequest(BaseModel):
        login: str
        password: str

    class AuthResponse(BaseModel):
        session_token: str
