from enum import Enum
from typing import List
from pydantic import BaseModel

class LoginRequest(BaseModel):
    user: str
    password: str | None


TOKEN_ERROR_MESSAGE = "Authentication failed"
TOKEN_RESPONSE_DESCRIPTION = "Authentication successful, JWT token generated"
TOKEN_RESPONSE_EXAMPLE = {
    "access_token": "....",
    "token_type": "bearer",
    "status": "success",
    "message": "Authentication successful"
}     

# Define the full response schema
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    status: str
    message: str

