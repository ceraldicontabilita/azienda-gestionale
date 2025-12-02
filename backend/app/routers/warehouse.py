"""Router Magazzino"""
from fastapi import APIRouter, HTTPException, Query, Form
from typing import Optional
from datetime import datetime
import logging
from app.database import get_table

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_inventory(id_utente: int = Query(...), categoria: Optional[str] = None):
    """Ottieni inventario"""
    try:
        inv_table = get_table('inventario')
        query = inv_table.select('*').eq('id_utente', id_utente)
        if categoria:
            query = query.eq('categoria', categoria)
        result = query.order('descrizione').execute()
        return {"success": True, "data": result.data if result.data else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_product(
    id_utente: int = Form(...),
    descrizione: str = Form(...),
    codice_prodotto: Optional[str] = Form(None),
    categoria: Optional[str] = Form(None),
    unita_misura: Optional[str] = Form(None),
    quantita: Optional[float] = Form(0),
    prezzo_acquisto: Optional[float] = Form(None)
):
    """Crea prodotto inventario"""
    try:
        inv_table = get_table('inventario')
        result = inv_table.insert({
            'id_utente': id_utente,
            'codice_prodotto': codice_prodotto,
            'descrizione': descrizione,
            'categoria': categoria,
            'unita_misura': unita_misura,
            'quantita': quantita,
            'prezzo_acquisto': prezzo_acquisto,
            'created_at': datetime.now().isoformat()
        }).execute()
        return {"success": True, "message": "Prodotto creato", "data": result.data[0] if result.data else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/populate-from-invoices")
async def populate_from_invoices(id_utente: int = Form(...)):
    """Popola magazzino da righe fatture"""
    try:
        righe_table = get_table('righe_fattura')
        inv_table = get_table('inventario')
        
        righe = righe_table.select('*, fatture!inner(id_utente)')\
            .eq('fatture.id_utente', id_utente)\
            .execute()
        
        if not righe.data:
            return {"success": True, "message": "Nessuna riga da importare"}
        
        imported = 0
        for riga in righe.data:
            existing = inv_table.select('*')\
                .eq('id_utente', id_utente)\
                .eq('descrizione', riga['descrizione'])\
                .execute()
            
            if not existing.data:
                inv_table.insert({
                    'id_utente': id_utente,
                    'descrizione': riga['descrizione'],
                    'prezzo_acquisto': float(riga['prezzo_unitario']),
                    'quantita': 0,
                    'created_at': datetime.now().isoformat()
                }).execute()
                imported += 1
        
        return {"success": True, "message": f"Importati {imported} prodotti"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
