"""
Router Dashboard - Statistiche e panoramica
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from app.database import get_table

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(id_utente: int = Query(...)):
    """
    Statistiche generali dashboard
    
    Returns:
        - Totale fatture mese corrente
        - Numero fornitori
        - Fatture da pagare
        - Saldo cassa
    """
    try:
        current_month = datetime.now().strftime('%Y-%m')
        
        # Totale fatture mese corrente
        fatture_table = get_table('fatture')
        fatture_mese = fatture_table.select('*')\
            .eq('id_utente', id_utente)\
            .gte('data_fattura', f'{current_month}-01')\
            .execute()
        
        totale_fatture_mese = sum(
            float(f.get('totale', 0)) 
            for f in fatture_mese.data
        ) if fatture_mese.data else 0
        
        # Numero fornitori attivi
        fornitori_table = get_table('fornitori')
        fornitori = fornitori_table.select('id')\
            .eq('id_utente', id_utente)\
            .eq('attivo', True)\
            .execute()
        
        num_fornitori = len(fornitori.data) if fornitori.data else 0
        
        # Fatture da pagare (non pagate)
        fatture_da_pagare = fatture_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('pagata', False)\
            .execute()
        
        totale_da_pagare = sum(
            float(f.get('totale', 0)) 
            for f in fatture_da_pagare.data
        ) if fatture_da_pagare.data else 0
        
        num_fatture_da_pagare = len(fatture_da_pagare.data) if fatture_da_pagare.data else 0
        
        # Saldo cassa (somma movimenti cassa)
        cassa_table = get_table('movimenti_cassa')
        movimenti_cassa = cassa_table.select('*')\
            .eq('id_utente', id_utente)\
            .execute()
        
        saldo_cassa = 0
        if movimenti_cassa.data:
            for mov in movimenti_cassa.data:
                tipo = mov.get('tipo', '')
                importo = float(mov.get('importo', 0))
                if tipo in ['corrispettivi', 'entrata']:
                    saldo_cassa += importo
                elif tipo in ['pos', 'versamento', 'uscita']:
                    saldo_cassa -= importo
        
        return {
            "success": True,
            "data": {
                "fatture_mese": {
                    "totale": round(totale_fatture_mese, 2),
                    "mese": current_month
                },
                "fornitori": {
                    "totale": num_fornitori
                },
                "fatture_da_pagare": {
                    "numero": num_fatture_da_pagare,
                    "importo": round(totale_da_pagare, 2)
                },
                "saldo_cassa": round(saldo_cassa, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Errore get_dashboard_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quick-actions")
async def get_quick_actions(id_utente: int = Query(...)):
    """Azioni rapide suggerite"""
    try:
        actions = []
        
        # Check fatture scadute
        fatture_table = get_table('fatture')
        today = datetime.now().date()
        
        fatture_scadute = fatture_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('pagata', False)\
            .lt('data_scadenza', today.isoformat())\
            .execute()
        
        if fatture_scadute.data and len(fatture_scadute.data) > 0:
            actions.append({
                "tipo": "warning",
                "titolo": f"{len(fatture_scadute.data)} fatture scadute",
                "descrizione": "Alcune fatture sono scadute e richiedono attenzione",
                "azione": "/archive?tab=attive",
                "priorita": "alta"
            })
        
        # Check libretti sanitari in scadenza (30 giorni)
        libretti_table = get_table('libretti_sanitari')
        data_limite = (today + timedelta(days=30)).isoformat()
        
        libretti_scadenza = libretti_table.select('*')\
            .eq('id_utente', id_utente)\
            .lte('data_scadenza', data_limite)\
            .execute()
        
        if libretti_scadenza.data and len(libretti_scadenza.data) > 0:
            actions.append({
                "tipo": "info",
                "titolo": f"{len(libretti_scadenza.data)} libretti in scadenza",
                "descrizione": "Libretti sanitari da rinnovare nei prossimi 30 giorni",
                "azione": "/gestione-dipendenti?tab=libretti",
                "priorita": "media"
            })
        
        # Check magazzino scorte basse
        magazzino_table = get_table('inventario')
        scorte_basse = magazzino_table.select('*')\
            .eq('id_utente', id_utente)\
            .lt('quantita', 10)\
            .execute()
        
        if scorte_basse.data and len(scorte_basse.data) > 0:
            actions.append({
                "tipo": "warning",
                "titolo": f"{len(scorte_basse.data)} prodotti in esaurimento",
                "descrizione": "Alcuni prodotti hanno scorte basse",
                "azione": "/warehouse",
                "priorita": "media"
            })
        
        return {
            "success": True,
            "data": actions
        }
        
    except Exception as e:
        logger.error(f"Errore get_quick_actions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent-activity")
async def get_recent_activity(id_utente: int = Query(...), limit: int = 10):
    """Attività recenti (ultime fatture, pagamenti, etc)"""
    try:
        activities = []
        
        # Ultime fatture caricate
        fatture_table = get_table('fatture')
        recent_fatture = fatture_table.select('*')\
            .eq('id_utente', id_utente)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        if recent_fatture.data:
            for f in recent_fatture.data:
                activities.append({
                    "tipo": "fattura",
                    "descrizione": f"Fattura {f.get('numero_fattura')} - {f.get('ragione_sociale_fornitore')}",
                    "importo": float(f.get('totale', 0)),
                    "data": f.get('created_at'),
                    "icon": "📄"
                })
        
        # Ordina per data e limita
        activities.sort(key=lambda x: x['data'], reverse=True)
        activities = activities[:limit]
        
        return {
            "success": True,
            "data": activities
        }
        
    except Exception as e:
        logger.error(f"Errore get_recent_activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
