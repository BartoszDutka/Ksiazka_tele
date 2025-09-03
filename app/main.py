from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlmodel import Session
from app.config import settings
from app.database import create_db_and_tables, get_session
from app.auth import create_admin_user
from app.routers import contacts, auth
from app.routers.api import contacts as api_contacts

# Inicjalizacja aplikacji
app = FastAPI(
    title="Książka Telefoniczna",
    description="Aplikacja do zarządzania kontaktami firmowymi z numerami wewnętrznymi",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    max_age=86400,  # 24 godziny
    same_site="lax",
    https_only=False  # True w produkcji
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:80", "http://127.0.0.1:80", "https://ksiazka-tel.siec.instytut"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Statyczne pliki
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routery
app.include_router(contacts.router)
app.include_router(auth.router)
app.include_router(api_contacts.router)

# Templates
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
async def startup_event():
    """Inicjalizacja przy starcie aplikacji"""
    # Tworzenie tabel
    create_db_and_tables()
    
    # Tworzenie użytkownika admin
    session = next(get_session())
    create_admin_user(session)
    session.close()


@app.get("/", include_in_schema=False)
async def root():
    """Przekierowanie głównej strony do kontaktów"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/kontakty")


# Middleware do obsługi komunikatów flash
@app.middleware("http")
async def flash_middleware(request: Request, call_next):
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=80,
        reload=settings.debug
    )
