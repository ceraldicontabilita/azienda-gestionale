"""
API Dipendenti - Anagrafica completa, turni, documenti, libro unico
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr
import os

router = APIRouter(prefix="/api/dipendenti", tags=["Dipendenti"])


# Placeholder dependencies
async def get_current_user():
    pass

async def get_current_admin_user():
    pass

async def get_db():
    pass


# ============================================================================
# MODELS
# ============================================================================

class DipendenteBase(BaseModel):
    nome: str
    cognome: str
    codice_fiscale: str
    data_nascita: Optional[date] = None
    luogo_nascita: Optional[str] = None
    indirizzo: Optional[str] = None
    cap: Optional[str] = None
    citta: Optional[str] = None
    provincia: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None


class DipendenteCreate(DipendenteBase):
    data_assunzione: date
    tipo_contratto: str  # 'determinato', 'indeterminato'
    tipo_orario: str  # 'full-time', 'part-time'
    percentuale_part_time: Optional[Decimal] = None
    livello: str
    mansione: str
    stipendio_base: Decimal
    iban: Optional[str] = None
    banca: Optional[str] = None


class DipendenteDetail(DipendenteBase):
    id: int
    codice_dipendente: str
    data_assunzione: date
    data_cessazione: Optional[date]
    tipo_contratto: str
    tipo_orario: str
    percentuale_part_time: Optional[Decimal]
    livello: str
    mansione: str
    stipendio_base: Decimal
    iban: Optional[str]
    banca: Optional[str]
    stato: str
    
    # Statistiche aggregate
    totale_buste_paga: int
    ultima_busta_paga: Optional[str]
    ferie_residue: Decimal
    permessi_residui: Decimal
    giorni_malattia_anno: int
    
    created_at: datetime
    updated_at: datetime


class TurnoCreate(BaseModel):
    """Turno lavorativo"""
    employee_id: int
    data: date
    ora_inizio: str  # "08:00"
    ora_fine: str  # "16:00"
    tipo: str  # 'mattina', 'pomeriggio', 'sera', 'notte', 'doppio'
    reparto: Optional[str] = None  # 'sala', 'cucina', 'bar', 'cassa'
    note: Optional[str] = None


class DocumentoCreate(BaseModel):
    """Documento dipendente"""
    tipo: str  # 'contratto', 'certificato', 'privacy', 'formazione', 'altro'
    titolo: str
    descrizione: Optional[str] = None
    visibile_dipendente: bool = True


# ============================================================================
# ENDPOINTS ANAGRAFICA
# ============================================================================

@router.get("/", response_model=List[DipendenteDetail])
async def list_dipendenti(
    stato: Optional[str] = 'attivo',
    mansione: Optional[str] = None,
    search: Optional[str] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Lista dipendenti con filtri
    
    Filtri:
    - stato: 'attivo', 'cessato', 'sospeso'
    - mansione: filtra per mansione
    - search: cerca in nome, cognome, CF
    """
    
    query = """
        SELECT 
            e.*,
            COUNT(DISTINCT p.id) as totale_buste_paga,
            MAX(p.periodo) as ultima_busta_paga,
            COALESCE(MAX(p.ferie_residue), 0) as ferie_residue,
            COALESCE(MAX(p.permessi_residui), 0) as permessi_residui,
            COUNT(DISTINCT a.id) FILTER (WHERE a.tipo = 'malattia' AND EXTRACT(YEAR FROM a.data) = EXTRACT(YEAR FROM NOW())) as giorni_malattia_anno
        FROM employees e
        LEFT JOIN payslips p ON e.id = p.employee_id
        LEFT JOIN attendances a ON e.id = a.employee_id
        WHERE 1=1
    """
    params = {}
    
    if stato:
        query += " AND e.stato = :stato"
        params['stato'] = stato
    
    if mansione:
        query += " AND e.mansione = :mansione"
        params['mansione'] = mansione
    
    if search:
        query += """ AND (
            LOWER(e.nome) LIKE LOWER(:search) OR
            LOWER(e.cognome) LIKE LOWER(:search) OR
            LOWER(e.codice_fiscale) LIKE LOWER(:search)
        )"""
        params['search'] = f'%{search}%'
    
    query += " GROUP BY e.id ORDER BY e.cognome, e.nome"
    
    dipendenti = await db.fetch_all(query, params)
    
    return [DipendenteDetail(**dict(d)) for d in dipendenti]


@router.get("/{dipendente_id}", response_model=DipendenteDetail)
async def get_dipendente(
    dipendente_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Dettagli singolo dipendente con statistiche"""
    
    dipendente = await db.fetch_one("""
        SELECT 
            e.*,
            COUNT(DISTINCT p.id) as totale_buste_paga,
            MAX(p.periodo) as ultima_busta_paga,
            COALESCE(MAX(p.ferie_residue), 0) as ferie_residue,
            COALESCE(MAX(p.permessi_residui), 0) as permessi_residui,
            COUNT(DISTINCT a.id) FILTER (WHERE a.tipo = 'malattia' AND EXTRACT(YEAR FROM a.data) = EXTRACT(YEAR FROM NOW())) as giorni_malattia_anno
        FROM employees e
        LEFT JOIN payslips p ON e.id = p.employee_id
        LEFT JOIN attendances a ON e.id = a.employee_id
        WHERE e.id = :id
        GROUP BY e.id
    """, {'id': dipendente_id})
    
    if not dipendente:
        raise HTTPException(404, "Dipendente non trovato")
    
    return DipendenteDetail(**dict(dipendente))


@router.post("/", response_model=DipendenteDetail)
async def create_dipendente(
    dipendente: DipendenteCreate,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Crea nuovo dipendente"""
    
    # Verifica CF univoco
    existing = await db.fetch_one("""
        SELECT id FROM employees WHERE codice_fiscale = :cf
    """, {'cf': dipendente.codice_fiscale.upper()})
    
    if existing:
        raise HTTPException(400, "Codice fiscale già presente")
    
    # Genera codice dipendente
    last_code = await db.fetch_val("""
        SELECT codice_dipendente FROM employees
        WHERE codice_dipendente LIKE 'DIP%'
        ORDER BY id DESC LIMIT 1
    """)
    
    if last_code:
        num = int(last_code[3:]) + 1
        codice = f'DIP{num:03d}'
    else:
        codice = 'DIP001'
    
    # Crea dipendente
    dipendente_id = await db.execute("""
        INSERT INTO employees (
            codice_dipendente, nome, cognome, codice_fiscale,
            data_nascita, luogo_nascita, indirizzo, cap, citta, provincia,
            telefono, email, data_assunzione, tipo_contratto, tipo_orario,
            percentuale_part_time, livello, mansione, stipendio_base,
            iban, banca, stato
        ) VALUES (
            :codice, :nome, :cognome, :cf,
            :data_nasc, :luogo, :indirizzo, :cap, :citta, :prov,
            :tel, :email, :data_ass, :tipo_contr, :tipo_or,
            :perc, :livello, :mansione, :stipendio,
            :iban, :banca, 'attivo'
        ) RETURNING id
    """, {
        'codice': codice,
        'nome': dipendente.nome,
        'cognome': dipendente.cognome,
        'cf': dipendente.codice_fiscale.upper(),
        'data_nasc': dipendente.data_nascita,
        'luogo': dipendente.luogo_nascita,
        'indirizzo': dipendente.indirizzo,
        'cap': dipendente.cap,
        'citta': dipendente.citta,
        'prov': dipendente.provincia,
        'tel': dipendente.telefono,
        'email': dipendente.email,
        'data_ass': dipendente.data_assunzione,
        'tipo_contr': dipendente.tipo_contratto,
        'tipo_or': dipendente.tipo_orario,
        'perc': dipendente.percentuale_part_time,
        'livello': dipendente.livello,
        'mansione': dipendente.mansione,
        'stipendio': dipendente.stipendio_base,
        'iban': dipendente.iban,
        'banca': dipendente.banca
    })
    
    return await get_dipendente(dipendente_id, current_user, db)


# ============================================================================
# TURNI
# ============================================================================

@router.get("/{dipendente_id}/turni")
async def get_turni_dipendente(
    dipendente_id: int,
    data_inizio: Optional[date] = None,
    data_fine: Optional[date] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Lista turni dipendente"""
    
    query = """
        SELECT * FROM attendances
        WHERE employee_id = :emp_id
    """
    params = {'emp_id': dipendente_id}
    
    if data_inizio:
        query += " AND data >= :data_in"
        params['data_in'] = data_inizio
    
    if data_fine:
        query += " AND data <= :data_fin"
        params['data_fin'] = data_fine
    
    query += " ORDER BY data DESC"
    
    turni = await db.fetch_all(query, params)
    
    return {'success': True, 'turni': [dict(t) for t in turni]}


@router.post("/{dipendente_id}/turni")
async def create_turno(
    dipendente_id: int,
    turno: TurnoCreate,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Crea turno lavorativo"""
    
    # Verifica dipendente
    dipendente = await db.fetch_one("""
        SELECT id FROM employees WHERE id = :id AND stato = 'attivo'
    """, {'id': dipendente_id})
    
    if not dipendente:
        raise HTTPException(404, "Dipendente non trovato o non attivo")
    
    # Crea attendance
    await db.execute("""
        INSERT INTO attendances (
            employee_id, data, tipo, ore_lavorate, note
        ) VALUES (
            :emp_id, :data, 'lavoro', :ore, :note
        )
        ON CONFLICT (employee_id, data) DO UPDATE
        SET tipo = 'lavoro', ore_lavorate = :ore, note = :note
    """, {
        'emp_id': dipendente_id,
        'data': turno.data,
        'ore': 8,  # TODO: calcola da ora_inizio/ora_fine
        'note': f"{turno.tipo} - {turno.reparto or ''} - {turno.note or ''}"
    })
    
    return {'success': True, 'message': 'Turno creato'}


# ============================================================================
# DOCUMENTI
# ============================================================================

@router.get("/{dipendente_id}/documenti")
async def get_documenti_dipendente(
    dipendente_id: int,
    tipo: Optional[str] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Lista documenti dipendente"""
    
    query = """
        SELECT * FROM employee_documents
        WHERE employee_id = :emp_id
    """
    params = {'emp_id': dipendente_id}
    
    if tipo:
        query += " AND tipo = :tipo"
        params['tipo'] = tipo
    
    query += " ORDER BY created_at DESC"
    
    documenti = await db.fetch_all(query, params)
    
    return {'success': True, 'documenti': [dict(d) for d in documenti]}


@router.post("/{dipendente_id}/documenti")
async def upload_documento(
    dipendente_id: int,
    file: UploadFile = File(...),
    tipo: str = Form(...),
    titolo: str = Form(...),
    descrizione: Optional[str] = Form(None),
    visibile_dipendente: bool = Form(True),
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Upload documento per dipendente"""
    
    # Salva file
    upload_dir = f'/home/claude/azienda-cloud/backend/uploads/dipendenti/{dipendente_id}'
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, 'wb') as f:
        f.write(await file.read())
    
    # Salva in DB
    doc_id = await db.execute("""
        INSERT INTO employee_documents (
            employee_id, tipo, titolo, descrizione,
            file_path, file_size, mime_type,
            visibile_dipendente, caricato_da
        ) VALUES (
            :emp_id, :tipo, :titolo, :desc,
            :path, :size, :mime,
            :vis, :user_id
        ) RETURNING id
    """, {
        'emp_id': dipendente_id,
        'tipo': tipo,
        'titolo': titolo,
        'desc': descrizione,
        'path': file_path,
        'size': file.size,
        'mime': file.content_type,
        'vis': visibile_dipendente,
        'user_id': current_user.id
    })
    
    return {'success': True, 'documento_id': doc_id}


# ============================================================================
# STATISTICHE
# ============================================================================

@router.get("/{dipendente_id}/statistiche")
async def get_statistiche_dipendente(
    dipendente_id: int,
    anno: Optional[int] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Statistiche complete dipendente"""
    
    if not anno:
        anno = datetime.now().year
    
    stats = await db.fetch_one("""
        SELECT
            COUNT(DISTINCT a.id) FILTER (WHERE a.tipo = 'lavoro') as giorni_lavorati,
            COUNT(DISTINCT a.id) FILTER (WHERE a.tipo = 'ferie') as giorni_ferie,
            COUNT(DISTINCT a.id) FILTER (WHERE a.tipo = 'malattia') as giorni_malattia,
            COUNT(DISTINCT a.id) FILTER (WHERE a.tipo = 'permesso') as giorni_permesso,
            SUM(a.ore_lavorate) as ore_totali,
            SUM(a.ore_straordinarie) as ore_straordinarie_totali,
            COUNT(DISTINCT p.id) as buste_paga_ricevute,
            SUM(p.netto_in_busta) as totale_netto_percepito
        FROM employees e
        LEFT JOIN attendances a ON e.id = a.employee_id AND EXTRACT(YEAR FROM a.data) = :anno
        LEFT JOIN payslips p ON e.id = p.employee_id AND p.anno = :anno
        WHERE e.id = :emp_id
        GROUP BY e.id
    """, {'emp_id': dipendente_id, 'anno': anno})
    
    return {
        'success': True,
        'anno': anno,
        'statistiche': dict(stats) if stats else {}
    }


@router.get("/mansioni/statistiche")
async def get_statistiche_mansioni(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Statistiche per mansione"""
    
    stats = await db.fetch_all("""
        SELECT
            mansione,
            COUNT(*) as totale,
            COUNT(*) FILTER (WHERE stato = 'attivo') as attivi,
            AVG(stipendio_base) as stipendio_medio,
            COUNT(*) FILTER (WHERE tipo_orario = 'part-time') as part_time
        FROM employees
        GROUP BY mansione
        ORDER BY totale DESC
    """)
    
    return {
        'success': True,
        'statistiche': [dict(s) for s in stats]
    }
