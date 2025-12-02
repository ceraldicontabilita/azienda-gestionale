"""
Router Bonifici - CRUD Completo
"""

from fastapi import APIRouter, HTTPException, Query, Form, UploadFile, File
from typing import Optional
from datetime import datetime
import logging

from app.database import get_table

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_transfers(
    id_utente: int = Query(...),
    collegato: Optional[bool] = None,
    anno: Optional[int] = None
):
    """Ottieni lista bonifici"""
    try:
        bonifici_table = get_table('bonifici')
        query = bonifici_table.select('*').eq('id_utente', id_utente)
        
        if collegato is not None:
            query = query.eq('collegato', collegato)
        
        if anno:
            query = query.gte('data_bonifico', f'{anno}-01-01')\
                        .lte('data_bonifico', f'{anno}-12-31')
        
        result = query.order('data_bonifico', desc=True).execute()
        
        return {
            "success": True,
            "data": result.data if result.data else [],
            "total": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Errore get_transfers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_transfer(
    id_utente: int = Form(...),
    data_bonifico: str = Form(...),
    importo: float = Form(...),
    beneficiario: str = Form(...),
    causale: Optional[str] = Form(None),
    ordinante: Optional[str] = Form(None),
    id_fattura: Optional[int] = Form(None)
):
    """Crea nuovo bonifico"""
    try:
        bonifici_table = get_table('bonifici')
        
        bonifico_data = {
            'id_utente': id_utente,
            'data_bonifico': data_bonifico,
            'importo': importo,
            'beneficiario': beneficiario,
            'causale': causale,
            'ordinante': ordinante,
            'id_fattura': id_fattura,
            'collegato': bool(id_fattura),
            'created_at': datetime.now().isoformat()
        }
        
        result = bonifici_table.insert(bonifico_data).execute()
        
        if id_fattura:
            fatture_table = get_table('fatture')
            fatture_table.update({
                'metodo_pagamento': 'banca_bonifico',
                'pagata': True,
                'data_pagamento': datetime.now().isoformat()
            }).eq('id', id_fattura).eq('id_utente', id_utente).execute()
        
        return {
            "success": True,
            "message": "Bonifico registrato",
            "data": result.data[0] if result.data else None
        }
        
    except Exception as e:
        logger.error(f"Errore create_transfer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-excel")
async def import_transfers_excel(
    file: UploadFile = File(...),
    id_utente: int = Form(...)
):
    """Import bonifici da Excel"""
    try:
        import pandas as pd
        import io
        
        content = await file.read()
        df = pd.read_excel(io.BytesIO(content))
        
        required_cols = ['Data', 'Importo', 'Beneficiario']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(status_code=400, detail=f"Colonne richieste: {required_cols}")
        
        bonifici_table = get_table('bonifici')
        imported = 0
        
        for _, row in df.iterrows():
            data = pd.to_datetime(row['Data']).date().isoformat()
            importo = float(row['Importo'])
            
            if importo > 0:
                continue
            
            bonifici_table.insert({
                'id_utente': id_utente,
                'data_bonifico': data,
                'importo': abs(importo),
                'beneficiario': str(row['Beneficiario']),
                'causale': str(row.get('Causale', '')) if pd.notna(row.get('Causale')) else None,
                'collegato': False,
                'created_at': datetime.now().isoformat()
            }).execute()
            
            imported += 1
        
        return {
            "success": True,
            "message": f"Importati {imported} bonifici"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore import_transfers_excel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id_bonifico}")
async def delete_transfer(id_bonifico: int, id_utente: int = Query(...)):
    """
    Elimina bonifico con controlli
    
    Può eliminare solo se NON collegato a fattura
    """
    try:
        from app.services.relationship_service import RelationshipService
        
        # Verifica integrità
        can_delete, message = await RelationshipService.check_can_delete_bonifico(
            id_utente=id_utente,
            id_bonifico=id_bonifico
        )
        
        if not can_delete:
            raise HTTPException(status_code=400, detail=message)
        
        bonifici_table = get_table('bonifici')
        bonifici_table.delete().eq('id', id_bonifico).eq('id_utente', id_utente).execute()
        
        return {
            "success": True,
            "message": "Bonifico eliminato"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore delete_transfer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
