"""
Router Fatture - Gestione completa fatture passive
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime, date
import logging
import io

from app.database import get_table
from app.parsers.fatturapa_parser import parse_fattura_xml
from app.models.invoices import Fattura, FatturaCreate, FatturaUpdate

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_invoices(
    id_utente: int = Query(...),
    status: Optional[str] = None,
    metodo_pagamento: Optional[str] = None,
    pagata: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Ottieni lista fatture con filtri
    
    Query params:
        - status: active, pending, paid, archived
        - metodo_pagamento: banca, cassa, assegno, misto
        - pagata: true/false
    """
    try:
        fatture_table = get_table('fatture')
        query = fatture_table.select('*').eq('id_utente', id_utente)
        
        if status:
            query = query.eq('stato', status)
        if metodo_pagamento:
            query = query.eq('metodo_pagamento', metodo_pagamento)
        if pagata is not None:
            query = query.eq('pagata', pagata)
        
        result = query.order('data_fattura', desc=True).range(offset, offset + limit - 1).execute()
        
        return {
            "success": True,
            "data": result.data if result.data else [],
            "total": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Errore get_invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-state/{state}")
async def get_invoices_by_state(state: str, id_utente: int = Query(...)):
    """
    Ottieni fatture per stato specifico
    
    States:
        - pending: In attesa (bonifico in corso)
        - registered_bank: Pagate via bonifico
        - registered_cash: Pagate in contanti
        - paid_not_reconciled: Pagate ma non riconciliate
        - unmanaged: Senza metodo pagamento
    """
    try:
        fatture_table = get_table('fatture')
        
        if state == "pending":
            query = fatture_table.select('*')\
                .eq('id_utente', id_utente)\
                .eq('stato', 'pending')
        elif state == "registered_bank":
            query = fatture_table.select('*')\
                .eq('id_utente', id_utente)\
                .eq('metodo_pagamento', 'banca')\
                .eq('pagata', True)
        elif state == "registered_cash":
            query = fatture_table.select('*')\
                .eq('id_utente', id_utente)\
                .eq('metodo_pagamento', 'cassa')\
                .eq('pagata', True)
        elif state == "paid_not_reconciled":
            query = fatture_table.select('*')\
                .eq('id_utente', id_utente)\
                .eq('pagata', True)\
                .eq('riconciliata', False)
        elif state == "unmanaged":
            query = fatture_table.select('*')\
                .eq('id_utente', id_utente)\
                .is_('metodo_pagamento', 'null')
        else:
            raise HTTPException(status_code=400, detail=f"Stato non valido: {state}")
        
        result = query.order('data_fattura', desc=True).execute()
        
        return {
            "success": True,
            "data": result.data if result.data else [],
            "total": len(result.data) if result.data else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore get_invoices_by_state: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-bulk")
async def upload_bulk_invoices(
    files: List[UploadFile] = File(...),
    id_utente: int = Form(...)
):
    """
    Upload multiplo fatture XML FatturaPA
    
    Supporta:
        - Formato FatturaPA con namespace
        - Formato XML semplificato
    """
    results = []
    errors = []
    
    for file in files:
        try:
            # Leggi contenuto XML
            content = await file.read()
            xml_string = content.decode('utf-8')
            
            # Parse XML
            fattura_data = parse_fattura_xml(xml_string)
            
            # Crea/aggiorna fornitore
            fornitori_table = get_table('fornitori')
            partita_iva = fattura_data['fornitore'].get('partita_iva')
            ragione_sociale = fattura_data['fornitore'].get('ragione_sociale')
            
            if partita_iva and ragione_sociale:
                # Verifica se fornitore esiste
                existing = fornitori_table.select('*')\
                    .eq('id_utente', id_utente)\
                    .eq('partita_iva', partita_iva)\
                    .execute()
                
                if not existing.data:
                    # Crea nuovo fornitore
                    fornitori_table.insert({
                        'id_utente': id_utente,
                        'partita_iva': partita_iva,
                        'ragione_sociale': ragione_sociale,
                        'indirizzo': fattura_data['fornitore'].get('indirizzo'),
                        'cap': fattura_data['fornitore'].get('cap'),
                        'citta': fattura_data['fornitore'].get('comune'),
                        'provincia': fattura_data['fornitore'].get('provincia'),
                    }).execute()
            
            # Crea fattura
            fatture_table = get_table('fatture')
            
            imponibile = float(fattura_data['totali'].get('imponibile', 0))
            iva = float(fattura_data['totali'].get('iva', 0))
            totale = float(fattura_data['totali'].get('totale', 0))
            
            fattura_insert = {
                'id_utente': id_utente,
                'numero_fattura': fattura_data['dati_generali'].get('numero', ''),
                'data_fattura': fattura_data['dati_generali'].get('data', datetime.now().date().isoformat()),
                'partita_iva_fornitore': partita_iva or '',
                'ragione_sociale_fornitore': ragione_sociale or '',
                'imponibile': imponibile,
                'iva': iva,
                'totale': totale,
                'stato': 'active',
                'pagata': False,
                'file_path': file.filename
            }
            
            # Data scadenza da pagamento se presente
            if 'pagamento' in fattura_data and fattura_data['pagamento'].get('data_scadenza'):
                fattura_insert['data_scadenza'] = fattura_data['pagamento']['data_scadenza']
            
            fattura_result = fatture_table.insert(fattura_insert).execute()
            
            # Crea righe fattura
            if fattura_result.data and len(fattura_result.data) > 0:
                id_fattura = fattura_result.data[0]['id']
                righe_table = get_table('righe_fattura')
                
                for riga in fattura_data.get('righe', []):
                    righe_table.insert({
                        'id_fattura': id_fattura,
                        'descrizione': riga.get('descrizione', ''),
                        'quantita': float(riga.get('quantita', 1)),
                        'prezzo_unitario': float(riga.get('prezzo_unitario', 0)),
                        'importo': float(riga.get('prezzo_totale', 0)),
                        'aliquota_iva': float(riga.get('aliquota_iva', 22))
                    }).execute()
            
            results.append({
                "filename": file.filename,
                "success": True,
                "numero_fattura": fattura_data['dati_generali'].get('numero'),
                "fornitore": ragione_sociale
            })
            
        except Exception as e:
            logger.error(f"Errore upload {file.filename}: {str(e)}")
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "success": len(errors) == 0,
        "uploaded": len(results),
        "errors": len(errors),
        "results": results,
        "error_details": errors
    }

@router.put("/{id_fattura}")
async def update_invoice(id_fattura: int, update: FatturaUpdate, id_utente: int = Query(...)):
    """Aggiorna fattura"""
    try:
        fatture_table = get_table('fatture')
        
        update_data = update.model_dump(exclude_none=True)
        update_data['updated_at'] = datetime.now().isoformat()
        
        result = fatture_table.update(update_data)\
            .eq('id', id_fattura)\
            .eq('id_utente', id_utente)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Fattura non trovata")
        
        return {
            "success": True,
            "data": result.data[0] if result.data else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore update_invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id_fattura}")
async def delete_invoice(id_fattura: int, id_utente: int = Query(...)):
    """
    Elimina fattura con cascata completa
    
    Elimina automaticamente:
    - Righe fattura
    - Movimenti Prima Nota Cassa collegati
    - Movimenti Prima Nota Banca collegati
    
    Scollega (senza eliminare):
    - Bonifici → tornano "non collegati"
    - Assegni → tornano "disponibili" (se erano "emessi")
    """
    try:
        from app.services.relationship_service import RelationshipService
        
        result = await RelationshipService.delete_fattura_with_cascade(
            id_utente=id_utente,
            id_fattura=id_fattura
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Errore delete_invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id_fattura}/righe")
async def get_invoice_lines(id_fattura: int, id_utente: int = Query(...)):
    """Ottieni righe dettaglio fattura"""
    try:
        righe_table = get_table('righe_fattura')
        result = righe_table.select('*').eq('id_fattura', id_fattura).execute()
        
        return {
            "success": True,
            "data": result.data if result.data else []
        }
        
    except Exception as e:
        logger.error(f"Errore get_invoice_lines: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{id_fattura}/mark-paid")
async def mark_invoice_paid(
    id_fattura: int,
    id_utente: int = Query(...),
    metodo: str = Form(...),
    data_pagamento: Optional[str] = Form(None),
    id_assegno: Optional[int] = Form(None),
    id_bonifico: Optional[int] = Form(None),
    note: Optional[str] = Form(None)
):
    """
    Segna fattura come pagata e registra movimento contabile
    
    Args:
        metodo: cassa, banca_bonifico, banca_rid, assegno, misto
        data_pagamento: Data pagamento (default oggi)
        id_assegno: ID assegno (se metodo=assegno)
        id_bonifico: ID bonifico (se metodo=banca_bonifico)
        note: Note aggiuntive
    
    Azioni:
        - metodo='cassa' → Crea movimento in Prima Nota Cassa
        - metodo='banca_bonifico' → Crea movimento in Prima Nota Banca + collega bonifico
        - metodo='banca_rid' → Crea movimento in Prima Nota Banca (RID)
        - metodo='assegno' → Collega assegno + movimento Prima Nota Banca
    """
    try:
        from app.services.payment_service import PaymentService
        
        # Get fattura per importo
        fatture_table = get_table('fatture')
        fattura = fatture_table.select('*').eq('id', id_fattura).eq('id_utente', id_utente).execute()
        
        if not fattura.data:
            raise HTTPException(status_code=404, detail="Fattura non trovata")
        
        importo = Decimal(str(fattura.data[0]['totale']))
        data_pag = datetime.fromisoformat(data_pagamento) if data_pagamento else datetime.now()
        
        # Registra pagamento (crea movimenti contabili)
        result = await PaymentService.registra_pagamento_fattura(
            id_utente=id_utente,
            id_fattura=id_fattura,
            metodo=metodo,
            importo=importo,
            data_pagamento=data_pag,
            id_assegno=id_assegno,
            id_bonifico=id_bonifico,
            note=note
        )
        
        return {
            "success": True,
            "message": f"Fattura pagata e registrata in {metodo}",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore mark_invoice_paid: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-excel")
async def export_invoices_excel(id_utente: int = Query(...)):
    """Export fatture in Excel"""
    # TODO: Implementare export Excel con openpyxl o pandas
    return {
        "success": False,
        "message": "Funzionalità in sviluppo"
    }

@router.get("/payment-options/assegni")
async def get_available_checks(id_utente: int = Query(...)):
    """
    Ottieni lista assegni disponibili per pagamento fattura
    """
    try:
        from app.services.payment_service import PaymentService
        
        assegni = await PaymentService.get_assegni_disponibili(id_utente)
        
        return {
            "success": True,
            "data": assegni,
            "total": len(assegni)
        }
    except Exception as e:
        logger.error(f"Errore get_available_checks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment-options/bonifici")
async def get_unlinked_transfers(id_utente: int = Query(...)):
    """
    Ottieni lista bonifici non ancora collegati a fatture
    """
    try:
        from app.services.payment_service import PaymentService
        
        bonifici = await PaymentService.get_bonifici_non_collegati(id_utente)
        
        return {
            "success": True,
            "data": bonifici,
            "total": len(bonifici)
        }
    except Exception as e:
        logger.error(f"Errore get_unlinked_transfers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest-payment-match")
async def suggest_payment_match(
    id_bonifico: int = Form(...),
    id_utente: int = Query(...)
):
    """
    Suggerisce fattura da collegare a bonifico
    Basato su importo e beneficiario
    """
    try:
        from app.services.payment_service import PaymentService
        
        match = await PaymentService.suggerisci_collegamento_bonifico(id_utente, id_bonifico)
        
        if match:
            return {
                "success": True,
                "suggested": True,
                "data": match
            }
        else:
            return {
                "success": True,
                "suggested": False,
                "message": "Nessuna fattura corrispondente trovata"
            }
    except Exception as e:
        logger.error(f"Errore suggest_payment_match: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
