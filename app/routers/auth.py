from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from app.models.user import UserLogin
from app.auth import authenticate_user, login_user, logout_user, get_current_user
from app.database import get_session

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/logowanie", response_class=HTMLResponse, name="login_page")
async def login_page(request: Request):
    """Strona logowania"""
    # Jeśli użytkownik jest już zalogowany, przekieruj
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/kontakty", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse(
        "auth/login.html", 
        {
            "request": request,
            "title": "Logowanie - Książka Telefoniczna"
        }
    )


@router.post("/logowanie")
async def login(
    request: Request,
    email: str = Form(..., description="Adres email"),
    password: str = Form(..., description="Hasło")
):
    """Przetwarzanie logowania"""
    session = next(get_session())
    
    # Próba uwierzytelnienia
    user = authenticate_user(email, password, session)
    
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "title": "Logowanie - Książka Telefoniczna",
                "error": "Nieprawidłowy email lub hasło"
            }
        )
    
    # Logowanie użytkownika
    login_user(request, user)
    
    return RedirectResponse(url="/kontakty", status_code=status.HTTP_302_FOUND)


@router.get("/wyloguj")
async def logout(request: Request):
    """Wylogowanie użytkownika"""
    logout_user(request)
    return RedirectResponse(url="/logowanie", status_code=status.HTTP_302_FOUND)
