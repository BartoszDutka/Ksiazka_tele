from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class User(SQLModel, table=True):
    """Model użytkownika (admin)"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True, description="Adres email użytkownika")
    hashed_password: str = Field(description="Zahashowane hasło")
    is_admin: bool = Field(default=True, description="Czy użytkownik jest administratorem")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data utworzenia")


class UserCreate(SQLModel):
    """Schema do tworzenia użytkownika"""
    email: str = Field(description="Adres email")
    password: str = Field(description="Hasło")


class UserLogin(SQLModel):
    """Schema do logowania"""
    email: str = Field(description="Adres email")
    password: str = Field(description="Hasło")
