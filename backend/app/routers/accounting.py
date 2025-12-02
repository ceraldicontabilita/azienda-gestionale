"""Router Contabilità Completa"""
from fastapi import APIRouter, HTTPException, Query, Form
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
import logging
from app.database import get_table

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/popola-piano-conti")
async def popola_piano_conti(id_utente: int = Form(...)):
    """Popola piano dei conti con struttura base per HORECA"""
    try:
        piano_table = get_table('piano_dei_conti')
        
        # Verifica se già popolato
        existing = piano_table.select('id').eq('id_utente', id_utente).execute()
        if existing.data and len(existing.data) > 0:
            raise HTTPException(status_code=400, detail="Piano dei conti già popolato")
        
        # Conti da inserire
        conti = [
            # ATTIVO - IMMOBILIZZAZIONI
            ('1001', 'Immobili', 'attivo', 'immobilizzazioni'),
            ('1002', 'Impianti e macchinari', 'attivo', 'immobilizzazioni'),
            ('1003', 'Attrezzature', 'attivo', 'immobilizzazioni'),
            ('1004', 'Mobili e arredi', 'attivo', 'immobilizzazioni'),
            ('1005', 'Automezzi', 'attivo', 'immobilizzazioni'),
            # ATTIVO - CIRCOLANTE
            ('2001', 'Cassa contanti', 'attivo', 'liquidita'),
            ('2002', 'Banca c/c', 'attivo', 'liquidita'),
            ('2003', 'POS da incassare', 'attivo', 'liquidita'),
            ('2010', 'Crediti clienti', 'attivo', 'crediti'),
            ('2020', 'Rimanenze materie prime', 'attivo', 'rimanenze'),
            ('2021', 'Rimanenze prodotti finiti', 'attivo', 'rimanenze'),
            ('2030', 'IVA a credito', 'attivo', 'crediti_tributari'),
            # PASSIVO
            ('3001', 'Capitale sociale', 'passivo', 'patrimonio_netto'),
            ('3002', 'Utili esercizi precedenti', 'passivo', 'patrimonio_netto'),
            ('3003', 'Utile/Perdita esercizio', 'passivo', 'patrimonio_netto'),
            ('4001', 'Debiti fornitori', 'passivo', 'debiti'),
            ('4002', 'Debiti banche', 'passivo', 'debiti'),
            ('4010', 'Debiti dipendenti', 'passivo', 'debiti'),
            ('4020', 'Debiti tributari', 'passivo', 'debiti_tributari'),
            ('4021', 'IVA a debito', 'passivo', 'debiti_tributari'),
            ('4030', 'TFR', 'passivo', 'debiti'),
            # COSTI
            ('5001', 'Materie prime', 'costo', 'costi_acquisti'),
            ('5002', 'Ingredienti freschi', 'costo', 'costi_acquisti'),
            ('5003', 'Packaging', 'costo', 'costi_acquisti'),
            ('5101', 'Energia elettrica', 'costo', 'costi_servizi'),
            ('5102', 'Gas', 'costo', 'costi_servizi'),
            ('5103', 'Acqua', 'costo', 'costi_servizi'),
            ('5105', 'Manutenzioni', 'costo', 'costi_servizi'),
            ('5106', 'Consulenze', 'costo', 'costi_servizi'),
            ('5107', 'Pubblicità', 'costo', 'costi_servizi'),
            ('5108', 'Spese bancarie', 'costo', 'costi_servizi'),
            ('5109', 'Affitto', 'costo', 'costi_servizi'),
            ('5110', 'Assicurazioni', 'costo', 'costi_servizi'),
            ('5111', 'Telefono internet', 'costo', 'costi_servizi'),
            ('5201', 'Stipendi salari', 'costo', 'costi_personale'),
            ('5202', 'INPS', 'costo', 'costi_personale'),
            ('5203', 'INAIL', 'costo', 'costi_personale'),
            ('5204', 'TFR maturato', 'costo', 'costi_personale'),
            ('5301', 'Ammortamenti', 'costo', 'ammortamenti'),
            ('5401', 'Imposte tasse', 'costo', 'altri_costi'),
            ('5404', 'Interessi passivi', 'costo', 'altri_costi'),
            # RICAVI
            ('7001', 'Vendite pasticceria', 'ricavo', 'ricavi_vendite'),
            ('7002', 'Vendite torte', 'ricavo', 'ricavi_vendite'),
            ('7003', 'Vendite caffetteria', 'ricavo', 'ricavi_vendite'),
        ]
        
        for codice, descrizione, tipo, categoria in conti:
            piano_table.insert({
                'id_utente': id_utente,
                'codice_conto': codice,
                'descrizione': descrizione,
                'tipo': tipo,
                'categoria': categoria,
                'saldo': 0,
                'attivo': True,
                'created_at': datetime.now().isoformat()
            }).execute()
        
        return {
            "success": True,
            "message": f"Piano dei conti popolato con {len(conti)} conti",
            "conti_creati": len(conti)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore popola_piano_conti: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/piano-conti")
async def get_piano_conti(id_utente: int = Query(...), tipo: Optional[str] = None):
    """Ottieni piano dei conti"""
    try:
        piano_table = get_table('piano_dei_conti')
        query = piano_table.select('*').eq('id_utente', id_utente).eq('attivo', True)
        if tipo:
            query = query.eq('tipo', tipo)
        result = query.order('codice_conto').execute()
        return {"success": True, "data": result.data if result.data else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/movimento")
async def registra_movimento(
    id_utente: int = Form(...),
    data_movimento: str = Form(...),
    codice_conto: str = Form(...),
    descrizione: str = Form(...),
    tipo_movimento: str = Form(...),  # dare/avere
    importo: float = Form(...),
    documento_riferimento: Optional[str] = Form(None)
):
    """Registra movimento contabile"""
    try:
        mov_table = get_table('movimenti_contabili')
        piano_table = get_table('piano_dei_conti')
        
        # Verifica conto esiste
        conto = piano_table.select('*').eq('id_utente', id_utente).eq('codice_conto', codice_conto).execute()
        if not conto.data:
            raise HTTPException(status_code=404, detail="Conto non trovato")
        
        # Registra movimento
        result = mov_table.insert({
            'id_utente': id_utente,
            'data_movimento': data_movimento,
            'codice_conto': codice_conto,
            'descrizione': descrizione,
            'tipo_movimento': tipo_movimento,
            'importo': importo,
            'documento_riferimento': documento_riferimento,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        # Aggiorna saldo conto
        saldo_attuale = float(conto.data[0].get('saldo', 0))
        nuovo_saldo = saldo_attuale + importo if tipo_movimento == 'dare' else saldo_attuale - importo
        piano_table.update({'saldo': nuovo_saldo}).eq('id_utente', id_utente).eq('codice_conto', codice_conto).execute()
        
        return {"success": True, "message": "Movimento registrato", "data": result.data[0] if result.data else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bilancio/stato-patrimoniale")
async def stato_patrimoniale(id_utente: int = Query(...), data_riferimento: Optional[str] = None):
    """Genera stato patrimoniale"""
    try:
        piano_table = get_table('piano_dei_conti')
        data_rif = data_riferimento or datetime.now().date().isoformat()
        
        conti = piano_table.select('*').eq('id_utente', id_utente).eq('attivo', True).execute()
        if not conti.data:
            raise HTTPException(status_code=404, detail="Piano dei conti non trovato")
        
        attivo_totale = sum(float(c.get('saldo', 0)) for c in conti.data if c['tipo'] == 'attivo')
        passivo_totale = sum(float(c.get('saldo', 0)) for c in conti.data if c['tipo'] == 'passivo')
        
        return {
            "success": True,
            "data": {
                "data_riferimento": data_rif,
                "attivo": {
                    "totale": round(attivo_totale, 2),
                    "dettaglio": [c for c in conti.data if c['tipo'] == 'attivo']
                },
                "passivo": {
                    "totale": round(passivo_totale, 2),
                    "dettaglio": [c for c in conti.data if c['tipo'] == 'passivo']
                },
                "pareggio": round(attivo_totale - passivo_totale, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bilancio/conto-economico")
async def conto_economico(id_utente: int = Query(...), anno: int = Query(...)):
    """Genera conto economico annuale"""
    try:
        piano_table = get_table('piano_dei_conti')
        
        conti = piano_table.select('*').eq('id_utente', id_utente).eq('attivo', True).execute()
        if not conti.data:
            raise HTTPException(status_code=404, detail="Piano dei conti non trovato")
        
        ricavi_totali = sum(float(c.get('saldo', 0)) for c in conti.data if c['tipo'] == 'ricavo')
        costi_totali = sum(float(c.get('saldo', 0)) for c in conti.data if c['tipo'] == 'costo')
        utile = ricavi_totali - costi_totali
        
        return {
            "success": True,
            "data": {
                "anno": anno,
                "ricavi": {
                    "totale": round(ricavi_totali, 2),
                    "dettaglio": [c for c in conti.data if c['tipo'] == 'ricavo']
                },
                "costi": {
                    "totale": round(costi_totali, 2),
                    "dettaglio": [c for c in conti.data if c['tipo'] == 'costo']
                },
                "utile_perdita": round(utile, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
