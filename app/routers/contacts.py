from fastapi import APIRouter, Request, Form, HTTPException, status, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, or_, func
from typing import List, Optional
from datetime import datetime
import pandas as pd
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
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
    imie: str = Form("", description="Imię lub nazwa"),
    nazwisko: str = Form("", description="Nazwisko"),
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
        imie=imie.strip() if imie.strip() else None,
        nazwisko=nazwisko.strip() if nazwisko.strip() else None,
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
    
    # Przygotuj tytuł strony
    contact_name = ""
    if contact.imie or contact.nazwisko:
        contact_name = f"{contact.imie or ''} {contact.nazwisko or ''}".strip()
    else:
        contact_name = "Kontakt bez nazwy"
    
    return templates.TemplateResponse(
        "contacts/detail.html",
        {
            "request": request,
            "title": f"{contact_name} - Książka Telefoniczna",
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
    
    # Przygotuj tytuł strony
    contact_name = ""
    if contact.imie or contact.nazwisko:
        contact_name = f" {contact.imie or ''} {contact.nazwisko or ''}".strip()
    
    return templates.TemplateResponse(
        "contacts/edit.html",
        {
            "request": request,
            "title": f"Edytuj{contact_name} - Książka Telefoniczna",
            "contact": contact
        }
    )


@router.post("/kontakty/{contact_id}/edytuj")
async def contact_edit(
    request: Request,
    contact_id: str,
    imie: str = Form("", description="Imię lub nazwa"),
    nazwisko: str = Form("", description="Nazwisko"),
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
    contact.imie = imie.strip() if imie.strip() else None
    contact.nazwisko = nazwisko.strip() if nazwisko.strip() else None
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


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@router.get("/kontakty/export/csv")
async def export_contacts_csv(
    request: Request,
    q: Optional[str] = Query(None, description="Wyszukiwana fraza"),
    dzial: Optional[str] = Query(None, description="Filtr po dziale"),
    session: Session = Depends(get_session)
):
    """Eksport kontaktów do pliku CSV"""
    # Wymagaj zalogowania
    try:
        get_current_user(request)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Wymagane zalogowanie")
    
    # Pobierz kontakty z takimi samymi filtrami jak lista
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
    query = query.order_by(Contact.nazwisko.asc())
    
    # Pobierz kontakty
    contacts = session.exec(query).all()
    
    # Przygotuj dane do CSV
    data = []
    for contact in contacts:
        data.append({
            'Imię/Nazwa': contact.imie or '',
            'Nazwisko': contact.nazwisko or '',
            'Numer wewnętrzny': contact.numer_wewnetrzny,
            'Dział': contact.dzial or '',
            'Firma': contact.firma or '',
            'Notatki': contact.notatki or '',
            'Data utworzenia': contact.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Utwórz DataFrame i konwertuj do CSV
    df = pd.DataFrame(data)
    
    # Utwórz CSV w pamięci z poprawnym kodowaniem dla polskich znaków
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8')
    csv_content = output.getvalue()
    output.seek(0)
    
    # Przygotuj nazwę pliku
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"kontakty_{timestamp}.csv"
    
    # Zwróć plik CSV z BOM dla lepszej obsługi w Excel
    csv_bytes = '\ufeff' + csv_content  # Dodaj BOM (Byte Order Mark)
    return StreamingResponse(
        io.BytesIO(csv_bytes.encode('utf-8')),
        media_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@router.get("/kontakty/export/excel")
async def export_contacts_excel(
    request: Request,
    q: Optional[str] = Query(None, description="Wyszukiwana fraza"),
    dzial: Optional[str] = Query(None, description="Filtr po dziale"),
    session: Session = Depends(get_session)
):
    """Eksport kontaktów do pliku Excel"""
    # Wymagaj zalogowania
    try:
        get_current_user(request)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Wymagane zalogowanie")
    
    # Pobierz kontakty (taki sam kod jak w CSV)
    query = select(Contact)
    
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
    
    if dzial:
        query = query.where(Contact.dzial == dzial)
    
    query = query.order_by(Contact.nazwisko.asc())
    contacts = session.exec(query).all()
    
    # Przygotuj dane
    data = []
    for contact in contacts:
        data.append({
            'Imię/Nazwa': contact.imie or '',
            'Nazwisko': contact.nazwisko or '',
            'Numer wewnętrzny': contact.numer_wewnetrzny,
            'Dział': contact.dzial or '',
            'Firma': contact.firma or '',
            'Notatki': contact.notatki or '',
            'Data utworzenia': contact.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Utwórz DataFrame
    df = pd.DataFrame(data)
    
    # Utwórz Excel w pamięci
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Kontakty', index=False)
        
        # Dostosuj szerokość kolumn
        worksheet = writer.sheets['Kontakty']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    
    # Przygotuj nazwę pliku
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"kontakty_{timestamp}.xlsx"
    
    # Zwróć plik Excel
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@router.get("/kontakty/export/pdf")
async def export_contacts_pdf(
    request: Request,
    q: Optional[str] = Query(None, description="Wyszukiwana fraza"),
    dzial: Optional[str] = Query(None, description="Filtr po dziale"),
    session: Session = Depends(get_session)
):
    """Eksport kontaktów do pliku PDF"""
    # Wymagaj zalogowania
    try:
        get_current_user(request)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Wymagane zalogowanie")
    
    # Pobierz kontakty
    query = select(Contact)
    
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
    
    if dzial:
        query = query.where(Contact.dzial == dzial)
    
    query = query.order_by(Contact.nazwisko.asc())
    contacts = session.exec(query).all()
    
    # Utwórz PDF w pamięci z obsługą polskich znaków
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    story = []
    
    # Style
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Funkcja pomocnicza do konwersji polskich znaków na ASCII
    def polish_to_ascii(text):
        if not text:
            return ''
        replacements = {
            'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 
            'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
            'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L',
            'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
        }
        result = str(text)
        for pl, ascii_char in replacements.items():
            result = result.replace(pl, ascii_char)
        return result
    
    # Tytuł
    title_text = polish_to_ascii("Książka Telefoniczna - Lista Kontaktów")
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 20))
    
    # Informacje o filtrach
    if q or dzial:
        filter_info = "Zastosowane filtry: "
        if q:
            filter_info += f"Wyszukiwanie: '{q}' "
        if dzial:
            filter_info += f"Dzial: '{dzial}' "
        story.append(Paragraph(polish_to_ascii(filter_info), styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Przygotuj dane tabeli z konwersją polskich znaków
    table_data = [[polish_to_ascii('Imie/Nazwa'), polish_to_ascii('Nazwisko'), 'Numer wew.', polish_to_ascii('Dzial'), 'Firma']]
    
    for contact in contacts:
        table_data.append([
            polish_to_ascii(contact.imie or ''),
            polish_to_ascii(contact.nazwisko or ''), 
            contact.numer_wewnetrzny,
            polish_to_ascii(contact.dzial or ''),
            polish_to_ascii(contact.firma or '')
        ])
    
    # Utwórz tabelę
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    # Informacja o dacie generacji
    story.append(Spacer(1, 30))
    generation_date = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    story.append(Paragraph(f"Wygenerowano: {generation_date}", styles['Normal']))
    
    # Zbuduj PDF
    doc.build(story)
    output.seek(0)
    
    # Przygotuj nazwę pliku
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"kontakty_{timestamp}.pdf"
    
    # Zwróć plik PDF
    return StreamingResponse(
        output,
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )
