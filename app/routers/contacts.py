from fastapi import APIRouter, Request, Form, HTTPException, status, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, or_, func
from typing import List, Optional
from datetime import datetime
from app.models.contact import Contact, ContactCreate, ContactUpdate
from app.auth import get_current_user, require_admin
from app.database import get_session

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Strona główna - przekierowanie do kontaktów"""
    return RedirectResponse(url="/kontakty", status_code=status.HTTP_302_FOUND)


@router.get("/kontakty", response_class=HTMLResponse, name="contacts_list")
async def contacts_list(
    request: Request,
    q: Optional[str] = Query(None, description="Wyszukiwana fraza"),
    dzial: Optional[str] = Query(None, description="Filtr po dziale"),
    sort: str = Query("nazwisko_asc", description="Sortowanie"),
    page: int = Query(1, ge=1, description="Numer strony"),
    session: Session = Depends(get_session)
):
    """Lista kontaktów z wyszukiwaniem i filtrowaniem"""
    
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
        # Sortowanie po dziale z uwzględnieniem wartości NULL
        # Używamy coalesce aby NULL wartości zostały zastąpione pustym stringiem
        # dzięki czemu będą sortowane jako pierwsze
        query = query.order_by(
            func.coalesce(Contact.dzial, "").asc(),
            Contact.nazwisko.asc()
        )
    elif sort == "data_desc":
        query = query.order_by(Contact.created_at.desc())
    else:  # nazwisko_asc (domyślne)
        query = query.order_by(Contact.nazwisko.asc())
    
    # Paginacja
    page_size = 20
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
    
    # Pobierz unikalne działy dla filtra
    dzialy_query = select(Contact.dzial).where(Contact.dzial.is_not(None)).distinct()
    dzialy = [d for d in session.exec(dzialy_query).all() if d]
    dzialy.sort()
    
    # Sprawdź czy to żądanie HTMX
    is_htmx = request.headers.get("HX-Request") == "true"
    
    # Sprawdź czy użytkownik jest zalogowany
    user = get_current_user(request)
    
    # Dla żądań HTMX zwróć tylko partial template
    if is_htmx:
        return templates.TemplateResponse(
            "contacts/list_partial.html",
            {
                "request": request,
                "contacts": contacts,
                "user": user,
                "q": q or "",
                "dzial": dzial,
                "sort": sort,
                "page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "dzialy": dzialy,
                "has_prev": page > 1,
                "has_next": page < total_pages,
                "prev_page": page - 1 if page > 1 else None,
                "next_page": page + 1 if page < total_pages else None
            }
        )
    
    return templates.TemplateResponse(
        "contacts/list.html",
        {
            "request": request,
            "title": "Kontakty - Książka Telefoniczna",
            "contacts": contacts,
            "user": user,
            "q": q or "",
            "dzial": dzial,
            "sort": sort,
            "page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "dzialy": dzialy,
            "has_prev": page > 1,
            "has_next": page < total_pages,
            "prev_page": page - 1 if page > 1 else None,
            "next_page": page + 1 if page < total_pages else None
        }
    )


@router.get("/kontakty/nowy", response_class=HTMLResponse, name="contact_create")
async def contact_create_form(request: Request):
    """Formularz dodawania nowego kontaktu"""
    # Wymagaj zalogowania administratora
    try:
        require_admin(request)
    except HTTPException:
        return RedirectResponse(url="/logowanie", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse(
        "contacts/create.html",
        {
            "request": request,
            "title": "Nowy kontakt - Książka Telefoniczna"
        }
    )


@router.post("/kontakty/nowy")
async def contact_create(
    request: Request,
    imie: str = Form(..., description="Imię"),
    nazwisko: str = Form(..., description="Nazwisko"),
    numer_wewnetrzny: str = Form(..., description="Numer wewnętrzny"),
    dzial: str = Form("", description="Dział"),
    firma: str = Form("", description="Firma"),
    notatki: str = Form("", description="Notatki"),
    session: Session = Depends(get_session)
):
    """Przetwarzanie dodawania kontaktu"""
    # Wymagaj zalogowania administratora
    try:
        require_admin(request)
    except HTTPException:
        return RedirectResponse(url="/logowanie", status_code=status.HTTP_302_FOUND)
    
    # Walidacja
    errors = {}
    
    if not numer_wewnetrzny.strip():
        errors["numer_wewnetrzny"] = "Numer wewnętrzny jest wymagany"
    
    # Sprawdź unikalność numeru wewnętrznego
    if numer_wewnetrzny.strip():
        existing = session.exec(
            select(Contact).where(Contact.numer_wewnetrzny == numer_wewnetrzny.strip())
        ).first()
        if existing:
            errors["numer_wewnetrzny"] = "Numer wewnętrzny już istnieje"
    
    if errors:
        return templates.TemplateResponse(
            "contacts/create.html",
            {
                "request": request,
                "title": "Nowy kontakt - Książka Telefoniczna",
                "errors": errors,
                "imie": imie,
                "nazwisko": nazwisko,
                "numer_wewnetrzny": numer_wewnetrzny,
                "dzial": dzial,
                "firma": firma,
                "notatki": notatki
            }
        )
    
    # Stwórz kontakt
    contact = Contact(
        imie=imie.strip(),
        nazwisko=nazwisko.strip(),
        numer_wewnetrzny=numer_wewnetrzny.strip(),
        dzial=dzial.strip() if dzial.strip() else None,
        firma=firma.strip() if firma.strip() else None,
        notatki=notatki.strip() if notatki.strip() else None
    )
    
    session.add(contact)
    session.commit()
    
    # Przekieruj z komunikatem sukcesu
    request.session["flash_message"] = "Kontakt został dodany pomyślnie"
    return RedirectResponse(url="/kontakty", status_code=status.HTTP_302_FOUND)


@router.get("/kontakty/{contact_id}", response_class=HTMLResponse, name="contact_detail")
async def contact_detail(
    request: Request,
    contact_id: str,
    session: Session = Depends(get_session)
):
    """Szczegóły kontaktu"""
    contact = session.get(Contact, contact_id)
    
    if not contact:
        raise HTTPException(status_code=404, detail="Kontakt nie został znaleziony")
    
    user = get_current_user(request)
    
    return templates.TemplateResponse(
        "contacts/detail.html",
        {
            "request": request,
            "title": f"{contact.imie} {contact.nazwisko} - Książka Telefoniczna",
            "contact": contact,
            "user": user
        }
    )


@router.get("/kontakty/{contact_id}/edytuj", response_class=HTMLResponse, name="contact_edit")
async def contact_edit_form(
    request: Request,
    contact_id: str,
    session: Session = Depends(get_session)
):
    """Formularz edycji kontaktu"""
    # Wymagaj zalogowania administratora
    try:
        require_admin(request)
    except HTTPException:
        return RedirectResponse(url="/logowanie", status_code=status.HTTP_302_FOUND)
    
    contact = session.get(Contact, contact_id)
    
    if not contact:
        raise HTTPException(status_code=404, detail="Kontakt nie został znaleziony")
    
    return templates.TemplateResponse(
        "contacts/edit.html",
        {
            "request": request,
            "title": f"Edytuj {contact.imie} {contact.nazwisko} - Książka Telefoniczna",
            "contact": contact
        }
    )


@router.post("/kontakty/{contact_id}/edytuj")
async def contact_edit(
    request: Request,
    contact_id: str,
    imie: str = Form(..., description="Imię"),
    nazwisko: str = Form(..., description="Nazwisko"),
    numer_wewnetrzny: str = Form(..., description="Numer wewnętrzny"),
    dzial: str = Form("", description="Dział"),
    firma: str = Form("", description="Firma"),
    notatki: str = Form("", description="Notatki"),
    session: Session = Depends(get_session)
):
    """Przetwarzanie edycji kontaktu"""
    # Wymagaj zalogowania administratora
    try:
        require_admin(request)
    except HTTPException:
        return RedirectResponse(url="/logowanie", status_code=status.HTTP_302_FOUND)
    
    contact = session.get(Contact, contact_id)
    
    if not contact:
        raise HTTPException(status_code=404, detail="Kontakt nie został znaleziony")
    
    # Walidacja
    errors = {}
    
    if not numer_wewnetrzny.strip():
        errors["numer_wewnetrzny"] = "Numer wewnętrzny jest wymagany"
    
    # Sprawdź unikalność numeru wewnętrznego (pomijając aktualny kontakt)
    if numer_wewnetrzny.strip():
        existing = session.exec(
            select(Contact).where(
                Contact.numer_wewnetrzny == numer_wewnetrzny.strip(),
                Contact.id != contact_id
            )
        ).first()
        if existing:
            errors["numer_wewnetrzny"] = "Numer wewnętrzny już istnieje"
    
    if errors:
        return templates.TemplateResponse(
            "contacts/edit.html",
            {
                "request": request,
                "title": f"Edytuj {contact.imie} {contact.nazwisko} - Książka Telefoniczna",
                "contact": contact,
                "errors": errors,
                "imie": imie,
                "nazwisko": nazwisko,
                "numer_wewnetrzny": numer_wewnetrzny,
                "dzial": dzial,
                "firma": firma,
                "notatki": notatki
            }
        )
    
    # Aktualizuj kontakt
    contact.imie = imie.strip()
    contact.nazwisko = nazwisko.strip()
    contact.numer_wewnetrzny = numer_wewnetrzny.strip()
    contact.dzial = dzial.strip() if dzial.strip() else None
    contact.firma = firma.strip() if firma.strip() else None
    contact.notatki = notatki.strip() if notatki.strip() else None
    contact.updated_at = datetime.utcnow()
    
    session.add(contact)
    session.commit()
    
    # Przekieruj z komunikatem sukcesu
    request.session["flash_message"] = "Kontakt został zaktualizowany pomyślnie"
    return RedirectResponse(url=f"/kontakty/{contact_id}", status_code=status.HTTP_302_FOUND)


@router.post("/kontakty/{contact_id}/usun")
async def contact_delete(
    request: Request,
    contact_id: str,
    session: Session = Depends(get_session)
):
    """Usuwanie kontaktu"""
    # Wymagaj zalogowania administratora
    try:
        require_admin(request)
    except HTTPException:
        return RedirectResponse(url="/logowanie", status_code=status.HTTP_302_FOUND)
    
    contact = session.get(Contact, contact_id)
    
    if not contact:
        raise HTTPException(status_code=404, detail="Kontakt nie został znaleziony")
    
    session.delete(contact)
    session.commit()
    
    # Przekieruj z komunikatem sukcesu
    request.session["flash_message"] = "Kontakt został usunięty pomyślnie"
    return RedirectResponse(url="/kontakty", status_code=status.HTTP_302_FOUND)
