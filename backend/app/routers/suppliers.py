"""
Router Fornitori - CRUD Completo
"""

from fastapi import APIRouter, HTTPException, Query, Form
from typing import Optional
from datetime import datetime
import logging

from app.database import get_table

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_suppliers(
    id_utente: int = Query(...),
    attivo: Optional[bool] = None,
    metodo_pagamento: Optional[str] = None
):
    """
    Ottieni lista fornitori
    
    Filtri:
    - attivo: true/false
    - metodo_pagamento: banca, cassa, assegno, misto
    """
    try:
        fornitori_table = get_table('fornitori')
        query = fornitori_table.select('*').eq('id_utente', id_utente)
        
        if attivo is not None:
            query = query.eq('attivo', attivo)
        if metodo_pagamento:
            query = query.eq('metodo_pagamento', metodo_pagamento)
        
        result = query.order('ragione_sociale').execute()
        
        return {
            "success": True,
            "data": result.data if result.data else [],
            "total": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Errore get_suppliers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{partita_iva}")
async def get_supplier(partita_iva: str, id_utente: int = Query(...)):
    """Ottieni fornitore per P.IVA"""
    try:
        fornitori_table = get_table('fornitori')
        
        result = fornitori_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('partita_iva', partita_iva)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Fornitore non trovato")
        
        return {
            "success": True,
            "data": result.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore get_supplier: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_supplier(
    id_utente: int = Form(...),
    partita_iva: str = Form(...),
    ragione_sociale: str = Form(...),
    codice_fiscale: Optional[str] = Form(None),
    indirizzo: Optional[str] = Form(None),
    cap: Optional[str] = Form(None),
    citta: Optional[str] = Form(None),
    provincia: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None),
    pec: Optional[str] = Form(None),
    codice_sdi: Optional[str] = Form(None),
    metodo_pagamento: Optional[str] = Form(None),
    iban: Optional[str] = Form(None),
    banca: Optional[str] = Form(None),
    note: Optional[str] = Form(None)
):
    """
    Crea nuovo fornitore
    
    Metodi pagamento: banca, cassa, assegno, misto
    """
    try:
        # Verifica duplicati
        fornitori_table = get_table('fornitori')
        existing = fornitori_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('partita_iva', partita_iva)\
            .execute()
        
        if existing.data:
            raise HTTPException(status_code=400, detail="Fornitore già esistente")
        
        # Valida P.IVA (11 cifre)
        if len(partita_iva) != 11 or not partita_iva.isdigit():
            raise HTTPException(status_code=400, detail="Partita IVA non valida (deve essere 11 cifre)")
        
        fornitore_data = {
            'id_utente': id_utente,
            'partita_iva': partita_iva,
            'ragione_sociale': ragione_sociale,
            'codice_fiscale': codice_fiscale,
            'indirizzo': indirizzo,
            'cap': cap,
            'citta': citta,
            'provincia': provincia,
            'email': email,
            'telefono': telefono,
            'pec': pec,
            'codice_sdi': codice_sdi,
            'metodo_pagamento': metodo_pagamento,
            'iban': iban,
            'banca': banca,
            'note': note,
            'attivo': True,
            'created_at': datetime.now().isoformat()
        }
        
        result = fornitori_table.insert(fornitore_data).execute()
        
        return {
            "success": True,
            "message": "Fornitore creato",
            "data": result.data[0] if result.data else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore create_supplier: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{partita_iva}")
async def update_supplier(
    partita_iva: str,
    id_utente: int = Query(...),
    ragione_sociale: Optional[str] = Form(None),
    codice_fiscale: Optional[str] = Form(None),
    indirizzo: Optional[str] = Form(None),
    cap: Optional[str] = Form(None),
    citta: Optional[str] = Form(None),
    provincia: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None),
    pec: Optional[str] = Form(None),
    codice_sdi: Optional[str] = Form(None),
    metodo_pagamento: Optional[str] = Form(None),
    iban: Optional[str] = Form(None),
    banca: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    attivo: Optional[bool] = Form(None)
):
    """
    Aggiorna fornitore con propagazione automatica
    
    Se cambi ragione_sociale:
    → Aggiorna automaticamente TUTTE le fatture del fornitore
    """
    try:
        from app.services.relationship_service import RelationshipService
        
        update_data = {}
        if ragione_sociale: update_data['ragione_sociale'] = ragione_sociale
        if codice_fiscale: update_data['codice_fiscale'] = codice_fiscale
        if indirizzo: update_data['indirizzo'] = indirizzo
        if cap: update_data['cap'] = cap
        if citta: update_data['citta'] = citta
        if provincia: update_data['provincia'] = provincia
        if email: update_data['email'] = email
        if telefono: update_data['telefono'] = telefono
        if pec: update_data['pec'] = pec
        if codice_sdi: update_data['codice_sdi'] = codice_sdi
        if metodo_pagamento: update_data['metodo_pagamento'] = metodo_pagamento
        if iban: update_data['iban'] = iban
        if banca: update_data['banca'] = banca
        if note: update_data['note'] = note
        if attivo is not None: update_data['attivo'] = attivo
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Nessun campo da aggiornare")
        
        update_data['updated_at'] = datetime.now().isoformat()
        
        # Usa servizio con propagazione
        result = await RelationshipService.update_fornitore_propagate(
            id_utente=id_utente,
            partita_iva=partita_iva,
            update_data=update_data
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore update_supplier: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{partita_iva}")
async def delete_supplier(
    partita_iva: str,
    id_utente: int = Query(...),
    force: bool = Query(default=False)
):
    """
    Elimina fornitore con controlli di integrità
    
    Comportamento:
    - Se ha fatture + force=false → BLOCCA eliminazione
    - Se ha fatture + force=true → SOFT DELETE (disattiva)
    - Se NO fatture → HARD DELETE (elimina definitivamente)
    
    Query params:
    - force: true per disattivare invece di eliminare
    """
    try:
        from app.services.relationship_service import RelationshipService
        
        result = await RelationshipService.delete_fornitore_safe(
            id_utente=id_utente,
            partita_iva=partita_iva,
            force=force
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Errore delete_supplier: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{partita_iva}/stats")
async def get_supplier_stats(partita_iva: str, id_utente: int = Query(...)):
    """
    Statistiche fornitore
    - Numero fatture
    - Totale importo
    - Ultima fattura
    """
    try:
        fatture_table = get_table('fatture')
        
        result = fatture_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('partita_iva_fornitore', partita_iva)\
            .execute()
        
        if not result.data:
            return {
                "success": True,
                "data": {
                    "totale_fatture": 0,
                    "totale_importo": 0,
                    "ultima_fattura": None
                }
            }
        
        fatture = result.data
        totale_importo = sum(float(f['totale']) for f in fatture)
        ultima = max(fatture, key=lambda x: x['data_fattura'])
        
        return {
            "success": True,
            "data": {
                "totale_fatture": len(fatture),
                "totale_importo": round(totale_importo, 2),
                "ultima_fattura": ultima['data_fattura'],
                "fatture_pagate": len([f for f in fatture if f.get('pagata')]),
                "fatture_da_pagare": len([f for f in fatture if not f.get('pagata')])
            }
        }
        
    except Exception as e:
        logger.error(f"Errore get_supplier_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{partita_iva}/fatture")
async def get_supplier_invoices(
    partita_iva: str,
    id_utente: int = Query(...),
    anno: Optional[int] = None
):
    """Ottieni tutte le fatture di un fornitore"""
    try:
        fatture_table = get_table('fatture')
        query = fatture_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('partita_iva_fornitore', partita_iva)
        
        if anno:
            query = query.gte('data_fattura', f'{anno}-01-01')\
                        .lte('data_fattura', f'{anno}-12-31')
        
        result = query.order('data_fattura', desc=True).execute()
        
        return {
            "success": True,
            "data": result.data if result.data else [],
            "total": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Errore get_supplier_invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-payment-method/{metodo}")
async def get_suppliers_by_payment(metodo: str, id_utente: int = Query(...)):
    """
    Filtra fornitori per metodo pagamento
    
    Metodi: banca, cassa, assegno, misto
    """
    try:
        fornitori_table = get_table('fornitori')
        
        result = fornitori_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('metodo_pagamento', metodo)\
            .eq('attivo', True)\
            .order('ragione_sociale')\
            .execute()
        
        return {
            "success": True,
            "data": result.data if result.data else [],
            "total": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Errore get_suppliers_by_payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{partita_iva}/dependencies")
async def get_supplier_dependencies(partita_iva: str, id_utente: int = Query(...)):
    """
    Verifica dipendenze fornitore
    
    Mostra:
    - Numero fatture collegate
    - Fatture pagate/non pagate
    - Se può essere eliminato
    """
    try:
        from app.services.relationship_service import RelationshipService
        
        deps = await RelationshipService.get_fornitore_dependencies(
            id_utente=id_utente,
            partita_iva=partita_iva
        )
        
        return {
            "success": True,
            "data": deps
        }
        
    except Exception as e:
        logger.error(f"Errore get_supplier_dependencies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
