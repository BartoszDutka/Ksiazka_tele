from sqlmodel import SQLModel, Field, Column, String
from typing import Optional
from datetime import datetime
import uuid


class ContactBase(SQLModel):
    """Bazowy model kontaktu z wspólnymi polami"""
    imie: Optional[str] = Field(default=None, description="Imię lub nazwa kontaktu")
    nazwisko: Optional[str] = Field(default=None, description="Nazwisko kontaktu")
    numer_wewnetrzny: str = Field(
        unique=True, 
        index=True, 
        description="Unikalny numer wewnętrzny firmy"
    )
    dzial: Optional[str] = Field(default=None, index=True, description="Nazwa działu")
    firma: Optional[str] = Field(default=None, description="Nazwa firmy")
    notatki: Optional[str] = Field(default=None, description="Dodatkowe notatki")


class Contact(ContactBase, table=True):
    """Model kontaktu w bazie danych"""
    __tablename__ = "kontakty"
    
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True,
        description="Unikalny identyfikator kontaktu"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Data utworzenia kontaktu"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Data ostatniej modyfikacji"
    )


class ContactCreate(ContactBase):
    """Schema do tworzenia kontaktu"""
    pass


class ContactUpdate(SQLModel):
    """Schema do aktualizacji kontaktu"""
    imie: Optional[str] = Field(default=None, description="Imię kontaktu")
    nazwisko: Optional[str] = Field(default=None, description="Nazwisko kontaktu")
    numer_wewnetrzny: Optional[str] = Field(default=None, description="Numer wewnętrzny")
    dzial: Optional[str] = Field(default=None, description="Nazwa działu")
    firma: Optional[str] = Field(default=None, description="Nazwa firmy")
    notatki: Optional[str] = Field(default=None, description="Dodatkowe notatki")


class ContactResponse(ContactBase):
    """Schema odpowiedzi z kontaktem"""
    id: str = Field(description="Identyfikator kontaktu")
    created_at: datetime = Field(description="Data utworzenia")
    updated_at: datetime = Field(description="Data ostatniej modyfikacji")


class ContactSearchParams(SQLModel):
    """Parametry wyszukiwania kontaktów"""
    q: Optional[str] = Field(default=None, description="Fraza do wyszukania")
    dzial: Optional[str] = Field(default=None, description="Filtr po dziale")
    sort: Optional[str] = Field(
        default="nazwisko_asc", 
        description="Sortowanie: nazwisko_asc, nazwisko_desc, dzial_asc, data_desc"
    )
    page: int = Field(default=1, ge=1, description="Numer strony")
    page_size: int = Field(default=20, ge=1, le=100, description="Liczba wyników na stronę")
