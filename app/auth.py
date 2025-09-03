from passlib.context import CryptContext
from fastapi import Request, HTTPException, status
from sqlmodel import Session, select
from app.models.user import User
from app.database import get_session
from app.config import settings
from typing import Optional

# Konfiguracja hashowania haseł
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashuje hasło"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Weryfikuje hasło"""
    return pwd_context.verify(plain_password, hashed_password)


def create_admin_user(session: Session) -> None:
    """Tworzy użytkownika admin jeśli nie istnieje"""
    admin = session.exec(select(User).where(User.email == settings.admin_email)).first()
    
    if not admin:
        admin = User(
            email=settings.admin_email,
            hashed_password=hash_password(settings.admin_password),
            is_admin=True
        )
        session.add(admin)
        session.commit()


def authenticate_user(email: str, password: str, session: Session) -> Optional[User]:
    """Uwierzytelnia użytkownika"""
    user = session.exec(select(User).where(User.email == email)).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def get_current_user(request: Request) -> Optional[User]:
    """Pobiera aktualnie zalogowanego użytkownika z sesji"""
    user_id = request.session.get("user_id")
    
    if not user_id:
        return None
    
    # Pobierz użytkownika z bazy danych
    session = next(get_session())
    user = session.get(User, user_id)
    
    return user


def require_admin(request: Request) -> User:
    """Wymaga zalogowanego administratora"""
    user = get_current_user(request)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wymagane logowanie"
        )
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wymagane uprawnienia administratora"
        )
    
    return user


def login_user(request: Request, user: User) -> None:
    """Loguje użytkownika (tworzy sesję)"""
    request.session["user_id"] = user.id


def logout_user(request: Request) -> None:
    """Wylogowuje użytkownika (usuwa sesję)"""
    request.session.clear()
