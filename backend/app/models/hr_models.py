"""
Modelli Pydantic per Sistema HR
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# ============================================================================
# EMPLOYEE MODELS
# ============================================================================

class EmployeeBase(BaseModel):
    nome: str = Field(..., max_length=100)
    cognome: str = Field(..., max_length=100)
    codice_fiscale: str = Field(..., min_length=16, max_length=16)
    data_nascita: Optional[date] = None
    luogo_nascita: Optional[str] = None
    indirizzo: Optional[str] = None
    cap: Optional[str] = Field(None, max_length=5)
    citta: Optional[str] = None
    provincia: Optional[str] = Field(None, max_length=2)
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    
    @validator('codice_fiscale')
    def validate_cf(cls, v):
        return v.upper().strip()


class EmployeeCreate(EmployeeBase):
    codice_dipendente: Optional[str] = None
    data_assunzione: date
    tipo_contratto: str = Field(..., pattern='^(determinato|indeterminato)$')
    tipo_orario: str = Field(..., pattern='^(full-time|part-time)$')
    percentuale_part_time: Optional[Decimal] = None
    livello: str
    mansione: str
    stipendio_base: Decimal
    iban: Optional[str] = None
    banca: Optional[str] = None


class EmployeeUpdate(BaseModel):
    nome: Optional[str] = None
    cognome: Optional[str] = None
    indirizzo: Optional[str] = None
    cap: Optional[str] = None
    citta: Optional[str] = None
    provincia: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    iban: Optional[str] = None
    banca: Optional[str] = None
    stipendio_base: Optional[Decimal] = None
    stato: Optional[str] = Field(None, pattern='^(attivo|cessato|sospeso)$')


class EmployeeResponse(EmployeeBase):
    id: int
    codice_dipendente: Optional[str]
    data_assunzione: Optional[date]
    data_cessazione: Optional[date]
    tipo_contratto: Optional[str]
    tipo_orario: Optional[str]
    percentuale_part_time: Optional[Decimal]
    livello: Optional[str]
    mansione: Optional[str]
    iban: Optional[str]
    banca: Optional[str]
    stipendio_base: Optional[Decimal]
    user_id: Optional[int]
    stato: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# PAYSLIP MODELS
# ============================================================================

class PayslipBase(BaseModel):
    periodo: str = Field(..., pattern=r'^\d{4}-\d{2}$')
    anno: int
    mese: int


class PayslipCreate(PayslipBase):
    employee_id: int
    retribuzione_lorda: Decimal
    netto_in_busta: Decimal
    inps_dipendente: Optional[Decimal] = Decimal('0')
    inps_azienda: Optional[Decimal] = Decimal('0')
    irpef: Optional[Decimal] = Decimal('0')
    addizionale_regionale: Optional[Decimal] = Decimal('0')
    addizionale_comunale: Optional[Decimal] = Decimal('0')
    altre_trattenute: Optional[Decimal] = Decimal('0')
    tfr_maturato: Optional[Decimal] = Decimal('0')
    tfr_progressivo: Optional[Decimal] = Decimal('0')
    ferie_maturate: Optional[Decimal] = Decimal('0')
    ferie_godute: Optional[Decimal] = Decimal('0')
    ferie_residue: Optional[Decimal] = Decimal('0')
    permessi_maturati: Optional[Decimal] = Decimal('0')
    permessi_goduti: Optional[Decimal] = Decimal('0')
    permessi_residui: Optional[Decimal] = Decimal('0')
    ore_ordinarie: Optional[Decimal] = Decimal('0')
    ore_straordinarie: Optional[Decimal] = Decimal('0')
    giorni_lavorati: Optional[int] = 0
    pdf_original_path: Optional[str] = None
    pdf_view_path: Optional[str] = None


class PayslipResponse(PayslipBase):
    id: int
    employee_id: int
    retribuzione_lorda: Decimal
    netto_in_busta: Decimal
    inps_dipendente: Decimal
    inps_azienda: Decimal
    irpef: Decimal
    addizionale_regionale: Decimal
    addizionale_comunale: Decimal
    altre_trattenute: Decimal
    tfr_maturato: Decimal
    tfr_progressivo: Decimal
    ferie_maturate: Decimal
    ferie_godute: Decimal
    ferie_residue: Decimal
    permessi_maturati: Decimal
    permessi_goduti: Decimal
    permessi_residui: Decimal
    ore_ordinarie: Decimal
    ore_straordinarie: Decimal
    giorni_lavorati: int
    pdf_original_path: Optional[str]
    pdf_view_path: Optional[str]
    stato_pagamento: str
    data_pagamento: Optional[date]
    notificato_dipendente: bool
    visualizzato_dipendente: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# CONTRACT MODELS
# ============================================================================

class ContractCreate(BaseModel):
    employee_id: int
    tipo_contratto: str = Field(..., pattern='^(determinato|indeterminato)$')
    tipo_orario: str = Field(..., pattern='^(full-time|part-time)$')
    percentuale_part_time: Optional[Decimal] = None
    data_inizio: date
    data_fine: Optional[date] = None
    mansione: str
    livello: str
    retribuzione_oraria: Decimal
    template_used: str
    
    @validator('data_fine')
    def validate_dates(cls, v, values):
        if v and 'data_inizio' in values and v <= values['data_inizio']:
            raise ValueError('Data fine deve essere successiva a data inizio')
        return v


class ContractResponse(BaseModel):
    id: int
    employee_id: int
    tipo_contratto: str
    tipo_orario: str
    percentuale_part_time: Optional[Decimal]
    data_inizio: date
    data_fine: Optional[date]
    mansione: str
    livello: str
    retribuzione_oraria: Decimal
    template_used: str
    pdf_path: Optional[str]
    firmato: bool
    data_firma: Optional[datetime]
    stato: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# ATTENDANCE MODELS
# ============================================================================

class AttendanceCreate(BaseModel):
    employee_id: int
    data: date
    tipo: str = Field(..., pattern='^(lavoro|ferie|malattia|permesso|assenza|festivo)$')
    ore_lavorate: Decimal = Decimal('0')
    ore_straordinarie: Decimal = Decimal('0')
    codice_giustificativo: Optional[str] = None
    descrizione_giustificativo: Optional[str] = None
    note: Optional[str] = None


class AttendanceResponse(AttendanceCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# LEAVE REQUEST MODELS
# ============================================================================

class LeaveRequestCreate(BaseModel):
    tipo: str = Field(..., pattern='^(ferie|permesso|malattia)$')
    data_inizio: date
    data_fine: date
    motivo: Optional[str] = None
    
    @validator('data_fine')
    def validate_dates(cls, v, values):
        if 'data_inizio' in values and v < values['data_inizio']:
            raise ValueError('Data fine deve essere >= data inizio')
        return v


class LeaveRequestResponse(BaseModel):
    id: int
    employee_id: int
    tipo: str
    data_inizio: date
    data_fine: date
    giorni_richiesti: Decimal
    ore_richieste: Optional[Decimal]
    motivo: Optional[str]
    stato: str
    approvato_da: Optional[int]
    data_approvazione: Optional[datetime]
    note_approvazione: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LeaveRequestApprove(BaseModel):
    approvato: bool
    note: Optional[str] = None


# ============================================================================
# DASHBOARD MODELS
# ============================================================================

class EmployeeDashboard(BaseModel):
    employee: EmployeeResponse
    ultima_busta_paga: Optional[PayslipResponse]
    ferie_residue: Decimal
    permessi_residui: Decimal
    richieste_ferie_pendenti: List[LeaveRequestResponse]
    notifiche_non_lette: int


class HRStatistics(BaseModel):
    totale_dipendenti: int
    dipendenti_attivi: int
    dipendenti_cessati: int
    buste_paga_da_pagare: int
    richieste_ferie_pendenti: int
    costo_mensile_stipendi: Decimal
