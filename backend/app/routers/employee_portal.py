"""
API Endpoint per Visualizzazione, Accettazione e Contestazione Buste Paga

Sistema di controllo temporale:
- 180 giorni partono dalla DATA DI DISPONIBILITÀ (quando arriva email)
- NON dalla data di visualizzazione
- Se dipendente apre dopo 180 giorni → Termine scaduto
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from typing import Optional, List
from datetime import datetime, timedelta, date
from pydantic import BaseModel
from decimal import Decimal
import os

router = APIRouter(prefix="/api/portale", tags=["Portale Dipendente"])


# Placeholder per dipendenze (da implementare in main.py)
async def get_current_employee_user():
    """Placeholder - implementare autenticazione"""
    pass

async def get_db():
    """Placeholder - implementare connessione DB"""
    pass

async def get_employee_by_user_id(user_id: int, db):
    """Placeholder - implementare query"""
    pass


# ============================================================================
# MODELS
# ============================================================================

class PayslipAcceptRequest(BaseModel):
    """Richiesta accettazione busta paga"""
    accetto: bool = True
    

class PayslipDisputeCreate(BaseModel):
    """Crea contestazione busta paga"""
    tipo_anomalia: str  # 'retribuzione', 'ore', 'contributi', 'irpef', 'ferie', 'tfr', 'altro'
    descrizione: str
    importo_indicato: Optional[Decimal] = None
    importo_ritenuto_corretto: Optional[Decimal] = None
    presentazione: str = 'portale'  # 'portale', 'email', 'mano'


class PayslipDetailResponse(BaseModel):
    """Risposta dettagli busta paga"""
    # Dati busta
    id: int
    periodo: str
    anno: int
    mese: int
    retribuzione_lorda: Decimal
    netto_in_busta: Decimal
    stato_pagamento: str
    data_pagamento: Optional[date]
    
    # PDF
    pdf_disponibile: bool
    
    # Stato visualizzazione/accettazione
    visualizzato: bool
    data_prima_visualizzazione: Optional[datetime]
    numero_visualizzazioni: int
    accettato: bool
    data_accettazione: Optional[datetime]
    
    # Controllo contestazione
    data_disponibilita: date
    data_scadenza_contestazione: date
    giorni_rimanenti_contestazione: int
    contestazione_possibile: bool
    contestazione_scaduta: bool
    messaggio_scadenza: Optional[str]
    
    # Contestazioni esistenti
    ha_contestazioni: bool
    numero_contestazioni: int


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calcola_giorni_rimanenti(data_disponibilita: date, data_scadenza: date) -> int:
    """Calcola giorni rimanenti per contestare"""
    oggi = date.today()
    
    if oggi > data_scadenza:
        return 0
    
    return (data_scadenza - oggi).days


def genera_messaggio_scadenza(
    giorni_rimanenti: int,
    data_prima_visualizzazione: Optional[datetime],
    data_disponibilita: date
) -> Optional[str]:
    """Genera messaggio informativo sulla scadenza"""
    
    if giorni_rimanenti <= 0:
        giorni_ritardo = (date.today() - data_disponibilita).days - 180
        
        if data_prima_visualizzazione:
            giorni_visualizzazione = (date.today() - data_prima_visualizzazione.date()).days
            
            return (
                f"⚠️ **TERMINE DI CONTESTAZIONE SCADUTO**\n\n"
                f"La busta paga era disponibile dal {data_disponibilita.strftime('%d/%m/%Y')} "
                f"e poteva essere contestata entro 180 giorni.\n\n"
                f"**Il termine è scaduto {giorni_ritardo} giorni fa** "
                f"({(data_disponibilita + timedelta(days=180)).strftime('%d/%m/%Y')}).\n\n"
                f"Hai visualizzato questa busta paga per la prima volta "
                f"{giorni_visualizzazione} giorni dopo la disponibilità.\n\n"
                f"⚖️ Secondo la Legge n. 4/1943, il termine decorre dalla data di messa a disposizione "
                f"della busta paga, non dalla data di visualizzazione. "
                f"L'accettazione tacita del pagamento comporta la decadenza dal diritto di contestazione."
            )
        else:
            return (
                f"⚠️ **TERMINE DI CONTESTAZIONE SCADUTO**\n\n"
                f"La busta paga era disponibile dal {data_disponibilita.strftime('%d/%m/%Y')} "
                f"e il termine di 180 giorni è scaduto il "
                f"{(data_disponibilita + timedelta(days=180)).strftime('%d/%m/%Y')}.\n\n"
                f"**Il termine è scaduto {giorni_ritardo} giorni fa.**\n\n"
                f"Non è più possibile contestare questa busta paga."
            )
    
    elif giorni_rimanenti <= 30:
        return (
            f"⚠️ **ATTENZIONE: Tempo in scadenza**\n\n"
            f"Hai ancora **{giorni_rimanenti} giorni** per contestare eventuali anomalie "
            f"(scadenza: {(data_disponibilita + timedelta(days=180)).strftime('%d/%m/%Y')}).\n\n"
            f"Verifica attentamente la busta paga e, se necessario, "
            f"scarica il modulo di contestazione."
        )
    
    elif giorni_rimanenti <= 90:
        return (
            f"ℹ️ Hai **{giorni_rimanenti} giorni** per contestare eventuali anomalie "
            f"(scadenza: {(data_disponibilita + timedelta(days=180)).strftime('%d/%m/%Y')})."
        )
    
    return None


async def log_payslip_action(
    db,
    payslip_id: int,
    employee_id: int,
    tipo: str,
    request: Request,
    giorni_rimanenti: int
):
    """Registra azione su busta paga (visualizzazione, download, ecc)"""
    
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get('user-agent', '')
    
    await db.execute("""
        INSERT INTO payslip_download_log 
        (payslip_id, employee_id, tipo, ip_address, user_agent, 
         giorni_rimanenti_contestazione, contestazione_ancora_valida)
        VALUES (:payslip_id, :employee_id, :tipo, :ip, :user_agent, 
                :giorni, :valida)
    """, {
        'payslip_id': payslip_id,
        'employee_id': employee_id,
        'tipo': tipo,
        'ip': ip_address,
        'user_agent': user_agent,
        'giorni': giorni_rimanenti,
        'valida': giorni_rimanenti > 0
    })


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/buste-paga/{payslip_id}", response_model=PayslipDetailResponse)
async def get_payslip_details(
    payslip_id: int,
    request: Request,
    current_user = Depends(get_current_employee_user),
    db = Depends(get_db)
):
    """
    Visualizza dettagli busta paga con controlli temporali
    
    PRIMA VISUALIZZAZIONE:
    - Marca come visualizzato
    - Conta visualizzazione
    - Calcola giorni rimanenti per contestare
    - Mostra alert se termine vicino/scaduto
    """
    
    employee = await get_employee_by_user_id(current_user.id, db)
    
    # Recupera busta paga
    payslip = await db.fetch_one("""
        SELECT * FROM payslips
        WHERE id = :id AND employee_id = :emp_id
    """, {'id': payslip_id, 'emp_id': employee.id})
    
    if not payslip:
        raise HTTPException(404, "Busta paga non trovata")
    
    # PRIMA VISUALIZZAZIONE
    if not payslip['visualizzato_dipendente']:
        await db.execute("""
            UPDATE payslips
            SET visualizzato_dipendente = true,
                data_prima_visualizzazione = NOW(),
                numero_visualizzazioni = 1,
                ultima_visualizzazione = NOW()
            WHERE id = :id
        """, {'id': payslip_id})
        
        data_prima_visualizzazione = datetime.now()
        numero_visualizzazioni = 1
    
    else:
        # Incrementa contatore visualizzazioni
        await db.execute("""
            UPDATE payslips
            SET numero_visualizzazioni = numero_visualizzazioni + 1,
                ultima_visualizzazione = NOW()
            WHERE id = :id
        """, {'id': payslip_id})
        
        data_prima_visualizzazione = payslip['data_prima_visualizzazione']
        numero_visualizzazioni = payslip['numero_visualizzazioni'] + 1
    
    # Calcola giorni rimanenti per contestazione
    data_disponibilita = payslip['data_disponibilita']
    data_scadenza = payslip['data_scadenza_contestazione']
    giorni_rimanenti = calcola_giorni_rimanenti(data_disponibilita, data_scadenza)
    
    # Aggiorna flag scadenza se necessario
    if giorni_rimanenti <= 0 and not payslip['contestazione_scaduta']:
        await db.execute("""
            UPDATE payslips
            SET contestazione_scaduta = true
            WHERE id = :id
        """, {'id': payslip_id})
    
    # Log visualizzazione
    await log_payslip_action(
        db, payslip_id, employee.id, 'visualizzazione', 
        request, giorni_rimanenti
    )
    
    # Conta contestazioni esistenti
    contestazioni = await db.fetch_all("""
        SELECT id FROM payslip_disputes
        WHERE payslip_id = :id
    """, {'id': payslip_id})
    
    # Genera messaggio scadenza
    messaggio_scadenza = genera_messaggio_scadenza(
        giorni_rimanenti,
        data_prima_visualizzazione,
        data_disponibilita
    )
    
    return PayslipDetailResponse(
        id=payslip['id'],
        periodo=payslip['periodo'],
        anno=payslip['anno'],
        mese=payslip['mese'],
        retribuzione_lorda=payslip['retribuzione_lorda'],
        netto_in_busta=payslip['netto_in_busta'],
        stato_pagamento=payslip['stato_pagamento'],
        data_pagamento=payslip['data_pagamento'],
        pdf_disponibile=bool(payslip['pdf_view_path']),
        visualizzato=True,
        data_prima_visualizzazione=data_prima_visualizzazione,
        numero_visualizzazioni=numero_visualizzazioni,
        accettato=payslip['accettato_dipendente'],
        data_accettazione=payslip['data_accettazione'],
        data_disponibilita=data_disponibilita,
        data_scadenza_contestazione=data_scadenza,
        giorni_rimanenti_contestazione=max(0, giorni_rimanenti),
        contestazione_possibile=giorni_rimanenti > 0,
        contestazione_scaduta=giorni_rimanenti <= 0,
        messaggio_scadenza=messaggio_scadenza,
        ha_contestazioni=len(contestazioni) > 0,
        numero_contestazioni=len(contestazioni)
    )


@router.post("/buste-paga/{payslip_id}/accetta")
async def accept_payslip(
    payslip_id: int,
    request: Request,
    accept_data: PayslipAcceptRequest,
    current_user = Depends(get_current_employee_user),
    db = Depends(get_db)
):
    """
    Accetta busta paga (spunta checkbox obbligatorio)
    
    CONTROLLI:
    - Verifica che non sia già accettata
    - Salva IP e timestamp
    - Se termine scaduto: accettazione implicita già avvenuta
    """
    
    employee = await get_employee_by_user_id(current_user.id, db)
    
    payslip = await db.fetch_one("""
        SELECT * FROM payslips
        WHERE id = :id AND employee_id = :emp_id
    """, {'id': payslip_id, 'emp_id': employee.id})
    
    if not payslip:
        raise HTTPException(404, "Busta paga non trovata")
    
    if payslip['accettato_dipendente']:
        raise HTTPException(400, "Busta paga già accettata")
    
    # Salva accettazione
    ip_address = request.client.host if request.client else None
    
    await db.execute("""
        UPDATE payslips
        SET accettato_dipendente = true,
            data_accettazione = NOW(),
            ip_accettazione = :ip
        WHERE id = :id
    """, {'id': payslip_id, 'ip': ip_address})
    
    # Log azione
    giorni_rimanenti = calcola_giorni_rimanenti(
        payslip['data_disponibilita'],
        payslip['data_scadenza_contestazione']
    )
    
    await log_payslip_action(
        db, payslip_id, employee.id, 'accettazione', 
        request, giorni_rimanenti
    )
    
    return {
        'success': True,
        'message': 'Busta paga accettata correttamente',
        'data_accettazione': datetime.now(),
        'giorni_rimanenti_contestazione': max(0, giorni_rimanenti)
    }


@router.get("/buste-paga/{payslip_id}/download-pdf")
async def download_payslip_pdf(
    payslip_id: int,
    request: Request,
    current_user = Depends(get_current_employee_user),
    db = Depends(get_db)
):
    """
    Scarica PDF busta paga (versione senza password)
    
    VINCOLO: Dipendente DEVE aver accettato prima di scaricare
    """
    
    employee = await get_employee_by_user_id(current_user.id, db)
    
    payslip = await db.fetch_one("""
        SELECT * FROM payslips
        WHERE id = :id AND employee_id = :emp_id
    """, {'id': payslip_id, 'emp_id': employee.id})
    
    if not payslip:
        raise HTTPException(404, "Busta paga non trovata")
    
    # CONTROLLO: Deve aver accettato
    if not payslip['accettato_dipendente']:
        raise HTTPException(
            403, 
            "Devi prima accettare la busta paga per poterla scaricare"
        )
    
    if not payslip['pdf_view_path']:
        raise HTTPException(404, "PDF non disponibile")
    
    # Log download
    giorni_rimanenti = calcola_giorni_rimanenti(
        payslip['data_disponibilita'],
        payslip['data_scadenza_contestazione']
    )
    
    await log_payslip_action(
        db, payslip_id, employee.id, 'download_pdf', 
        request, giorni_rimanenti
    )
    
    filename = f"BustaPaga_{payslip['periodo']}_{employee.cognome}_{employee.nome}.pdf"
    
    return FileResponse(
        payslip['pdf_view_path'],
        media_type='application/pdf',
        filename=filename
    )


@router.get("/buste-paga/{payslip_id}/download-modulo-contestazione")
async def download_dispute_form(
    payslip_id: int,
    request: Request,
    current_user = Depends(get_current_employee_user),
    db = Depends(get_db)
):
    """
    Scarica modulo contestazione (DOCX)
    
    CONTROLLI:
    - Verifica che termine non sia scaduto
    - Se scaduto: blocca download e mostra messaggio
    - Log download modulo
    """
    
    employee = await get_employee_by_user_id(current_user.id, db)
    
    payslip = await db.fetch_one("""
        SELECT * FROM payslips
        WHERE id = :id AND employee_id = :emp_id
    """, {'id': payslip_id, 'emp_id': employee.id})
    
    if not payslip:
        raise HTTPException(404, "Busta paga non trovata")
    
    # Calcola giorni rimanenti
    giorni_rimanenti = calcola_giorni_rimanenti(
        payslip['data_disponibilita'],
        payslip['data_scadenza_contestazione']
    )
    
    # CONTROLLO: Termine scaduto
    if giorni_rimanenti <= 0:
        giorni_scaduti = abs(giorni_rimanenti)
        raise HTTPException(
            403,
            f"Termine di contestazione scaduto da {giorni_scaduti} giorni. "
            f"La busta paga era disponibile dal {payslip['data_disponibilita'].strftime('%d/%m/%Y')} "
            f"e poteva essere contestata entro 180 giorni "
            f"(scadenza: {payslip['data_scadenza_contestazione'].strftime('%d/%m/%Y')}). "
            f"L'accettazione tacita del pagamento comporta la decadenza dal diritto di contestazione."
        )
    
    # Marca download modulo
    await db.execute("""
        UPDATE payslips
        SET modulo_contestazione_scaricato = true,
            data_download_modulo = NOW()
        WHERE id = :id
    """, {'id': payslip_id})
    
    # Log download
    await log_payslip_action(
        db, payslip_id, employee.id, 'download_modulo', 
        request, giorni_rimanenti
    )
    
    modulo_path = '/home/claude/azienda-cloud/backend/templates/MODULO_CONTESTAZIONE_BUSTA_PAGA.docx'
    
    filename = f"Modulo_Contestazione_BustaPaga_{payslip['periodo']}.docx"
    
    return FileResponse(
        modulo_path,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename=filename
    )


@router.post("/buste-paga/{payslip_id}/contesta")
async def create_dispute(
    payslip_id: int,
    request: Request,
    dispute_data: PayslipDisputeCreate,
    current_user = Depends(get_current_employee_user),
    db = Depends(get_db)
):
    """
    Crea contestazione busta paga
    
    CONTROLLI RIGOROSI:
    - Verifica termine 180 giorni dalla data disponibilità
    - Se scaduto: BLOCCA e mostra messaggio
    - Calcola differenza se importi forniti
    - Salva tutto per tracciabilità legale
    """
    
    employee = await get_employee_by_user_id(current_user.id, db)
    
    payslip = await db.fetch_one("""
        SELECT * FROM payslips
        WHERE id = :id AND employee_id = :emp_id
    """, {'id': payslip_id, 'emp_id': employee.id})
    
    if not payslip:
        raise HTTPException(404, "Busta paga non trovata")
    
    # CALCOLA GIORNI RIMANENTI
    data_disponibilita = payslip['data_disponibilita']
    data_scadenza = payslip['data_scadenza_contestazione']
    giorni_rimanenti = calcola_giorni_rimanenti(data_disponibilita, data_scadenza)
    
    # CONTROLLO TERMINE SCADUTO
    if giorni_rimanenti <= 0:
        giorni_scaduti = abs(giorni_rimanenti)
        raise HTTPException(
            403,
            f"❌ Contestazione NON VALIDA: termine scaduto da {giorni_scaduti} giorni.\n\n"
            f"📅 Data disponibilità busta: {data_disponibilita.strftime('%d/%m/%Y')}\n"
            f"⏰ Termine contestazione: {data_scadenza.strftime('%d/%m/%Y')}\n"
            f"📆 Data odierna: {date.today().strftime('%d/%m/%Y')}\n\n"
            f"⚖️ Secondo la Legge 11 gennaio 1943, n. 4, il lavoratore ha 180 giorni "
            f"dalla data di messa a disposizione della busta paga per contestare anomalie. "
            f"Il termine è decorso e non è più possibile presentare contestazione."
        )
    
    # Calcola differenza se importi forniti
    differenza = None
    if dispute_data.importo_indicato and dispute_data.importo_ritenuto_corretto:
        differenza = dispute_data.importo_ritenuto_corretto - dispute_data.importo_indicato
    
    # CREA CONTESTAZIONE
    dispute_id = await db.execute("""
        INSERT INTO payslip_disputes (
            payslip_id, employee_id,
            data_contestazione, data_creazione_contestazione,
            data_disponibilita_busta, data_scadenza,
            giorni_rimanenti, contestazione_valida,
            tipo_anomalia, descrizione,
            importo_indicato, importo_ritenuto_corretto, differenza,
            presentazione, stato
        ) VALUES (
            :payslip_id, :employee_id,
            :data_cont, NOW(),
            :data_disp, :data_scad,
            :giorni, true,
            :tipo, :desc,
            :imp_ind, :imp_corr, :diff,
            :pres, 'in_attesa'
        ) RETURNING id
    """, {
        'payslip_id': payslip_id,
        'employee_id': employee.id,
        'data_cont': date.today(),
        'data_disp': data_disponibilita,
        'data_scad': data_scadenza,
        'giorni': giorni_rimanenti,
        'tipo': dispute_data.tipo_anomalia,
        'desc': dispute_data.descrizione,
        'imp_ind': dispute_data.importo_indicato,
        'imp_corr': dispute_data.importo_ritenuto_corretto,
        'diff': differenza,
        'pres': dispute_data.presentazione
    })
    
    # Log azione
    await log_payslip_action(
        db, payslip_id, employee.id, 'contestazione_creata', 
        request, giorni_rimanenti
    )
    
    # TODO: Invia notifica a HR/Amministrazione
    
    return {
        'success': True,
        'message': 'Contestazione registrata correttamente',
        'dispute_id': dispute_id,
        'giorni_rimanenti': giorni_rimanenti,
        'data_scadenza': data_scadenza.strftime('%d/%m/%Y'),
        'nota': 'La contestazione verrà esaminata dall\'ufficio HR. Riceverai risposta via email.'
    }


@router.get("/buste-paga/{payslip_id}/contestazioni")
async def get_payslip_disputes(
    payslip_id: int,
    current_user = Depends(get_current_employee_user),
    db = Depends(get_db)
):
    """Lista contestazioni per una busta paga"""
    
    employee = await get_employee_by_user_id(current_user.id, db)
    
    disputes = await db.fetch_all("""
        SELECT 
            id, tipo_anomalia, descrizione,
            importo_indicato, importo_ritenuto_corretto, differenza,
            data_contestazione, giorni_rimanenti, contestazione_valida,
            stato, risposta, data_gestione,
            created_at
        FROM payslip_disputes
        WHERE payslip_id = :payslip_id AND employee_id = :emp_id
        ORDER BY created_at DESC
    """, {'payslip_id': payslip_id, 'emp_id': employee.id})
    
    return {
        'success': True,
        'contestazioni': [dict(d) for d in disputes]
    }
