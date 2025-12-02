"""Router IVA"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import logging
from app.database import get_table

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/liquidazione")
async def calcola_liquidazione(
    id_utente: int = Query(...),
    mese: int = Query(...),
    anno: int = Query(...)
):
    """Calcola liquidazione IVA mensile"""
    try:
        fatture_table = get_table('fatture')
        fatture_emesse_table = get_table('fatture_emesse')
        
        data_inizio = f"{anno}-{mese:02d}-01"
        if mese == 12:
            data_fine = f"{anno+1}-01-01"
        else:
            data_fine = f"{anno}-{mese+1:02d}-01"
        
        # IVA Acquisti (detraibile)
        fatture_acq = fatture_table.select('*')\
            .eq('id_utente', id_utente)\
            .gte('data_fattura', data_inizio)\
            .lt('data_fattura', data_fine)\
            .execute()
        
        iva_acquisti = sum(float(f['iva']) for f in (fatture_acq.data or []))
        
        # IVA Vendite (da versare)
        fatture_ven = fatture_emesse_table.select('*')\
            .eq('id_utente', id_utente)\
            .gte('data_fattura', data_inizio)\
            .lt('data_fattura', data_fine)\
            .execute()
        
        iva_vendite = sum(float(f['iva']) for f in (fatture_ven.data or []))
        
        # Calcolo
        iva_da_versare = iva_vendite - iva_acquisti
        
        return {
            "success": True,
            "data": {
                "mese": mese,
                "anno": anno,
                "iva_vendite": round(iva_vendite, 2),
                "iva_acquisti": round(iva_acquisti, 2),
                "iva_da_versare": round(iva_da_versare, 2),
                "tipo": "credito" if iva_da_versare < 0 else "debito"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
