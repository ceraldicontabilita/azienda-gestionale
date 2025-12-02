"""
Gestione Bonifici Bancari
- Import da file XLS banca
- Riconciliazione con debiti dipendenti
- Riconciliazione con debiti fornitori
- Storico bonifici
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel
import pandas as pd
import openpyxl

router = APIRouter(prefix="/api/bonifici", tags=["Bonifici"])


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

class BonificoCreate(BaseModel):
    """Crea bonifico manualmente"""
    data_bonifico: date
    beneficiario: str
    iban_beneficiario: str
    importo: Decimal
    causale: str
    tipo: str  # 'dipendente', 'fornitore', 'altro'
    riferimento_id: Optional[int] = None  # ID payslip o fornitore


class BonificoDetail(BaseModel):
    """Dettaglio bonifico"""
    id: int
    data_bonifico: date
    beneficiario: str
    iban_beneficiario: str
    importo: Decimal
    causale: str
    tipo: str
    
    # Riconciliazione
    riconciliato: bool
    data_riconciliazione: Optional[datetime]
    payslip_id: Optional[int]
    fornitore_id: Optional[int]
    
    # Import
    file_import_path: Optional[str]
    
    created_at: datetime


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/import-xls")
async def import_bonifici_xls(
    file: UploadFile = File(...),
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """
    Import bonifici da file XLS banca
    
    Formato atteso (Unicredit/Intesa):
    - Colonna "Data" o "Data Valuta"
    - Colonna "Beneficiario"
    - Colonna "IBAN" o "Conto Beneficiario"
    - Colonna "Importo" o "Dare/Avere"
    - Colonna "Causale" o "Descrizione"
    """
    
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(400, "Solo file XLS/XLSX accettati")
    
    # Leggi file
    content = await file.read()
    
    # Salva file
    upload_dir = '/home/claude/azienda-cloud/backend/uploads/bonifici'
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Parse Excel
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise HTTPException(400, f"Errore lettura Excel: {str(e)}")
    
    # Identifica colonne
    col_data = None
    col_beneficiario = None
    col_iban = None
    col_importo = None
    col_causale = None
    
    for col in df.columns:
        col_lower = col.lower()
        
        if 'data' in col_lower and not col_data:
            col_data = col
        elif 'beneficiario' in col_lower or 'destinatario' in col_lower:
            col_beneficiario = col
        elif 'iban' in col_lower or 'conto' in col_lower:
            col_iban = col
        elif 'importo' in col_lower or 'dare' in col_lower or 'avere' in col_lower:
            col_importo = col
        elif 'causale' in col_lower or 'descrizione' in col_lower:
            col_causale = col
    
    if not all([col_data, col_beneficiario, col_importo]):
        raise HTTPException(400, "Colonne obbligatorie non trovate (Data, Beneficiario, Importo)")
    
    # Import bonifici
    imported = 0
    skipped = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            data_bonifico = pd.to_datetime(row[col_data]).date()
            beneficiario = str(row[col_beneficiario])
            importo = Decimal(str(row[col_importo]).replace(',', '.'))
            
            # Solo uscite (bonifici)
            if importo >= 0:
                skipped += 1
                continue
            
            importo = abs(importo)
            
            iban = str(row[col_iban]) if col_iban and pd.notna(row[col_iban]) else None
            causale = str(row[col_causale]) if col_causale and pd.notna(row[col_causale]) else ''
            
            # Verifica se esiste già
            existing = await db.fetch_one("""
                SELECT id FROM bonifici
                WHERE data_bonifico = :data
                AND beneficiario = :benef
                AND importo = :importo
            """, {
                'data': data_bonifico,
                'benef': beneficiario,
                'importo': importo
            })
            
            if existing:
                skipped += 1
                continue
            
            # Identifica tipo (dipendente o fornitore)
            tipo = 'altro'
            riferimento_id = None
            
            # Cerca dipendente per nome
            dipendente = await db.fetch_one("""
                SELECT id FROM employees
                WHERE LOWER(CONCAT(nome, ' ', cognome)) = LOWER(:nome)
                OR LOWER(CONCAT(cognome, ' ', nome)) = LOWER(:nome)
                LIMIT 1
            """, {'nome': beneficiario.strip()})
            
            if dipendente:
                tipo = 'dipendente'
                riferimento_id = dipendente['id']
            else:
                # Cerca fornitore
                fornitore = await db.fetch_one("""
                    SELECT id FROM fornitori
                    WHERE LOWER(ragione_sociale) = LOWER(:nome)
                    LIMIT 1
                """, {'nome': beneficiario.strip()})
                
                if fornitore:
                    tipo = 'fornitore'
                    riferimento_id = fornitore['id']
            
            # Inserisci bonifico
            await db.execute("""
                INSERT INTO bonifici (
                    data_bonifico, beneficiario, iban_beneficiario,
                    importo, causale, tipo, riferimento_id,
                    file_import_path, riconciliato
                ) VALUES (
                    :data, :benef, :iban,
                    :importo, :causale, :tipo, :rif,
                    :file, false
                )
            """, {
                'data': data_bonifico,
                'benef': beneficiario,
                'iban': iban,
                'importo': importo,
                'causale': causale,
                'tipo': tipo,
                'rif': riferimento_id,
                'file': file_path
            })
            
            imported += 1
            
        except Exception as e:
            errors.append(f"Riga {idx + 2}: {str(e)}")
            skipped += 1
    
    return {
        'success': True,
        'imported': imported,
        'skipped': skipped,
        'errors': errors
    }


@router.get("/")
async def list_bonifici(
    data_da: Optional[date] = None,
    data_a: Optional[date] = None,
    tipo: Optional[str] = None,
    riconciliato: Optional[bool] = None,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Lista bonifici con filtri"""
    
    query = "SELECT * FROM bonifici WHERE 1=1"
    params = {}
    
    if data_da:
        query += " AND data_bonifico >= :data_da"
        params['data_da'] = data_da
    
    if data_a:
        query += " AND data_bonifico <= :data_a"
        params['data_a'] = data_a
    
    if tipo:
        query += " AND tipo = :tipo"
        params['tipo'] = tipo
    
    if riconciliato is not None:
        query += " AND riconciliato = :ric"
        params['ric'] = riconciliato
    
    query += " ORDER BY data_bonifico DESC LIMIT :limit"
    params['limit'] = limit
    
    bonifici = await db.fetch_all(query, params)
    
    return {
        'success': True,
        'bonifici': [dict(b) for b in bonifici]
    }


@router.post("/{bonifico_id}/riconcilia")
async def riconcilia_bonifico(
    bonifico_id: int,
    tipo_riconciliazione: str,  # 'payslip', 'fornitore'
    riferimento_id: int,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """
    Riconcilia bonifico con payslip o fornitore
    
    Se payslip: marca busta paga come pagata
    Se fornitore: marca fattura come pagata
    """
    
    bonifico = await db.fetch_one("""
        SELECT * FROM bonifici WHERE id = :id
    """, {'id': bonifico_id})
    
    if not bonifico:
        raise HTTPException(404, "Bonifico non trovato")
    
    if bonifico['riconciliato']:
        raise HTTPException(400, "Bonifico già riconciliato")
    
    # RICONCILIAZIONE PAYSLIP
    if tipo_riconciliazione == 'payslip':
        payslip = await db.fetch_one("""
            SELECT * FROM payslips WHERE id = :id
        """, {'id': riferimento_id})
        
        if not payslip:
            raise HTTPException(404, "Busta paga non trovata")
        
        # Verifica importo
        if abs(bonifico['importo'] - payslip['netto_in_busta']) > Decimal('1.0'):
            return {
                'success': False,
                'message': f"Importo non corrispondente: Bonifico €{bonifico['importo']}, Netto €{payslip['netto_in_busta']}"
            }
        
        # Marca payslip come pagata
        await db.execute("""
            UPDATE payslips
            SET stato_pagamento = 'pagato',
                data_pagamento = :data,
                movimento_bancario_id = :bonifico_id
            WHERE id = :id
        """, {
            'id': riferimento_id,
            'data': bonifico['data_bonifico'],
            'bonifico_id': bonifico_id
        })
        
        # Marca bonifico come riconciliato
        await db.execute("""
            UPDATE bonifici
            SET riconciliato = true,
                data_riconciliazione = NOW(),
                payslip_id = :payslip_id
            WHERE id = :id
        """, {
            'id': bonifico_id,
            'payslip_id': riferimento_id
        })
        
        return {
            'success': True,
            'message': 'Bonifico riconciliato con busta paga'
        }
    
    # RICONCILIAZIONE FORNITORE
    elif tipo_riconciliazione == 'fornitore':
        fornitore = await db.fetch_one("""
            SELECT * FROM fornitori WHERE id = :id
        """, {'id': riferimento_id})
        
        if not fornitore:
            raise HTTPException(404, "Fornitore non trovato")
        
        # TODO: Marca fattura come pagata
        
        # Marca bonifico come riconciliato
        await db.execute("""
            UPDATE bonifici
            SET riconciliato = true,
                data_riconciliazione = NOW(),
                fornitore_id = :forn_id
            WHERE id = :id
        """, {
            'id': bonifico_id,
            'forn_id': riferimento_id
        })
        
        return {
            'success': True,
            'message': 'Bonifico riconciliato con fornitore'
        }
    
    else:
        raise HTTPException(400, "Tipo riconciliazione non valido")


@router.get("/da-riconciliare")
async def bonifici_da_riconciliare(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Lista bonifici da riconciliare"""
    
    bonifici = await db.fetch_all("""
        SELECT * FROM bonifici
        WHERE riconciliato = false
        ORDER BY data_bonifico DESC
    """)
    
    # Per ogni bonifico, cerca possibili match
    risultati = []
    
    for bonifico in bonifici:
        matches = []
        
        # Se tipo dipendente, cerca buste paga
        if bonifico['tipo'] == 'dipendente' and bonifico['riferimento_id']:
            payslips = await db.fetch_all("""
                SELECT p.*, e.nome, e.cognome
                FROM payslips p
                JOIN employees e ON p.employee_id = e.id
                WHERE e.id = :emp_id
                AND p.stato_pagamento = 'da_pagare'
                AND ABS(p.netto_in_busta - :importo) < 10
                ORDER BY p.periodo DESC
                LIMIT 3
            """, {
                'emp_id': bonifico['riferimento_id'],
                'importo': bonifico['importo']
            })
            
            for ps in payslips:
                matches.append({
                    'tipo': 'payslip',
                    'id': ps['id'],
                    'descrizione': f"Busta paga {ps['periodo']} - {ps['nome']} {ps['cognome']}",
                    'importo': float(ps['netto_in_busta']),
                    'differenza': float(abs(ps['netto_in_busta'] - bonifico['importo']))
                })
        
        risultati.append({
            'bonifico': dict(bonifico),
            'possibili_match': matches
        })
    
    return {
        'success': True,
        'bonifici_da_riconciliare': len(bonifici),
        'risultati': risultati
    }


@router.get("/statistiche")
async def statistiche_bonifici(
    anno: Optional[int] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Statistiche bonifici"""
    
    if not anno:
        anno = datetime.now().year
    
    stats = await db.fetch_one("""
        SELECT
            COUNT(*) as totale_bonifici,
            SUM(importo) as totale_importo,
            COUNT(*) FILTER (WHERE tipo = 'dipendente') as bonifici_dipendenti,
            SUM(importo) FILTER (WHERE tipo = 'dipendente') as importo_dipendenti,
            COUNT(*) FILTER (WHERE tipo = 'fornitore') as bonifici_fornitori,
            SUM(importo) FILTER (WHERE tipo = 'fornitore') as importo_fornitori,
            COUNT(*) FILTER (WHERE riconciliato = false) as da_riconciliare
        FROM bonifici
        WHERE EXTRACT(YEAR FROM data_bonifico) = :anno
    """, {'anno': anno})
    
    return {
        'success': True,
        'anno': anno,
        'statistiche': dict(stats) if stats else {}
    }
