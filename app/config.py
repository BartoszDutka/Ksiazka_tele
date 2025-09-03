from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    admin_email: str = "admin@firma.pl"
    admin_password: str = "admin123"
    secret_key: str = "super_tajny_klucz_sesji_min_32_znaki_dla_bezpieczenstwa"
    database_url: str = "sqlite:///./ksiazka_tele.db"
    debug: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()
