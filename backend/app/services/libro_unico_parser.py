"""
Parser LibroUnico Zucchetti - Import presenze
"""
try:
    import PyPDF2
    from io import BytesIO
except ImportError:
    PyPDF2 = None
    BytesIO = None
    
import re
from datetime import datetime, date
from typing import List, Dict
from decimal import Decimal


class LibroUnicoParser:
    """Parser per file LibroUnico Zucchetti"""
    
    def __init__(self):
        self.giustificativi_map = {
            'FE': 'ferie',
            'MA': 'malattia',
            'AI': 'assenza_ingiustificata',
            'AH': 'assenza_autorizzata',
            'PE': 'permesso',
            'FP': 'festivita',
            'RP': 'riposo',
            'ROL': 'permesso'
        }
    
    def parse_pdf(self, pdf_data: bytes) -> List[Dict]:
        """
        Parse PDF LibroUnico
        
        Returns lista presenze:
        [
            {
                'codice_fiscale': 'ABC...',
                'nome': 'Mario',
                'cognome': 'Rossi',
                'data': date(2025, 3, 1),
                'tipo': 'lavoro',
                'ore_lavorate': 8,
                'ore_straordinarie': 0,
                'codice_giustificativo': None,
                'descrizione': ''
            },
            ...
        ]
        """
        
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            presenze = self._extract_attendances(text)
            
            return presenze
            
        except Exception as e:
            print(f"Errore parsing LibroUnico: {e}")
            return []
    
    def _extract_attendances(self, text: str) -> List[Dict]:
        """Estrai presenze dal testo"""
        
        presenze = []
        
        # Identifica dipendente
        cf_match = re.search(r'\b([A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z])\b', text)
        if not cf_match:
            return presenze
        
        codice_fiscale = cf_match.group(1)
        
        # Nome cognome
        name_match = re.search(r'(?:COGNOME.*NOME)\s*([A-Z\s]+)', text)
        if name_match:
            full_name = name_match.group(1).strip()
            parts = full_name.split()
            cognome = parts[0] if parts else ''
            nome = ' '.join(parts[1:]) if len(parts) > 1 else ''
        else:
            cognome = ''
            nome = ''
        
        # Mese/Anno
        periodo_match = re.search(
            r'(Gennaio|Febbraio|Marzo|Aprile|Maggio|Giugno|Luglio|Agosto|Settembre|Ottobre|Novembre|Dicembre)\s+(\d{4})',
            text
        )
        
        if not periodo_match:
            return presenze
        
        mese_nome = periodo_match.group(1)
        anno = int(periodo_match.group(2))
        
        mesi = {
            'Gennaio': 1, 'Febbraio': 2, 'Marzo': 3, 'Aprile': 4,
            'Maggio': 5, 'Giugno': 6, 'Luglio': 7, 'Agosto': 8,
            'Settembre': 9, 'Ottobre': 10, 'Novembre': 11, 'Dicembre': 12
        }
        
        mese = mesi[mese_nome]
        
        # Tabella presenze (cerca pattern giorno + ore/giustificativo)
        # Esempio: "01 8:00 - - FE"
        
        lines = text.split('\n')
        
        for line in lines:
            # Pattern: giorno numero
            day_match = re.search(r'\b(\d{1,2})\b', line)
            
            if not day_match:
                continue
            
            giorno = int(day_match.group(1))
            
            if giorno < 1 or giorno > 31:
                continue
            
            try:
                data_presenza = date(anno, mese, giorno)
            except ValueError:
                continue
            
            # Cerca ore lavorate
            ore_match = re.search(r'(\d{1,2}):(\d{2})', line)
            
            # Cerca giustificativi
            giust_match = re.search(r'\b(FE|MA|AI|AH|PE|FP|RP|ROL)\b', line)
            
            if ore_match:
                # Lavoro normale
                ore = int(ore_match.group(1))
                minuti = int(ore_match.group(2))
                
                ore_lavorate = Decimal(ore) + Decimal(minuti) / Decimal(60)
                
                # Cerca straordinari
                ore_str_match = re.search(r'STR\s+(\d{1,2}):(\d{2})', line)
                
                ore_straordinarie = Decimal('0')
                if ore_str_match:
                    ore_str = int(ore_str_match.group(1))
                    min_str = int(ore_str_match.group(2))
                    ore_straordinarie = Decimal(ore_str) + Decimal(min_str) / Decimal(60)
                
                presenze.append({
                    'codice_fiscale': codice_fiscale,
                    'nome': nome,
                    'cognome': cognome,
                    'data': data_presenza,
                    'tipo': 'lavoro',
                    'ore_lavorate': ore_lavorate,
                    'ore_straordinarie': ore_straordinarie,
                    'codice_giustificativo': None,
                    'descrizione_giustificativo': ''
                })
            
            elif giust_match:
                # Assenza giustificata
                codice = giust_match.group(1)
                tipo = self.giustificativi_map.get(codice, 'altro')
                
                presenze.append({
                    'codice_fiscale': codice_fiscale,
                    'nome': nome,
                    'cognome': cognome,
                    'data': data_presenza,
                    'tipo': tipo,
                    'ore_lavorate': Decimal('0'),
                    'ore_straordinarie': Decimal('0'),
                    'codice_giustificativo': codice,
                    'descrizione_giustificativo': self._get_giustificativo_desc(codice)
                })
        
        return presenze
    
    def _get_giustificativo_desc(self, codice: str) -> str:
        """Descrizione giustificativo"""
        
        descrizioni = {
            'FE': 'Ferie',
            'MA': 'Malattia',
            'AI': 'Assenza ingiustificata',
            'AH': 'Assenza autorizzata',
            'PE': 'Permesso',
            'FP': 'Festività',
            'RP': 'Riposo',
            'ROL': 'Riduzione Orario Lavoro'
        }
        
        return descrizioni.get(codice, codice)


# ============================================================================
# SERVICE - Import presenze
# ============================================================================

async def import_libro_unico(pdf_data: bytes, db) -> Dict:
    """
    Import presenze da LibroUnico
    
    1. Parse PDF
    2. Trova dipendente per CF
    3. Inserisci/Aggiorna presenze
    """
    
    parser = LibroUnicoParser()
    presenze = parser.parse_pdf(pdf_data)
    
    if not presenze:
        return {
            'success': False,
            'error': 'Nessuna presenza trovata nel PDF'
        }
    
    imported = 0
    updated = 0
    errors = []
    
    for presenza in presenze:
        try:
            # Trova dipendente
            employee = await db.fetch_one("""
                SELECT id FROM employees
                WHERE codice_fiscale = :cf
            """, {'cf': presenza['codice_fiscale']})
            
            if not employee:
                errors.append(f"Dipendente non trovato: {presenza['codice_fiscale']}")
                continue
            
            # Inserisci/Aggiorna presenza
            existing = await db.fetch_one("""
                SELECT id FROM attendances
                WHERE employee_id = :emp_id AND data = :data
            """, {
                'emp_id': employee['id'],
                'data': presenza['data']
            })
            
            if existing:
                # Aggiorna
                await db.execute("""
                    UPDATE attendances
                    SET tipo = :tipo,
                        ore_lavorate = :ore,
                        ore_straordinarie = :ore_str,
                        codice_giustificativo = :cod_giust,
                        descrizione_giustificativo = :desc_giust
                    WHERE id = :id
                """, {
                    'id': existing['id'],
                    'tipo': presenza['tipo'],
                    'ore': presenza['ore_lavorate'],
                    'ore_str': presenza['ore_straordinarie'],
                    'cod_giust': presenza['codice_giustificativo'],
                    'desc_giust': presenza['descrizione_giustificativo']
                })
                updated += 1
            else:
                # Inserisci
                await db.execute("""
                    INSERT INTO attendances (
                        employee_id, data, tipo,
                        ore_lavorate, ore_straordinarie,
                        codice_giustificativo, descrizione_giustificativo
                    ) VALUES (
                        :emp_id, :data, :tipo,
                        :ore, :ore_str,
                        :cod_giust, :desc_giust
                    )
                """, {
                    'emp_id': employee['id'],
                    'data': presenza['data'],
                    'tipo': presenza['tipo'],
                    'ore': presenza['ore_lavorate'],
                    'ore_str': presenza['ore_straordinarie'],
                    'cod_giust': presenza['codice_giustificativo'],
                    'desc_giust': presenza['descrizione_giustificativo']
                })
                imported += 1
        
        except Exception as e:
            errors.append(f"Errore presenza {presenza['data']}: {str(e)}")
    
    return {
        'success': True,
        'imported': imported,
        'updated': updated,
        'total': len(presenze),
        'errors': errors
    }


# API Endpoint
from fastapi import APIRouter, UploadFile, File

router = APIRouter(prefix="/api/presenze", tags=["Presenze"])

@router.post("/import-libro-unico")
async def import_libro_unico_endpoint(
    file: UploadFile = File(...),
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Import presenze da LibroUnico PDF"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Solo PDF accettati")
    
    pdf_data = await file.read()
    
    result = await import_libro_unico(pdf_data, db)
    
    return result
