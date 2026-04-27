from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    user_name: str = Field(max_length=36)
    password: str


class UserResponse(BaseModel):
    id: int
    user_name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuthRequest(BaseModel):
    user_name: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
