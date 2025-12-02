"""
Router Gestione Assegni
"""

from fastapi import APIRouter, HTTPException, Query, Form
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import logging

from app.database import get_table

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_checks(
    id_utente: int = Query(...),
    stato: Optional[str] = None
):
    """
    Ottieni lista assegni
    
    Stati:
    - disponibile: Assegni pronti da emettere
    - emesso: Assegni compilati e consegnati
    - incassato: Assegni incassati
    - annullato: Assegni annullati
    """
    try:
        assegni_table = get_table('assegni')
        query = assegni_table.select('*').eq('id_utente', id_utente)
        
        if stato:
            query = query.eq('stato', stato)
        
        result = query.order('numero').execute()
        
        return {
            "success": True,
            "data": result.data if result.data else [],
            "total": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Errore get_checks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_check(
    id_utente: int = Form(...),
    numero: str = Form(...),
    banca: str = Form(...),
    stato: str = Form(default="disponibile")
):
    """
    Crea nuovo assegno (carnet)
    Stato iniziale: disponibile
    """
    try:
        assegni_table = get_table('assegni')
        
        # Verifica duplicati
        existing = assegni_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('numero', numero)\
            .execute()
        
        if existing.data:
            raise HTTPException(status_code=400, detail="Numero assegno già esistente")
        
        result = assegni_table.insert({
            'id_utente': id_utente,
            'numero': numero,
            'banca': banca,
            'stato': stato,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return {
            "success": True,
            "message": "Assegno creato",
            "data": result.data[0] if result.data else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore create_check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-create")
async def batch_create_checks(
    id_utente: int = Form(...),
    banca: str = Form(...),
    numero_inizio: int = Form(...),
    quantita: int = Form(...)
):
    """
    Crea carnet assegni in blocco
    
    Es: numero_inizio=1001, quantita=25 → crea assegni 1001-1025
    """
    try:
        if quantita > 100:
            raise HTTPException(status_code=400, detail="Massimo 100 assegni per volta")
        
        assegni_table = get_table('assegni')
        created = []
        
        for i in range(quantita):
            numero = str(numero_inizio + i)
            
            assegni_table.insert({
                'id_utente': id_utente,
                'numero': numero,
                'banca': banca,
                'stato': 'disponibile',
                'created_at': datetime.now().isoformat()
            }).execute()
            
            created.append(numero)
        
        return {
            "success": True,
            "message": f"Creati {quantita} assegni",
            "created": created
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore batch_create_checks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id_assegno}")
async def update_check(
    id_assegno: int,
    id_utente: int = Query(...),
    stato: Optional[str] = Form(None),
    data_emissione: Optional[str] = Form(None),
    importo: Optional[float] = Form(None),
    beneficiario: Optional[str] = Form(None),
    data_incasso: Optional[str] = Form(None),
    note: Optional[str] = Form(None)
):
    """Aggiorna assegno"""
    try:
        assegni_table = get_table('assegni')
        
        update_data = {}
        if stato: update_data['stato'] = stato
        if data_emissione: update_data['data_emissione'] = data_emissione
        if importo: update_data['importo'] = importo
        if beneficiario: update_data['beneficiario'] = beneficiario
        if data_incasso: update_data['data_incasso'] = data_incasso
        if note: update_data['note'] = note
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Nessun campo da aggiornare")
        
        result = assegni_table.update(update_data)\
            .eq('id', id_assegno)\
            .eq('id_utente', id_utente)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Assegno non trovato")
        
        return {
            "success": True,
            "message": "Assegno aggiornato",
            "data": result.data[0] if result.data else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore update_check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{id_assegno}/mark-incassato")
async def mark_check_cashed(
    id_assegno: int,
    id_utente: int = Query(...),
    data_incasso: Optional[str] = Form(None)
):
    """Segna assegno come incassato"""
    try:
        assegni_table = get_table('assegni')
        
        result = assegni_table.update({
            'stato': 'incassato',
            'data_incasso': data_incasso or datetime.now().date().isoformat()
        })\
        .eq('id', id_assegno)\
        .eq('id_utente', id_utente)\
        .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Assegno non trovato")
        
        return {
            "success": True,
            "message": "Assegno segnato come incassato"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore mark_check_cashed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id_assegno}")
async def delete_check(id_assegno: int, id_utente: int = Query(...)):
    """
    Elimina assegno con controlli di integrità
    
    Può eliminare solo se stato = 'disponibile'
    Non può eliminare assegni emessi/incassati
    """
    try:
        from app.services.relationship_service import RelationshipService
        
        result = await RelationshipService.delete_assegno_safe(
            id_utente=id_utente,
            id_assegno=id_assegno
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Errore delete_check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_checks_stats(id_utente: int = Query(...)):
    """Statistiche assegni"""
    try:
        assegni_table = get_table('assegni')
        result = assegni_table.select('*').eq('id_utente', id_utente).execute()
        
        if not result.data:
            return {
                "success": True,
                "data": {
                    "totale": 0,
                    "disponibili": 0,
                    "emessi": 0,
                    "incassati": 0,
                    "annullati": 0
                }
            }
        
        stats = {
            "totale": len(result.data),
            "disponibili": len([a for a in result.data if a['stato'] == 'disponibile']),
            "emessi": len([a for a in result.data if a['stato'] == 'emesso']),
            "incassati": len([a for a in result.data if a['stato'] == 'incassato']),
            "annullati": len([a for a in result.data if a['stato'] == 'annullato'])
        }
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Errore get_checks_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
