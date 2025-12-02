"""
Router Prima Nota Cassa
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
import logging

from app.database import get_table

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_cash_movements(
    id_utente: int = Query(...),
    data_inizio: Optional[str] = None,
    data_fine: Optional[str] = None,
    tipo: Optional[str] = None
):
    """
    Ottieni movimenti cassa
    
    Tipi:
    - corrispettivi: Incassi giornalieri
    - pos: Pagamenti carta
    - versamento: Versamenti in banca
    - pagamento_fattura: Pagamento fornitori
    - entrata/uscita: Altro
    """
    try:
        cassa_table = get_table('movimenti_cassa')
        query = cassa_table.select('*').eq('id_utente', id_utente)
        
        if data_inizio:
            query = query.gte('data_operazione', data_inizio)
        if data_fine:
            query = query.lte('data_operazione', data_fine)
        if tipo:
            query = query.eq('tipo', tipo)
        
        result = query.order('data_operazione', desc=True).execute()
        
        return {
            "success": True,
            "data": result.data if result.data else [],
            "total": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Errore get_cash_movements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_cash_movement(
    id_utente: int = Form(...),
    data_operazione: str = Form(...),
    tipo: str = Form(...),
    importo: float = Form(...),
    descrizione: Optional[str] = Form(None),
    corrispettivi: Optional[float] = Form(None),
    pos: Optional[float] = Form(None),
    versamento: Optional[float] = Form(None)
):
    """Crea movimento cassa manuale"""
    try:
        cassa_table = get_table('movimenti_cassa')
        
        result = cassa_table.insert({
            'id_utente': id_utente,
            'data_operazione': data_operazione,
            'tipo': tipo,
            'importo': importo,
            'descrizione': descrizione,
            'corrispettivi': corrispettivi,
            'pos': pos,
            'versamento': versamento,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return {
            "success": True,
            "message": "Movimento registrato",
            "data": result.data[0] if result.data else None
        }
        
    except Exception as e:
        logger.error(f"Errore create_cash_movement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chiusura-giornaliera")
async def create_daily_closure(
    id_utente: int = Form(...),
    data: str = Form(...),
    corrispettivi: float = Form(default=0),
    pos: float = Form(default=0),
    versamento: float = Form(default=0),
    note: Optional[str] = Form(None)
):
    """
    Registra chiusura giornaliera
    
    Calcolo saldo: Corrispettivi - POS - Versamenti
    """
    try:
        saldo = corrispettivi - pos - versamento
        
        cassa_table = get_table('movimenti_cassa')
        
        # Corrispettivi
        if corrispettivi > 0:
            cassa_table.insert({
                'id_utente': id_utente,
                'data_operazione': data,
                'tipo': 'corrispettivi',
                'importo': corrispettivi,
                'descrizione': f"Corrispettivi giornalieri {data}",
                'corrispettivi': corrispettivi,
                'note': note,
                'created_at': datetime.now().isoformat()
            }).execute()
        
        # POS
        if pos > 0:
            cassa_table.insert({
                'id_utente': id_utente,
                'data_operazione': data,
                'tipo': 'pos',
                'importo': -pos,
                'descrizione': f"Pagamenti POS {data}",
                'pos': pos,
                'note': note,
                'created_at': datetime.now().isoformat()
            }).execute()
        
        # Versamento
        if versamento > 0:
            cassa_table.insert({
                'id_utente': id_utente,
                'data_operazione': data,
                'tipo': 'versamento',
                'importo': -versamento,
                'descrizione': f"Versamento in banca {data}",
                'versamento': versamento,
                'note': note,
                'created_at': datetime.now().isoformat()
            }).execute()
        
        return {
            "success": True,
            "message": "Chiusura giornaliera registrata",
            "saldo_cassa": round(saldo, 2)
        }
        
    except Exception as e:
        logger.error(f"Errore create_daily_closure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/saldo")
async def get_cash_balance(
    id_utente: int = Query(...),
    data_fino_a: Optional[str] = None
):
    """
    Calcola saldo cassa
    
    Somma tutti i movimenti:
    + Entrate (corrispettivi, entrate)
    - Uscite (pos, versamenti, pagamento_fattura, uscite)
    """
    try:
        cassa_table = get_table('movimenti_cassa')
        query = cassa_table.select('*').eq('id_utente', id_utente)
        
        if data_fino_a:
            query = query.lte('data_operazione', data_fino_a)
        
        result = query.execute()
        
        saldo = 0
        if result.data:
            for mov in result.data:
                saldo += float(mov['importo'])
        
        return {
            "success": True,
            "saldo": round(saldo, 2),
            "data_calcolo": data_fino_a or datetime.now().date().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Errore get_cash_balance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-corrispettivi")
async def import_corrispettivi(
    file: UploadFile = File(...),
    id_utente: int = Form(...)
):
    """
    Import corrispettivi da Excel
    
    Formato Excel:
    Data | Importo | Descrizione
    """
    try:
        import pandas as pd
        import io
        
        # Leggi Excel
        content = await file.read()
        df = pd.read_excel(io.BytesIO(content))
        
        # Valida colonne
        required_cols = ['Data', 'Importo']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(status_code=400, detail=f"Colonne richieste: {required_cols}")
        
        cassa_table = get_table('movimenti_cassa')
        imported = 0
        
        for _, row in df.iterrows():
            data = pd.to_datetime(row['Data']).date().isoformat()
            importo = float(row['Importo'])
            descrizione = row.get('Descrizione', f"Corrispettivi {data}")
            
            cassa_table.insert({
                'id_utente': id_utente,
                'data_operazione': data,
                'tipo': 'corrispettivi',
                'importo': importo,
                'descrizione': descrizione,
                'corrispettivi': importo,
                'created_at': datetime.now().isoformat()
            }).execute()
            
            imported += 1
        
        return {
            "success": True,
            "message": f"Importati {imported} corrispettivi"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore import_corrispettivi: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-pos")
async def import_pos(
    file: UploadFile = File(...),
    id_utente: int = Form(...)
):
    """Import transazioni POS da Excel"""
    try:
        import pandas as pd
        import io
        
        content = await file.read()
        df = pd.read_excel(io.BytesIO(content))
        
        required_cols = ['Data', 'Importo']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(status_code=400, detail=f"Colonne richieste: {required_cols}")
        
        cassa_table = get_table('movimenti_cassa')
        imported = 0
        
        for _, row in df.iterrows():
            data = pd.to_datetime(row['Data']).date().isoformat()
            importo = float(row['Importo'])
            
            cassa_table.insert({
                'id_utente': id_utente,
                'data_operazione': data,
                'tipo': 'pos',
                'importo': -importo,  # Negativo perché esce dalla cassa
                'descrizione': f"POS {data}",
                'pos': importo,
                'created_at': datetime.now().isoformat()
            }).execute()
            
            imported += 1
        
        return {
            "success": True,
            "message": f"Importate {imported} transazioni POS"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore import_pos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id_movimento}")
async def delete_cash_movement(id_movimento: int, id_utente: int = Query(...)):
    """Elimina movimento cassa"""
    try:
        cassa_table = get_table('movimenti_cassa')
        
        cassa_table.delete()\
            .eq('id', id_movimento)\
            .eq('id_utente', id_utente)\
            .execute()
        
        return {
            "success": True,
            "message": "Movimento eliminato"
        }
        
    except Exception as e:
        logger.error(f"Errore delete_cash_movement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
