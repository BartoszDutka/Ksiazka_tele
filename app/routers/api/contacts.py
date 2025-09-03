from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from sqlmodel import Session, select, or_, func
from typing import List, Optional
from datetime import datetime
from app.models.contact import (
    Contact, 
    ContactCreate, 
    ContactUpdate, 
    ContactResponse,
    ContactSearchParams
)
from app.auth import require_admin
from app.database import get_session

router = APIRouter(prefix="/api", tags=["Kontakty API"])


@router.get(
    "/kontakty",
    response_model=dict,
    summary="Lista kontaktów",
    description="Pobiera listę kontaktów z możliwością wyszukiwania, filtrowania i sortowania"
)
async def get_contacts(
    q: Optional[str] = Query(None, description="Fraza do wyszukania w imię, nazwisko, dziale, numerze wewnętrznym"),
    dzial: Optional[str] = Query(None, description="Filtr po dziale"),
    sort: str = Query("nazwisko_asc", description="Sortowanie: nazwisko_asc, nazwisko_desc, dzial_asc, data_desc"),
    page: int = Query(1, ge=1, description="Numer strony"),
    page_size: int = Query(20, ge=1, le=100, description="Liczba wyników na stronę"),
    session: Session = Depends(get_session)
):
    """Pobiera listę kontaktów z parametrami wyszukiwania"""
    
    # Podstawowe zapytanie
    query = select(Contact)
    
    # Wyszukiwanie
    if q:
        search_term = f"%{q.strip()}%"
        query = query.where(
            or_(
                Contact.imie.contains(search_term),
                Contact.nazwisko.contains(search_term),
                Contact.numer_wewnetrzny.contains(search_term),
                Contact.dzial.contains(search_term),
                Contact.firma.contains(search_term),
                Contact.notatki.contains(search_term)
            )
        )
    
    # Filtrowanie po dziale
    if dzial:
        query = query.where(Contact.dzial == dzial)
    
    # Sortowanie
    if sort == "nazwisko_desc":
        query = query.order_by(Contact.nazwisko.desc())
    elif sort == "dzial_asc":
        query = query.order_by(Contact.dzial.asc())
    elif sort == "data_desc":
        query = query.order_by(Contact.created_at.desc())
    else:  # nazwisko_asc (domyślne)
        query = query.order_by(Contact.nazwisko.asc())
    
    # Paginacja
    offset = (page - 1) * page_size
    
    # Pobierz kontakty
    contacts = session.exec(query.offset(offset).limit(page_size)).all()
    
    # Policz wszystkie wyniki
    count_query = select(func.count(Contact.id))
    if q:
        search_term = f"%{q.strip()}%"
        count_query = count_query.where(
            or_(
                Contact.imie.contains(search_term),
                Contact.nazwisko.contains(search_term),
                Contact.numer_wewnetrzny.contains(search_term),
                Contact.dzial.contains(search_term),
                Contact.firma.contains(search_term),
                Contact.notatki.contains(search_term)
            )
        )
    if dzial:
        count_query = count_query.where(Contact.dzial == dzial)
    
    total_count = session.exec(count_query).first()
    total_pages = (total_count + page_size - 1) // page_size
    
    return {
        "kontakty": [ContactResponse.model_validate(contact) for contact in contacts],
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages
    }


@router.get(
    "/kontakty/{contact_id}",
    response_model=ContactResponse,
    summary="Szczegóły kontaktu",
    description="Pobiera szczegóły konkretnego kontaktu"
)
async def get_contact(
    contact_id: str,
    session: Session = Depends(get_session)
):
    """Pobiera szczegóły kontaktu"""
    contact = session.get(Contact, contact_id)
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kontakt nie został znaleziony"
        )
    
    return ContactResponse.model_validate(contact)


@router.post(
    "/kontakty",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dodaj kontakt",
    description="Tworzy nowy kontakt (wymagane uprawnienia administratora)"
)
async def create_contact(
    request: Request,
    contact_data: ContactCreate,
    session: Session = Depends(get_session)
):
    """Tworzy nowy kontakt"""
    # Wymagaj uprawnień administratora
    require_admin(request)
    
    # Sprawdź unikalność numeru wewnętrznego
    existing = session.exec(
        select(Contact).where(Contact.numer_wewnetrzny == contact_data.numer_wewnetrzny)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Numer wewnętrzny już istnieje"
        )
    
    # Stwórz kontakt
    contact = Contact(**contact_data.model_dump())
    session.add(contact)
    session.commit()
    session.refresh(contact)
    
    return ContactResponse.model_validate(contact)


@router.put(
    "/kontakty/{contact_id}",
    response_model=ContactResponse,
    summary="Aktualizuj kontakt",
    description="Aktualizuje istniejący kontakt (wymagane uprawnienia administratora)"
)
async def update_contact(
    request: Request,
    contact_id: str,
    contact_data: ContactUpdate,
    session: Session = Depends(get_session)
):
    """Aktualizuje kontakt"""
    # Wymagaj uprawnień administratora
    require_admin(request)
    
    contact = session.get(Contact, contact_id)
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kontakt nie został znaleziony"
        )
    
    # Sprawdź unikalność numeru wewnętrznego (jeśli się zmienia)
    if contact_data.numer_wewnetrzny and contact_data.numer_wewnetrzny != contact.numer_wewnetrzny:
        existing = session.exec(
            select(Contact).where(
                Contact.numer_wewnetrzny == contact_data.numer_wewnetrzny,
                Contact.id != contact_id
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Numer wewnętrzny już istnieje"
            )
    
    # Aktualizuj tylko podane pola
    update_data = contact_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    contact.updated_at = datetime.utcnow()
    
    session.add(contact)
    session.commit()
    session.refresh(contact)
    
    return ContactResponse.model_validate(contact)


@router.delete(
    "/kontakty/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Usuń kontakt",
    description="Usuwa kontakt (wymagane uprawnienia administratora)"
)
async def delete_contact(
    request: Request,
    contact_id: str,
    session: Session = Depends(get_session)
):
    """Usuwa kontakt"""
    # Wymagaj uprawnień administratora
    require_admin(request)
    
    contact = session.get(Contact, contact_id)
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kontakt nie został znaleziony"
        )
    
    session.delete(contact)
    session.commit()
    
    return None
