"""
API Router HR Administration
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
import os

from app.models.hr_models import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    PayslipCreate, PayslipResponse,
    ContractCreate, ContractResponse,
    LeaveRequestResponse, LeaveRequestApprove,
    HRStatistics
)
from app.services.hr_service import HRService

router = APIRouter(prefix="/api/hr", tags=["HR Administration"])


# Placeholder dependencies
async def get_current_admin_user():
    """Placeholder - implementare in main.py"""
    pass

async def get_db():
    """Placeholder - implementare connessione DB"""
    pass


# ============================================================================
# EMPLOYEE MANAGEMENT
# ============================================================================

@router.post("/employees", response_model=EmployeeResponse)
async def create_employee(
    employee: EmployeeCreate,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Crea nuovo dipendente"""
    
    hr_service = HRService(db)
    
    employee_id = await hr_service.create_employee(employee.dict())
    
    # Recupera dipendente creato
    new_employee = await db.fetch_one("""
        SELECT * FROM employees WHERE id = :id
    """, {'id': employee_id})
    
    return EmployeeResponse(**new_employee)


@router.get("/employees", response_model=List[EmployeeResponse])
async def list_employees(
    stato: Optional[str] = 'attivo',
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Lista dipendenti"""
    
    query = "SELECT * FROM employees"
    params = {}
    
    if stato:
        query += " WHERE stato = :stato"
        params['stato'] = stato
    
    query += " ORDER BY cognome, nome"
    
    employees = await db.fetch_all(query, params)
    
    return [EmployeeResponse(**e) for e in employees]


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Dettagli dipendente"""
    
    employee = await db.fetch_one("""
        SELECT * FROM employees WHERE id = :id
    """, {'id': employee_id})
    
    if not employee:
        raise HTTPException(404, "Dipendente non trovato")
    
    return EmployeeResponse(**employee)


@router.patch("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    updates: EmployeeUpdate,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Aggiorna dipendente"""
    
    # Costruisci query dinamica
    update_fields = []
    params = {'id': employee_id}
    
    for field, value in updates.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = :{field}")
            params[field] = value
    
    if not update_fields:
        raise HTTPException(400, "Nessun campo da aggiornare")
    
    query = f"""
        UPDATE employees
        SET {', '.join(update_fields)}, updated_at = NOW()
        WHERE id = :id
        RETURNING *
    """
    
    updated = await db.fetch_one(query, params)
    
    if not updated:
        raise HTTPException(404, "Dipendente non trovato")
    
    return EmployeeResponse(**updated)


@router.post("/employees/{employee_id}/terminate")
async def terminate_employee(
    employee_id: int,
    data_cessazione: date,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Cessazione dipendente"""
    
    hr_service = HRService(db)
    await hr_service.terminate_employee(employee_id, data_cessazione)
    
    return {'success': True, 'message': 'Dipendente cessato'}


# ============================================================================
# PAYSLIP MANAGEMENT
# ============================================================================

@router.post("/payslips/import")
async def import_payslip(
    file: UploadFile = File(...),
    data_disponibilita: Optional[date] = None,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """
    Import manuale busta paga da PDF
    
    Upload PDF → Parse → Salva
    """
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Solo file PDF accettati")
    
    pdf_data = await file.read()
    
    hr_service = HRService(db)
    
    result = await hr_service.import_payslip_from_pdf(
        pdf_data,
        file.filename,
        data_disponibilita or date.today()
    )
    
    if not result['success']:
        raise HTTPException(400, result['error'])
    
    return result


@router.get("/payslips", response_model=List[PayslipResponse])
async def list_payslips(
    employee_id: Optional[int] = None,
    periodo: Optional[str] = None,
    stato_pagamento: Optional[str] = None,
    limit: int = 100,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Lista buste paga"""
    
    query = "SELECT * FROM payslips WHERE 1=1"
    params = {}
    
    if employee_id:
        query += " AND employee_id = :emp_id"
        params['emp_id'] = employee_id
    
    if periodo:
        query += " AND periodo = :periodo"
        params['periodo'] = periodo
    
    if stato_pagamento:
        query += " AND stato_pagamento = :stato"
        params['stato'] = stato_pagamento
    
    query += " ORDER BY anno DESC, mese DESC LIMIT :limit"
    params['limit'] = limit
    
    payslips = await db.fetch_all(query, params)
    
    return [PayslipResponse(**p) for p in payslips]


@router.get("/payslips/{payslip_id}", response_model=PayslipResponse)
async def get_payslip(
    payslip_id: int,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Dettagli busta paga"""
    
    payslip = await db.fetch_one("""
        SELECT * FROM payslips WHERE id = :id
    """, {'id': payslip_id})
    
    if not payslip:
        raise HTTPException(404, "Busta paga non trovata")
    
    return PayslipResponse(**payslip)


@router.get("/payslips/{payslip_id}/download-original")
async def download_payslip_original(
    payslip_id: int,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Scarica PDF originale (con password) - Solo admin"""
    
    payslip = await db.fetch_one("""
        SELECT p.*, e.cognome, e.nome
        FROM payslips p
        JOIN employees e ON p.employee_id = e.id
        WHERE p.id = :id
    """, {'id': payslip_id})
    
    if not payslip or not payslip['pdf_original_path']:
        raise HTTPException(404, "PDF non trovato")
    
    filename = f"BustaPaga_ORIGINAL_{payslip['periodo']}_{payslip['cognome']}.pdf"
    
    return FileResponse(
        payslip['pdf_original_path'],
        media_type='application/pdf',
        filename=filename
    )


@router.post("/payslips/{payslip_id}/mark-paid")
async def mark_payslip_paid(
    payslip_id: int,
    data_pagamento: date,
    movimento_bancario_id: Optional[int] = None,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Marca busta paga come pagata"""
    
    await db.execute("""
        UPDATE payslips
        SET stato_pagamento = 'pagato',
            data_pagamento = :data,
            movimento_bancario_id = :mov_id
        WHERE id = :id
    """, {
        'id': payslip_id,
        'data': data_pagamento,
        'mov_id': movimento_bancario_id
    })
    
    return {'success': True, 'message': 'Busta paga marcata come pagata'}


@router.post("/payslips/{payslip_id}/create-prima-nota")
async def create_prima_nota(
    payslip_id: int,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Crea registrazione prima nota da busta paga"""
    
    hr_service = HRService(db)
    
    try:
        prima_nota_id = await hr_service.create_prima_nota_from_payslip(payslip_id)
        
        return {
            'success': True,
            'prima_nota_id': prima_nota_id,
            'message': 'Prima nota creata'
        }
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/payslips/{payslip_id}/notify-employee")
async def notify_employee_payslip(
    payslip_id: int,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Invia notifica a dipendente per nuova busta paga"""
    
    payslip = await db.fetch_one("""
        SELECT p.*, e.email, e.nome, e.cognome, e.user_id
        FROM payslips p
        JOIN employees e ON p.employee_id = e.id
        WHERE p.id = :id
    """, {'id': payslip_id})
    
    if not payslip:
        raise HTTPException(404, "Busta paga non trovata")
    
    # Marca come notificato
    await db.execute("""
        UPDATE payslips
        SET notificato_dipendente = true,
            data_notifica = NOW()
        WHERE id = :id
    """, {'id': payslip_id})
    
    # Crea notifica in-app
    if payslip['user_id']:
        await db.execute("""
            INSERT INTO hr_notifications (
                employee_id, user_id, tipo, titolo, messaggio, link_url
            ) VALUES (
                :emp_id, :user_id, 'nuova_busta_paga',
                :titolo, :msg, :link
            )
        """, {
            'emp_id': payslip['employee_id'],
            'user_id': payslip['user_id'],
            'titolo': f"Nuova busta paga disponibile: {payslip['periodo']}",
            'msg': f"La tua busta paga di {payslip['periodo']} è ora disponibile per la consultazione.",
            'link': f"/portale/buste-paga/{payslip_id}"
        })
    
    # TODO: Invia email
    
    return {
        'success': True,
        'message': f"Notifica inviata a {payslip['nome']} {payslip['cognome']}"
    }


# ============================================================================
# CONTRACTS
# ============================================================================

@router.post("/contracts", response_model=ContractResponse)
async def create_contract(
    contract: ContractCreate,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Crea nuovo contratto"""
    
    hr_service = HRService(db)
    
    contract_id = await hr_service.create_contract_from_template(
        contract.employee_id,
        contract.template_used,
        contract.dict()
    )
    
    # Recupera contratto creato
    new_contract = await db.fetch_one("""
        SELECT * FROM contracts WHERE id = :id
    """, {'id': contract_id})
    
    return ContractResponse(**new_contract)


@router.get("/contracts/{contract_id}/download")
async def download_contract(
    contract_id: int,
    formato: str = 'pdf',  # 'pdf' o 'docx'
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Scarica contratto"""
    
    contract = await db.fetch_one("""
        SELECT c.*, e.cognome, e.nome
        FROM contracts c
        JOIN employees e ON c.employee_id = e.id
        WHERE c.id = :id
    """, {'id': contract_id})
    
    if not contract:
        raise HTTPException(404, "Contratto non trovato")
    
    if formato == 'pdf':
        if not contract['pdf_path']:
            raise HTTPException(404, "PDF non disponibile")
        
        filename = f"Contratto_{contract['cognome']}_{contract['nome']}.pdf"
        
        return FileResponse(
            contract['pdf_path'],
            media_type='application/pdf',
            filename=filename
        )
    
    else:  # docx
        if not contract['docx_path']:
            raise HTTPException(404, "DOCX non disponibile")
        
        filename = f"Contratto_{contract['cognome']}_{contract['nome']}.docx"
        
        return FileResponse(
            contract['docx_path'],
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=filename
        )


# ============================================================================
# LEAVE REQUESTS
# ============================================================================

@router.get("/leave-requests", response_model=List[LeaveRequestResponse])
async def list_leave_requests(
    stato: Optional[str] = 'in_attesa',
    employee_id: Optional[int] = None,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Lista richieste ferie/permessi"""
    
    query = "SELECT * FROM leave_requests WHERE 1=1"
    params = {}
    
    if stato:
        query += " AND stato = :stato"
        params['stato'] = stato
    
    if employee_id:
        query += " AND employee_id = :emp_id"
        params['emp_id'] = employee_id
    
    query += " ORDER BY created_at DESC"
    
    requests = await db.fetch_all(query, params)
    
    return [LeaveRequestResponse(**r) for r in requests]


@router.post("/leave-requests/{request_id}/approve")
async def approve_leave_request(
    request_id: int,
    approval: LeaveRequestApprove,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Approva/Rifiuta richiesta ferie"""
    
    hr_service = HRService(db)
    
    if approval.approvato:
        await hr_service.approve_leave_request(
            request_id,
            current_user.id,
            approval.note
        )
        message = 'Richiesta approvata'
    else:
        await db.execute("""
            UPDATE leave_requests
            SET stato = 'rifiutato',
                approvato_da = :user_id,
                data_approvazione = NOW(),
                note_approvazione = :note
            WHERE id = :id
        """, {
            'id': request_id,
            'user_id': current_user.id,
            'note': approval.note
        })
        message = 'Richiesta rifiutata'
    
    return {'success': True, 'message': message}


# ============================================================================
# DISPUTES (CONTESTAZIONI)
# ============================================================================

@router.get("/disputes")
async def list_disputes(
    stato: Optional[str] = 'in_attesa',
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Lista contestazioni buste paga"""
    
    query = """
        SELECT 
            d.*,
            e.nome, e.cognome, e.codice_fiscale,
            p.periodo, p.netto_in_busta
        FROM payslip_disputes d
        JOIN employees e ON d.employee_id = e.id
        JOIN payslips p ON d.payslip_id = p.id
        WHERE 1=1
    """
    params = {}
    
    if stato:
        query += " AND d.stato = :stato"
        params['stato'] = stato
    
    query += " ORDER BY d.created_at DESC"
    
    disputes = await db.fetch_all(query, params)
    
    return {'success': True, 'contestazioni': [dict(d) for d in disputes]}


@router.post("/disputes/{dispute_id}/respond")
async def respond_to_dispute(
    dispute_id: int,
    stato: str,  # 'accettata', 'rifiutata', 'in_esame', 'risolta'
    risposta: str,
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Rispondi a contestazione"""
    
    await db.execute("""
        UPDATE payslip_disputes
        SET stato = :stato,
            gestito_da = :user_id,
            data_gestione = NOW(),
            risposta = :risposta
        WHERE id = :id
    """, {
        'id': dispute_id,
        'stato': stato,
        'user_id': current_user.id,
        'risposta': risposta
    })
    
    # TODO: Notifica dipendente
    
    return {'success': True, 'message': 'Risposta registrata'}


# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/statistics", response_model=HRStatistics)
async def get_statistics(
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Statistiche HR dashboard"""
    
    hr_service = HRService(db)
    
    stats = await hr_service.get_hr_statistics()
    
    return HRStatistics(**stats)


# ============================================================================
# EMAIL BOT CONTROL
# ============================================================================

@router.post("/email-bot/run")
async def run_email_bot(
    current_user = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Esegui manualmente import email"""
    
    from app.services.email_bot_payslips import run_email_import_job
    
    results = await run_email_import_job(db)
    
    return results
