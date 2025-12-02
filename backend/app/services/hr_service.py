"""
HR Service - Business Logic per gestione dipendenti, buste paga, contratti
"""
from typing import Optional, List, Dict
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
import os
from .payslip_parser import PayslipParser
from .pdf_utils import PDFUtils


class HRService:
    """Service per gestione HR completa"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.parser = PayslipParser()
        self.pdf_utils = PDFUtils()
    
    # ========================================================================
    # EMPLOYEE MANAGEMENT
    # ========================================================================
    
    async def create_employee(self, employee_data: dict) -> int:
        """Crea nuovo dipendente"""
        
        # Auto-genera codice dipendente se non fornito
        if not employee_data.get('codice_dipendente'):
            employee_data['codice_dipendente'] = await self._generate_employee_code()
        
        query = """
            INSERT INTO employees (
                codice_dipendente, nome, cognome, codice_fiscale,
                data_nascita, luogo_nascita, indirizzo, cap, citta, provincia,
                telefono, email, data_assunzione, tipo_contratto, tipo_orario,
                percentuale_part_time, livello, mansione, stipendio_base,
                iban, banca, stato
            ) VALUES (
                :codice, :nome, :cognome, :cf,
                :data_nasc, :luogo_nasc, :indirizzo, :cap, :citta, :prov,
                :tel, :email, :data_ass, :tipo_contr, :tipo_or,
                :perc_pt, :livello, :mansione, :stipendio,
                :iban, :banca, 'attivo'
            ) RETURNING id
        """
        
        employee_id = await self.db.execute(query, employee_data)
        
        return employee_id
    
    async def _generate_employee_code(self) -> str:
        """Genera codice dipendente univoco (es: DIP001)"""
        
        last_code = await self.db.fetch_val("""
            SELECT codice_dipendente FROM employees
            WHERE codice_dipendente LIKE 'DIP%'
            ORDER BY id DESC LIMIT 1
        """)
        
        if not last_code:
            return 'DIP001'
        
        num = int(last_code[3:]) + 1
        return f'DIP{num:03d}'
    
    async def get_employee_by_cf(self, codice_fiscale: str) -> Optional[dict]:
        """Trova dipendente per codice fiscale"""
        
        employee = await self.db.fetch_one("""
            SELECT * FROM employees
            WHERE codice_fiscale = :cf
        """, {'cf': codice_fiscale.upper()})
        
        return dict(employee) if employee else None
    
    async def get_active_employees(self) -> List[dict]:
        """Lista dipendenti attivi"""
        
        employees = await self.db.fetch_all("""
            SELECT * FROM employees
            WHERE stato = 'attivo'
            ORDER BY cognome, nome
        """)
        
        return [dict(e) for e in employees]
    
    async def terminate_employee(self, employee_id: int, data_cessazione: date):
        """Cessazione dipendente"""
        
        await self.db.execute("""
            UPDATE employees
            SET stato = 'cessato',
                data_cessazione = :data
            WHERE id = :id
        """, {'id': employee_id, 'data': data_cessazione})
    
    # ========================================================================
    # PAYSLIP MANAGEMENT
    # ========================================================================
    
    async def import_payslip_from_pdf(
        self, 
        pdf_data: bytes, 
        pdf_filename: str,
        data_disponibilita: Optional[date] = None
    ) -> Dict:
        """
        Importa busta paga da PDF
        
        1. Parse PDF ed estrai dati
        2. Trova dipendente per CF
        3. Genera PDF senza password per dipendente
        4. Salva in database
        5. Calcola scadenza contestazione
        """
        
        # 1. PARSE PDF
        parsed_data = self.parser.parse_pdf(pdf_data)
        
        if not parsed_data:
            return {'success': False, 'error': 'Impossibile parsare PDF'}
        
        if not parsed_data.get('codice_fiscale'):
            return {'success': False, 'error': 'Codice fiscale non trovato nel PDF'}
        
        # 2. TROVA DIPENDENTE
        employee = await self.get_employee_by_cf(parsed_data['codice_fiscale'])
        
        if not employee:
            return {
                'success': False, 
                'error': f"Dipendente non trovato con CF {parsed_data['codice_fiscale']}"
            }
        
        # 3. SALVA PDF
        upload_dir = '/home/claude/azienda-cloud/backend/uploads/payslips'
        os.makedirs(upload_dir, exist_ok=True)
        
        # PDF originale (con password)
        original_filename = f"payslip_{employee['id']}_{parsed_data['periodo']}_original.pdf"
        original_path = os.path.join(upload_dir, original_filename)
        
        with open(original_path, 'wb') as f:
            f.write(pdf_data)
        
        # PDF per dipendente (senza password)
        view_filename = f"payslip_{employee['id']}_{parsed_data['periodo']}_view.pdf"
        view_path = os.path.join(upload_dir, view_filename)
        
        # Rimuovi password se presente
        pdf_unlocked = self.pdf_utils.remove_pdf_password(pdf_data)
        
        with open(view_path, 'wb') as f:
            f.write(pdf_unlocked if pdf_unlocked else pdf_data)
        
        # 4. CALCOLA DATE CONTESTAZIONE
        if not data_disponibilita:
            data_disponibilita = date.today()
        
        data_scadenza_contestazione = data_disponibilita + timedelta(days=180)
        
        # 5. SALVA IN DATABASE
        payslip_data = {
            'employee_id': employee['id'],
            'periodo': parsed_data['periodo'],
            'anno': parsed_data['anno'],
            'mese': parsed_data['mese'],
            'retribuzione_lorda': parsed_data.get('retribuzione_lorda', Decimal('0')),
            'netto_in_busta': parsed_data.get('netto_in_busta', Decimal('0')),
            'inps_dipendente': parsed_data.get('inps_dipendente', Decimal('0')),
            'inps_azienda': parsed_data.get('inps_azienda', Decimal('0')),
            'irpef': parsed_data.get('irpef', Decimal('0')),
            'addizionale_regionale': parsed_data.get('addizionale_regionale', Decimal('0')),
            'addizionale_comunale': parsed_data.get('addizionale_comunale', Decimal('0')),
            'altre_trattenute': parsed_data.get('altre_trattenute', Decimal('0')),
            'tfr_maturato': parsed_data.get('tfr_maturato', Decimal('0')),
            'tfr_progressivo': parsed_data.get('tfr_progressivo', Decimal('0')),
            'ferie_maturate': parsed_data.get('ferie_maturate', Decimal('0')),
            'ferie_godute': parsed_data.get('ferie_godute', Decimal('0')),
            'ferie_residue': parsed_data.get('ferie_residue', Decimal('0')),
            'permessi_maturati': parsed_data.get('permessi_maturati', Decimal('0')),
            'permessi_goduti': parsed_data.get('permessi_goduti', Decimal('0')),
            'permessi_residui': parsed_data.get('permessi_residui', Decimal('0')),
            'ore_ordinarie': parsed_data.get('ore_ordinarie', Decimal('0')),
            'ore_straordinarie': parsed_data.get('ore_straordinarie', Decimal('0')),
            'giorni_lavorati': parsed_data.get('giorni_lavorati', 0),
            'pdf_original_path': original_path,
            'pdf_view_path': view_path,
            'data_disponibilita': data_disponibilita,
            'data_scadenza_contestazione': data_scadenza_contestazione
        }
        
        # Controlla se esiste già
        existing = await self.db.fetch_one("""
            SELECT id FROM payslips
            WHERE employee_id = :emp_id AND periodo = :periodo
        """, {'emp_id': employee['id'], 'periodo': parsed_data['periodo']})
        
        if existing:
            # Aggiorna
            await self.db.execute("""
                UPDATE payslips SET
                    retribuzione_lorda = :retribuzione_lorda,
                    netto_in_busta = :netto_in_busta,
                    inps_dipendente = :inps_dipendente,
                    inps_azienda = :inps_azienda,
                    irpef = :irpef,
                    ore_ordinarie = :ore_ordinarie,
                    pdf_original_path = :pdf_original_path,
                    pdf_view_path = :pdf_view_path,
                    updated_at = NOW()
                WHERE id = :id
            """, {**payslip_data, 'id': existing['id']})
            
            payslip_id = existing['id']
            action = 'updated'
        else:
            # Inserisci
            payslip_id = await self.db.execute("""
                INSERT INTO payslips (
                    employee_id, periodo, anno, mese,
                    retribuzione_lorda, netto_in_busta,
                    inps_dipendente, inps_azienda, irpef,
                    addizionale_regionale, addizionale_comunale, altre_trattenute,
                    tfr_maturato, tfr_progressivo,
                    ferie_maturate, ferie_godute, ferie_residue,
                    permessi_maturati, permessi_goduti, permessi_residui,
                    ore_ordinarie, ore_straordinarie, giorni_lavorati,
                    pdf_original_path, pdf_view_path,
                    data_disponibilita, data_scadenza_contestazione,
                    stato_pagamento
                ) VALUES (
                    :employee_id, :periodo, :anno, :mese,
                    :retribuzione_lorda, :netto_in_busta,
                    :inps_dipendente, :inps_azienda, :irpef,
                    :addizionale_regionale, :addizionale_comunale, :altre_trattenute,
                    :tfr_maturato, :tfr_progressivo,
                    :ferie_maturate, :ferie_godute, :ferie_residue,
                    :permessi_maturati, :permessi_goduti, :permessi_residui,
                    :ore_ordinarie, :ore_straordinarie, :giorni_lavorati,
                    :pdf_original_path, :pdf_view_path,
                    :data_disponibilita, :data_scadenza_contestazione,
                    'da_pagare'
                ) RETURNING id
            """, payslip_data)
            
            action = 'created'
        
        # 6. AGGIORNA DATI DIPENDENTE SE NECESSARIO
        if parsed_data.get('iban') and not employee.get('iban'):
            await self.db.execute("""
                UPDATE employees SET iban = :iban, banca = :banca
                WHERE id = :id
            """, {
                'id': employee['id'],
                'iban': parsed_data['iban'],
                'banca': parsed_data.get('banca')
            })
        
        return {
            'success': True,
            'action': action,
            'payslip_id': payslip_id,
            'employee': employee,
            'periodo': parsed_data['periodo'],
            'netto': parsed_data.get('netto_in_busta'),
            'data_disponibilita': data_disponibilita,
            'data_scadenza_contestazione': data_scadenza_contestazione
        }
    
    async def get_employee_payslips(
        self, 
        employee_id: int, 
        limit: int = 12
    ) -> List[dict]:
        """Lista buste paga dipendente (ultime 12)"""
        
        payslips = await self.db.fetch_all("""
            SELECT * FROM payslips
            WHERE employee_id = :emp_id
            ORDER BY anno DESC, mese DESC
            LIMIT :limit
        """, {'emp_id': employee_id, 'limit': limit})
        
        return [dict(p) for p in payslips]
    
    async def create_prima_nota_from_payslip(self, payslip_id: int) -> int:
        """
        Crea registrazione prima nota da busta paga
        
        DARE:
        - Salari e Stipendi (retribuzione_lorda)
        - Oneri Sociali Azienda (inps_azienda)
        - TFR Accantonamento (tfr_maturato)
        
        AVERE:
        - Debiti vs Dipendenti (netto_in_busta)
        - Debiti vs INPS (inps_dipendente + inps_azienda)
        - Debiti vs Erario (irpef + addizionali)
        - Debiti TFR (tfr_maturato)
        """
        
        payslip = await self.db.fetch_one("""
            SELECT p.*, e.nome, e.cognome
            FROM payslips p
            JOIN employees e ON p.employee_id = e.id
            WHERE p.id = :id
        """, {'id': payslip_id})
        
        if not payslip:
            raise ValueError("Payslip non trovata")
        
        # Calcoli
        salari = payslip['retribuzione_lorda']
        oneri_azienda = payslip['inps_azienda']
        tfr = payslip['tfr_maturato']
        
        debiti_dipendenti = payslip['netto_in_busta']
        debiti_inps = payslip['inps_dipendente'] + payslip['inps_azienda']
        debiti_erario = (
            payslip['irpef'] + 
            payslip['addizionale_regionale'] + 
            payslip['addizionale_comunale']
        )
        debiti_tfr = tfr
        
        totale_dare = salari + oneri_azienda + tfr
        totale_avere = debiti_dipendenti + debiti_inps + debiti_erario + debiti_tfr
        
        # Verifica quadratura
        if abs(totale_dare - totale_avere) > Decimal('0.01'):
            raise ValueError(f"Prima nota non quadra: DARE={totale_dare}, AVERE={totale_avere}")
        
        # Crea registrazione
        prima_nota_id = await self.db.execute("""
            INSERT INTO prima_nota_salari (
                payslip_id, employee_id,
                data_registrazione, periodo,
                descrizione,
                salari_stipendi, oneri_sociali_azienda, tfr_accantonamento,
                debiti_vs_dipendenti, debiti_vs_inps, debiti_vs_erario, debiti_tfr,
                totale_dare, totale_avere
            ) VALUES (
                :payslip_id, :emp_id,
                :data, :periodo,
                :desc,
                :salari, :oneri, :tfr,
                :deb_dip, :deb_inps, :deb_erario, :deb_tfr,
                :tot_dare, :tot_avere
            ) RETURNING id
        """, {
            'payslip_id': payslip_id,
            'emp_id': payslip['employee_id'],
            'data': date.today(),
            'periodo': payslip['periodo'],
            'desc': f"Busta paga {payslip['periodo']} - {payslip['nome']} {payslip['cognome']}",
            'salari': salari,
            'oneri': oneri_azienda,
            'tfr': tfr,
            'deb_dip': debiti_dipendenti,
            'deb_inps': debiti_inps,
            'deb_erario': debiti_erario,
            'deb_tfr': debiti_tfr,
            'tot_dare': totale_dare,
            'tot_avere': totale_avere
        })
        
        # Aggiorna payslip
        await self.db.execute("""
            UPDATE payslips
            SET prima_nota_id = :pn_id
            WHERE id = :id
        """, {'pn_id': prima_nota_id, 'id': payslip_id})
        
        return prima_nota_id
    
    # ========================================================================
    # CONTRACT MANAGEMENT
    # ========================================================================
    
    async def create_contract_from_template(
        self,
        employee_id: int,
        template_name: str,
        contract_data: dict
    ) -> int:
        """
        Crea contratto da template
        
        Templates disponibili:
        - contratto_determinato
        - contratto_indeterminato
        - contratto_part_time
        """
        
        from .contract_generator import ContractGenerator
        
        generator = ContractGenerator()
        
        # Genera contratto
        docx_path, pdf_path = await generator.generate_contract(
            template_name,
            employee_id,
            contract_data
        )
        
        # Salva in database
        contract_id = await self.db.execute("""
            INSERT INTO contracts (
                employee_id, tipo_contratto, tipo_orario,
                percentuale_part_time, data_inizio, data_fine,
                mansione, livello, retribuzione_oraria,
                template_used, docx_path, pdf_path,
                stato
            ) VALUES (
                :emp_id, :tipo_contr, :tipo_or,
                :perc_pt, :data_in, :data_fin,
                :mansione, :livello, :retr_or,
                :template, :docx, :pdf,
                'bozza'
            ) RETURNING id
        """, {
            'emp_id': employee_id,
            'tipo_contr': contract_data['tipo_contratto'],
            'tipo_or': contract_data['tipo_orario'],
            'perc_pt': contract_data.get('percentuale_part_time'),
            'data_in': contract_data['data_inizio'],
            'data_fin': contract_data.get('data_fine'),
            'mansione': contract_data['mansione'],
            'livello': contract_data['livello'],
            'retr_or': contract_data['retribuzione_oraria'],
            'template': template_name,
            'docx': docx_path,
            'pdf': pdf_path
        })
        
        return contract_id
    
    # ========================================================================
    # LEAVE REQUESTS
    # ========================================================================
    
    async def create_leave_request(
        self,
        employee_id: int,
        tipo: str,
        data_inizio: date,
        data_fine: date,
        motivo: Optional[str] = None
    ) -> int:
        """Crea richiesta ferie/permesso"""
        
        # Calcola giorni richiesti
        giorni = (data_fine - data_inizio).days + 1
        
        leave_id = await self.db.execute("""
            INSERT INTO leave_requests (
                employee_id, tipo, data_inizio, data_fine,
                giorni_richiesti, motivo, stato
            ) VALUES (
                :emp_id, :tipo, :data_in, :data_fin,
                :giorni, :motivo, 'in_attesa'
            ) RETURNING id
        """, {
            'emp_id': employee_id,
            'tipo': tipo,
            'data_in': data_inizio,
            'data_fin': data_fine,
            'giorni': giorni,
            'motivo': motivo
        })
        
        return leave_id
    
    async def approve_leave_request(
        self,
        request_id: int,
        approved_by_user_id: int,
        note: Optional[str] = None
    ) -> bool:
        """Approva richiesta ferie"""
        
        await self.db.execute("""
            UPDATE leave_requests
            SET stato = 'approvato',
                approvato_da = :user_id,
                data_approvazione = NOW(),
                note_approvazione = :note
            WHERE id = :id
        """, {
            'id': request_id,
            'user_id': approved_by_user_id,
            'note': note
        })
        
        # TODO: Crea attendances per i giorni approvati
        
        return True
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    async def get_hr_statistics(self) -> dict:
        """Statistiche HR dashboard"""
        
        stats = await self.db.fetch_one("""
            SELECT
                COUNT(*) FILTER (WHERE stato = 'attivo') as totale_attivi,
                COUNT(*) FILTER (WHERE stato = 'cessato') as totale_cessati,
                COUNT(*) as totale_dipendenti
            FROM employees
        """)
        
        buste_paga = await self.db.fetch_one("""
            SELECT
                COUNT(*) FILTER (WHERE stato_pagamento = 'da_pagare') as da_pagare,
                SUM(netto_in_busta) FILTER (WHERE stato_pagamento = 'da_pagare') as importo_da_pagare
            FROM payslips
        """)
        
        ferie = await self.db.fetch_val("""
            SELECT COUNT(*) FROM leave_requests
            WHERE stato = 'in_attesa'
        """)
        
        return {
            'dipendenti_attivi': stats['totale_attivi'],
            'dipendenti_cessati': stats['totale_cessati'],
            'totale_dipendenti': stats['totale_dipendenti'],
            'buste_paga_da_pagare': buste_paga['da_pagare'] or 0,
            'importo_da_pagare': buste_paga['importo_da_pagare'] or Decimal('0'),
            'richieste_ferie_pendenti': ferie or 0
        }
