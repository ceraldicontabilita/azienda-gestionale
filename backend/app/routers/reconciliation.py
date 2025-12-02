"""Router Riconciliazione Bancaria"""
from fastapi import APIRouter, HTTPException, Query
import logging
from app.database import get_table

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_unreconciled(id_utente: int = Query(...)):
    """Ottieni movimenti non riconciliati"""
    try:
        banca_table = get_table('prima_nota_banca')
        result = banca_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('riconciliato', False)\
            .order('data_operazione', desc=True)\
            .execute()
        return {"success": True, "data": result.data if result.data else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match")
async def match_transaction(
    id_movimento: int = Query(...),
    id_fattura: int = Query(...),
    id_utente: int = Query(...)
):
    """Riconcilia movimento con fattura"""
    try:
        banca_table = get_table('prima_nota_banca')
        fatture_table = get_table('fatture')
        
        banca_table.update({'riconciliato': True})\
            .eq('id', id_movimento)\
            .eq('id_utente', id_utente)\
            .execute()
        
        fatture_table.update({'riconciliata': True})\
            .eq('id', id_fattura)\
            .eq('id_utente', id_utente)\
            .execute()
        
        return {"success": True, "message": "Riconciliazione completata"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
