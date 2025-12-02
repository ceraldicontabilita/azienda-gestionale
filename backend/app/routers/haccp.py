"""Router HACCP"""
from fastapi import APIRouter, HTTPException, Query, Form
from typing import Optional
from datetime import datetime
import logging
from app.database import get_table

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/temperature")
async def get_temperatures(id_utente: int = Query(...), tipo: Optional[str] = None):
    """Ottieni temperature (frigoriferi/congelatori)"""
    try:
        temp_table = get_table('temperature')
        query = temp_table.select('*').eq('id_utente', id_utente)
        if tipo:
            query = query.eq('tipo', tipo)
        result = query.order('data_rilevazione', desc=True).limit(100).execute()
        return {"success": True, "data": result.data if result.data else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/temperature")
async def create_temperature(
    id_utente: int = Form(...),
    tipo: str = Form(...),
    data_rilevazione: str = Form(...),
    ora_rilevazione: str = Form(...),
    temperatura: float = Form(...),
    operatore: Optional[str] = Form(None)
):
    """Registra temperatura"""
    try:
        temp_table = get_table('temperature')
        result = temp_table.insert({
            'id_utente': id_utente,
            'tipo': tipo,
            'data_rilevazione': data_rilevazione,
            'ora_rilevazione': ora_rilevazione,
            'temperatura': temperatura,
            'operatore': operatore,
            'created_at': datetime.now().isoformat()
        }).execute()
        return {"success": True, "message": "Temperatura registrata", "data": result.data[0] if result.data else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sanificazioni")
async def get_sanificazioni(id_utente: int = Query(...)):
    """Ottieni sanificazioni"""
    try:
        san_table = get_table('sanificazioni')
        result = san_table.select('*').eq('id_utente', id_utente).order('data_sanificazione', desc=True).limit(100).execute()
        return {"success": True, "data": result.data if result.data else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sanificazioni")
async def create_sanificazione(
    id_utente: int = Form(...),
    data_sanificazione: str = Form(...),
    area: str = Form(...),
    prodotto_usato: Optional[str] = Form(None),
    operatore: Optional[str] = Form(None)
):
    """Registra sanificazione"""
    try:
        san_table = get_table('sanificazioni')
        result = san_table.insert({
            'id_utente': id_utente,
            'data_sanificazione': data_sanificazione,
            'area': area,
            'prodotto_usato': prodotto_usato,
            'operatore': operatore,
            'created_at': datetime.now().isoformat()
        }).execute()
        return {"success": True, "message": "Sanificazione registrata"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/libretti-sanitari")
async def get_libretti(id_utente: int = Query(...)):
    """Ottieni libretti sanitari"""
    try:
        libretti_table = get_table('libretti_sanitari')
        result = libretti_table.select('*, dipendenti(nome, cognome)')\
            .eq('id_utente', id_utente)\
            .order('data_scadenza')\
            .execute()
        return {"success": True, "data": result.data if result.data else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
