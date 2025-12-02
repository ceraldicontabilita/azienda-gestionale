"""
Router Dipendenti - CRUD Completo
"""

from fastapi import APIRouter, HTTPException, Query, Form, UploadFile, File
from typing import Optional
from datetime import datetime
import logging

from app.database import get_table

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_employees(
    id_utente: int = Query(...),
    attivo: Optional[bool] = None
):
    """Ottieni lista dipendenti"""
    try:
        dipendenti_table = get_table('dipendenti')
        query = dipendenti_table.select('*').eq('id_utente', id_utente)
        
        if attivo is not None:
            query = query.eq('attivo', attivo)
        
        result = query.order('cognome', 'nome').execute()
        
        return {
            "success": True,
            "data": result.data if result.data else [],
            "total": len(result.data) if result.data else 0
        }
    except Exception as e:
        logger.error(f"Errore get_employees: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_employee(
    id_utente: int = Form(...),
    nome: str = Form(...),
    cognome: str = Form(...),
    codice_fiscale: str = Form(...),
    data_nascita: Optional[str] = Form(None),
    mansione: Optional[str] = Form(None),
    data_assunzione: Optional[str] = Form(None),
    tipo_contratto: Optional[str] = Form(None),
    retribuzione_mensile: Optional[float] = Form(None),
    email: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None)
):
    """Crea nuovo dipendente"""
    try:
        dipendenti_table = get_table('dipendenti')
        
        existing = dipendenti_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('codice_fiscale', codice_fiscale)\
            .execute()
        
        if existing.data:
            raise HTTPException(status_code=400, detail="Dipendente già esistente")
        
        result = dipendenti_table.insert({
            'id_utente': id_utente,
            'nome': nome,
            'cognome': cognome,
            'codice_fiscale': codice_fiscale,
            'data_nascita': data_nascita,
            'mansione': mansione,
            'data_assunzione': data_assunzione,
            'tipo_contratto': tipo_contratto,
            'retribuzione_mensile': retribuzione_mensile,
            'email': email,
            'telefono': telefono,
            'attivo': True,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return {
            "success": True,
            "message": "Dipendente creato",
            "data": result.data[0] if result.data else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore create_employee: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-busta-paga")
async def upload_payslip(
    file: UploadFile = File(...),
    id_utente: int = Form(...)
):
    """
    Upload e parse PDF busta paga Zucchetti
    Estrae automaticamente: nome, CF, netto, acconto, mese, anno
    """
    try:
        from app.parsers.busta_paga_parser import parse_busta_paga
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            data = parse_busta_paga(tmp_path)
            
            dipendenti_table = get_table('dipendenti')
            paghe_table = get_table('paghe_dipendenti')
            
            dipendente = dipendenti_table.select('*')\
                .eq('id_utente', id_utente)\
                .eq('codice_fiscale', data['codice_fiscale'])\
                .execute()
            
            if not dipendente.data:
                dipendente_result = dipendenti_table.insert({
                    'id_utente': id_utente,
                    'nome': data['nome'],
                    'cognome': data['cognome'],
                    'codice_fiscale': data['codice_fiscale'],
                    'mansione': data.get('mansione'),
                    'attivo': True,
                    'created_at': datetime.now().isoformat()
                }).execute()
                id_dipendente = dipendente_result.data[0]['id']
            else:
                id_dipendente = dipendente.data[0]['id']
            
            paghe_table.insert({
                'id_utente': id_utente,
                'id_dipendente': id_dipendente,
                'mese': data['mese'],
                'anno': data['anno'],
                'lordo': float(data['lordo']) if data.get('lordo') else None,
                'netto': float(data['netto']),
                'acconto': float(data['acconto']) if data.get('acconto') else None,
                'saldo': float(data['saldo']) if data.get('saldo') else None,
                'inps_dipendente': float(data['inps_dipendente']) if data.get('inps_dipendente') else None,
                'inail': float(data['inail']) if data.get('inail') else None,
                'irpef': float(data['irpef']) if data.get('irpef') else None,
                'pagata': False,
                'created_at': datetime.now().isoformat()
            }).execute()
            
            return {
                "success": True,
                "message": "Busta paga importata",
                "data": data
            }
        finally:
            os.unlink(tmp_path)
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Errore upload_payslip: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id_dipendente}/paghe")
async def get_employee_payslips(
    id_dipendente: int,
    id_utente: int = Query(...),
    anno: Optional[int] = None
):
    """Ottieni buste paga dipendente"""
    try:
        paghe_table = get_table('paghe_dipendenti')
        query = paghe_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('id_dipendente', id_dipendente)
        
        if anno:
            query = query.eq('anno', anno)
        
        result = query.order('anno', desc=True).order('mese', desc=True).execute()
        
        return {
            "success": True,
            "data": result.data if result.data else []
        }
    except Exception as e:
        logger.error(f"Errore get_employee_payslips: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id_dipendente}")
async def delete_employee(
    id_dipendente: int,
    id_utente: int = Query(...),
    force: bool = Query(default=False)
):
    """
    Elimina dipendente con controlli
    
    Comportamento:
    - Se ha paghe/turni + force=false → BLOCCA
    - Se ha paghe/turni + force=true → SOFT DELETE (disattiva)
    - Se NO paghe/turni → HARD DELETE
    """
    try:
        from app.services.relationship_service import RelationshipService
        
        result = await RelationshipService.delete_dipendente_safe(
            id_utente=id_utente,
            id_dipendente=id_dipendente,
            force=force
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Errore delete_employee: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id_dipendente}")
async def update_employee(
    id_dipendente: int,
    id_utente: int = Query(...),
    nome: Optional[str] = Form(None),
    cognome: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None),
    mansione: Optional[str] = Form(None),
    retribuzione_mensile: Optional[float] = Form(None),
    attivo: Optional[bool] = Form(None)
):
    """
    Aggiorna dipendente
    
    Note: nome/cognome nelle paghe vengono letti via JOIN,
    quindi non serve propagazione
    """
    try:
        from app.services.relationship_service import RelationshipService
        
        update_data = {}
        if nome: update_data['nome'] = nome
        if cognome: update_data['cognome'] = cognome
        if email: update_data['email'] = email
        if telefono: update_data['telefono'] = telefono
        if mansione: update_data['mansione'] = mansione
        if retribuzione_mensile: update_data['retribuzione_mensile'] = retribuzione_mensile
        if attivo is not None: update_data['attivo'] = attivo
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Nessun campo da aggiornare")
        
        update_data['updated_at'] = datetime.now().isoformat()
        
        result = await RelationshipService.update_dipendente_propagate(
            id_utente=id_utente,
            id_dipendente=id_dipendente,
            update_data=update_data
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore update_employee: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
