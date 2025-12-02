"""
Router Bulk Import - Import massivo da Excel
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import pandas as pd
import logging
from io import BytesIO
from datetime import datetime

from app.database import get_table

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/fornitori")
async def bulk_import_fornitori(
    file: UploadFile = File(...),
    id_utente: int = Form(...)
):
    """
    Import massivo fornitori da Excel
    
    Formato atteso:
    - Partita Iva (obbligatorio)
    - Denominazione (obbligatorio)
    - Email, Telefono, Indirizzo, CAP, Comune, Provincia (opzionali)
    """
    try:
        contents = await file.read()
        
        # Leggi Excel
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(contents), engine='openpyxl')
        elif file.filename.endswith('.xls'):
            df = pd.read_excel(BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Formato file non supportato. Usa .xlsx o .xls")
        
        fornitori_table = get_table('fornitori')
        
        imported = 0
        errors = []
        skipped = 0
        
        for idx, row in df.iterrows():
            try:
                # Estrai P.IVA
                piva = str(row.get('Partita Iva', '')).replace("'", "").strip()
                
                if not piva or len(piva) != 11:
                    skipped += 1
                    continue
                
                # Verifica se esiste già
                existing = fornitori_table.select('*')\
                    .eq('id_utente', id_utente)\
                    .eq('partita_iva', piva)\
                    .execute()
                
                if existing.data:
                    skipped += 1
                    continue
                
                # Prepara dati
                ragione_sociale = str(row.get('Denominazione', 'N/D')).replace('"', '')
                
                data = {
                    'id_utente': id_utente,
                    'partita_iva': piva,
                    'ragione_sociale': ragione_sociale,
                    'codice_fiscale': str(row.get('Codice Fiscale', piva)),
                    'email': str(row.get('Email', '')) if pd.notna(row.get('Email')) else None,
                    'telefono': str(row.get('Telefono', '')) if pd.notna(row.get('Telefono')) else None,
                    'indirizzo': str(row.get('Indirizzo', '')) if pd.notna(row.get('Indirizzo')) else None,
                    'cap': str(row.get('CAP', '')) if pd.notna(row.get('CAP')) else None,
                    'citta': str(row.get('Comune', '')) if pd.notna(row.get('Comune')) else None,
                    'provincia': str(row.get('Provincia', '')) if pd.notna(row.get('Provincia')) else None,
                    'metodo_pagamento': 'banca',
                    'attivo': True,
                    'created_at': datetime.now().isoformat()
                }
                
                # Insert
                fornitori_table.insert(data).execute()
                imported += 1
                
            except Exception as e:
                errors.append(f"Riga {idx+1}: {str(e)}")
        
        return {
            "success": True,
            "imported": imported,
            "skipped": skipped,
            "errors": errors[:10],  # Max 10 errori
            "total_errors": len(errors)
        }
        
    except Exception as e:
        logger.error(f"Errore bulk_import_fornitori: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/corrispettivi")
async def bulk_import_corrispettivi(
    file: UploadFile = File(...),
    id_utente: int = Form(...)
):
    """
    Import massivo corrispettivi da Excel
    
    Formato atteso:
    - Data e ora rilevazione
    - Ammontare delle vendite (totale in euro)
    - Totale
    """
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents), engine='openpyxl')
        
        cassa_table = get_table('movimenti_cassa')
        
        imported = 0
        errors = []
        skipped = 0
        
        for idx, row in df.iterrows():
            try:
                # Salta se importo 0
                totale = float(row.get('Totale', 0))
                if totale == 0:
                    skipped += 1
                    continue
                
                data = pd.to_datetime(row['Data e ora rilevazione'])
                importo = float(row['Ammontare delle vendite (totale in euro)'])
                
                # Insert movimento cassa
                movimento_data = {
                    'id_utente': id_utente,
                    'data': data.strftime('%Y-%m-%d'),
                    'tipo': 'corrispettivi',
                    'descrizione': f"Corrispettivi giornalieri",
                    'importo': importo,
                    'created_at': datetime.now().isoformat()
                }
                
                cassa_table.insert(movimento_data).execute()
                imported += 1
                
            except Exception as e:
                errors.append(f"Riga {idx+1}: {str(e)}")
        
        return {
            "success": True,
            "imported": imported,
            "skipped": skipped,
            "errors": errors[:10],
            "total_errors": len(errors)
        }
        
    except Exception as e:
        logger.error(f"Errore bulk_import_corrispettivi: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pos")
async def bulk_import_pos(
    file: UploadFile = File(...),
    id_utente: int = Form(...)
):
    """Import massivo transazioni POS"""
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents), engine='openpyxl')
        
        cassa_table = get_table('movimenti_cassa')
        imported = 0
        errors = []
        skipped = 0
        
        for idx, row in df.iterrows():
            try:
                if pd.isna(row['IMPORTO']) or float(row['IMPORTO']) == 0:
                    skipped += 1
                    continue
                
                data = pd.to_datetime(row['DATA'])
                importo = -abs(float(row['IMPORTO']))  # Negativo
                
                movimento_data = {
                    'id_utente': id_utente,
                    'data': data.strftime('%Y-%m-%d'),
                    'tipo': 'pos',
                    'descrizione': 'Transazioni POS',
                    'importo': importo,
                    'created_at': datetime.now().isoformat()
                }
                
                cassa_table.insert(movimento_data).execute()
                imported += 1
                
            except Exception as e:
                errors.append(f"Riga {idx+1}: {str(e)}")
        
        return {
            "success": True,
            "imported": imported,
            "skipped": skipped,
            "errors": errors[:10],
            "total_errors": len(errors)
        }
        
    except Exception as e:
        logger.error(f"Errore bulk_import_pos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/versamenti")
async def bulk_import_versamenti(
    file: UploadFile = File(...),
    id_utente: int = Form(...)
):
    """Import massivo versamenti"""
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents), engine='openpyxl')
        
        cassa_table = get_table('movimenti_cassa')
        imported = 0
        errors = []
        skipped = 0
        
        for idx, row in df.iterrows():
            try:
                if pd.isna(row['IMPORTO']) or float(row['IMPORTO']) == 0:
                    skipped += 1
                    continue
                
                data = pd.to_datetime(row['DATA'])
                importo = -abs(float(row['IMPORTO']))  # Negativo
                
                movimento_data = {
                    'id_utente': id_utente,
                    'data': data.strftime('%Y-%m-%d'),
                    'tipo': 'versamento',
                    'descrizione': 'Versamento in banca',
                    'importo': importo,
                    'created_at': datetime.now().isoformat()
                }
                
                cassa_table.insert(movimento_data).execute()
                imported += 1
                
            except Exception as e:
                errors.append(f"Riga {idx+1}: {str(e)}")
        
        return {
            "success": True,
            "imported": imported,
            "skipped": skipped,
            "errors": errors[:10],
            "total_errors": len(errors)
        }
        
    except Exception as e:
        logger.error(f"Errore bulk_import_versamenti: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
