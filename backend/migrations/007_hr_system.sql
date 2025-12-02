-- ============================================================================
-- MIGRATION 007: SISTEMA HR COMPLETO
-- Data: 2025-12-02
-- Descrizione: Gestione dipendenti, buste paga, contratti, presenze
-- ============================================================================

-- TABELLA: employees (ANAGRAFICA DIPENDENTI)
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    codice_dipendente VARCHAR(20) UNIQUE,
    nome VARCHAR(100) NOT NULL,
    cognome VARCHAR(100) NOT NULL,
    codice_fiscale VARCHAR(16) UNIQUE NOT NULL,
    data_nascita DATE,
    luogo_nascita VARCHAR(100),
    indirizzo TEXT,
    cap VARCHAR(5),
    citta VARCHAR(100),
    provincia VARCHAR(2),
    telefono VARCHAR(20),
    email VARCHAR(255),
    data_assunzione DATE,
    data_cessazione DATE,
    tipo_contratto VARCHAR(50), -- 'determinato', 'indeterminato'
    tipo_orario VARCHAR(50), -- 'full-time', 'part-time'
    percentuale_part_time DECIMAL(5,2),
    livello VARCHAR(20), -- '4 Livello', '5 Livello', '6 Livello'
    mansione VARCHAR(100), -- 'Cameriere', 'Barista', 'Cassiera', etc
    iban VARCHAR(27),
    banca VARCHAR(255),
    stipendio_base DECIMAL(10,2),
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, -- Link a login dipendente
    stato VARCHAR(20) DEFAULT 'attivo', -- 'attivo', 'cessato', 'sospeso'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indici per performance
CREATE INDEX idx_employees_cf ON employees(codice_fiscale);
CREATE INDEX idx_employees_user ON employees(user_id);
CREATE INDEX idx_employees_stato ON employees(stato);

-- TABELLA: payslips (BUSTE PAGA)
CREATE TABLE IF NOT EXISTS payslips (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    periodo VARCHAR(7) NOT NULL, -- '2025-03'
    anno INTEGER NOT NULL,
    mese INTEGER NOT NULL,
    
    -- File PDF
    pdf_original_path TEXT, -- Con password (per azienda)
    pdf_view_path TEXT, -- Senza password (per dipendente)
    pdf_password VARCHAR(100), -- Password PDF originale
    
    -- Dati estratti dalla busta
    retribuzione_lorda DECIMAL(10,2),
    netto_in_busta DECIMAL(10,2),
    
    -- Contributi
    inps_dipendente DECIMAL(10,2),
    inps_azienda DECIMAL(10,2),
    irpef DECIMAL(10,2),
    addizionale_regionale DECIMAL(10,2),
    addizionale_comunale DECIMAL(10,2),
    altre_trattenute DECIMAL(10,2),
    
    -- TFR
    tfr_maturato DECIMAL(10,2),
    tfr_progressivo DECIMAL(10,2),
    
    -- Ferie/Permessi
    ferie_maturate DECIMAL(8,2),
    ferie_godute DECIMAL(8,2),
    ferie_residue DECIMAL(8,2),
    permessi_maturati DECIMAL(8,2),
    permessi_goduti DECIMAL(8,2),
    permessi_residui DECIMAL(8,2),
    
    -- Ore lavorate
    ore_ordinarie DECIMAL(8,2),
    ore_straordinarie DECIMAL(8,2),
    giorni_lavorati INTEGER,
    
    -- Collegamento prima nota
    prima_nota_id INTEGER,
    
    -- Stato pagamento
    stato_pagamento VARCHAR(20) DEFAULT 'da_pagare', -- 'da_pagare', 'pagato', 'in_attesa'
    data_pagamento DATE,
    movimento_bancario_id INTEGER, -- Link a movimento banca
    
    -- Notifiche
    notificato_dipendente BOOLEAN DEFAULT false,
    data_notifica TIMESTAMP,
    
    -- Visualizzazione e Accettazione
    visualizzato_dipendente BOOLEAN DEFAULT false,
    data_prima_visualizzazione TIMESTAMP, -- Prima volta che apre
    numero_visualizzazioni INTEGER DEFAULT 0,
    ultima_visualizzazione TIMESTAMP, -- Ultima volta che apre
    
    -- Accettazione esplicita (spunta checkbox)
    accettato_dipendente BOOLEAN DEFAULT false,
    data_accettazione TIMESTAMP,
    ip_accettazione VARCHAR(45),
    
    -- Date cruciali per contestazione
    data_disponibilita DATE NOT NULL, -- Quando la busta è disponibile (arrivo email)
    data_scadenza_contestazione DATE NOT NULL, -- data_disponibilita + 180 giorni
    contestazione_scaduta BOOLEAN DEFAULT false, -- Flag automatico
    
    -- Download modulo contestazione
    modulo_contestazione_scaricato BOOLEAN DEFAULT false,
    data_download_modulo TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(employee_id, periodo)
);

CREATE INDEX idx_payslips_employee ON payslips(employee_id);
CREATE INDEX idx_payslips_periodo ON payslips(periodo);
CREATE INDEX idx_payslips_stato ON payslips(stato_pagamento);

-- TABELLA: prima_nota_salari (REGISTRAZIONI CONTABILI SALARI)
CREATE TABLE IF NOT EXISTS prima_nota_salari (
    id SERIAL PRIMARY KEY,
    payslip_id INTEGER REFERENCES payslips(id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    
    data_registrazione DATE NOT NULL,
    periodo VARCHAR(7), -- '2025-03'
    descrizione TEXT,
    
    -- DARE (Costi azienda)
    salari_stipendi DECIMAL(10,2) DEFAULT 0,
    oneri_sociali_azienda DECIMAL(10,2) DEFAULT 0,
    tfr_accantonamento DECIMAL(10,2) DEFAULT 0,
    
    -- AVERE (Debiti)
    debiti_vs_dipendenti DECIMAL(10,2) DEFAULT 0,
    debiti_vs_inps DECIMAL(10,2) DEFAULT 0,
    debiti_vs_erario DECIMAL(10,2) DEFAULT 0,
    debiti_tfr DECIMAL(10,2) DEFAULT 0,
    
    totale_dare DECIMAL(10,2),
    totale_avere DECIMAL(10,2),
    
    riconciliato BOOLEAN DEFAULT false,
    data_riconciliazione TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_prima_nota_salari_employee ON prima_nota_salari(employee_id);
CREATE INDEX idx_prima_nota_salari_periodo ON prima_nota_salari(periodo);

-- TABELLA: employee_payments (BONIFICI DIPENDENTI)
CREATE TABLE IF NOT EXISTS employee_payments (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    payslip_id INTEGER REFERENCES payslips(id) ON DELETE SET NULL,
    
    data_bonifico DATE NOT NULL,
    importo DECIMAL(10,2) NOT NULL,
    iban_destinatario VARCHAR(27),
    causale TEXT,
    
    -- Collegamento movimento bancario
    movimento_bancario_id INTEGER,
    riconciliato BOOLEAN DEFAULT false,
    data_riconciliazione TIMESTAMP,
    
    -- Import da file XLS banca
    file_import_path TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_employee_payments_employee ON employee_payments(employee_id);
CREATE INDEX idx_employee_payments_data ON employee_payments(data_bonifico);

-- TABELLA: attendances (PRESENZE)
CREATE TABLE IF NOT EXISTS attendances (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    
    tipo VARCHAR(20), -- 'lavoro', 'ferie', 'malattia', 'permesso', 'assenza', 'festivo'
    ore_lavorate DECIMAL(5,2) DEFAULT 0,
    ore_straordinarie DECIMAL(5,2) DEFAULT 0,
    
    codice_giustificativo VARCHAR(10), -- 'FE', 'MA', 'AI', 'AH', etc
    descrizione_giustificativo TEXT,
    note TEXT,
    
    -- Import da LibroUnico
    file_import_path TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(employee_id, data)
);

CREATE INDEX idx_attendances_employee ON attendances(employee_id);
CREATE INDEX idx_attendances_data ON attendances(data);
CREATE INDEX idx_attendances_tipo ON attendances(tipo);

-- TABELLA: contracts (CONTRATTI)
CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    
    tipo_contratto VARCHAR(50) NOT NULL, -- 'determinato', 'indeterminato'
    tipo_orario VARCHAR(50) NOT NULL, -- 'full-time', 'part-time'
    percentuale_part_time DECIMAL(5,2),
    
    data_inizio DATE NOT NULL,
    data_fine DATE,
    
    mansione VARCHAR(100),
    livello VARCHAR(20),
    retribuzione_oraria DECIMAL(10,2),
    
    -- File contratto
    template_used VARCHAR(100),
    pdf_path TEXT,
    docx_path TEXT,
    
    -- Firma digitale
    firmato BOOLEAN DEFAULT false,
    data_firma TIMESTAMP,
    firma_digitale_id VARCHAR(255), -- DocuSign ID o altro
    firma_dipendente_path TEXT,
    
    stato VARCHAR(20) DEFAULT 'bozza', -- 'bozza', 'inviato', 'firmato', 'attivo', 'scaduto'
    
    note TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_contracts_employee ON contracts(employee_id);
CREATE INDEX idx_contracts_stato ON contracts(stato);
CREATE INDEX idx_contracts_date ON contracts(data_inizio, data_fine);

-- TABELLA: leave_requests (RICHIESTE FERIE/PERMESSI)
CREATE TABLE IF NOT EXISTS leave_requests (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    
    tipo VARCHAR(20) NOT NULL, -- 'ferie', 'permesso', 'malattia'
    data_inizio DATE NOT NULL,
    data_fine DATE NOT NULL,
    giorni_richiesti DECIMAL(5,2) NOT NULL,
    ore_richieste DECIMAL(5,2),
    
    motivo TEXT,
    
    stato VARCHAR(20) DEFAULT 'in_attesa', -- 'in_attesa', 'approvato', 'rifiutato', 'annullato'
    approvato_da INTEGER REFERENCES users(id) ON DELETE SET NULL,
    data_approvazione TIMESTAMP,
    note_approvazione TEXT,
    
    -- Documento allegato (es. certificato medico)
    documento_path TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_leave_requests_employee ON leave_requests(employee_id);
CREATE INDEX idx_leave_requests_stato ON leave_requests(stato);
CREATE INDEX idx_leave_requests_date ON leave_requests(data_inizio, data_fine);

-- TABELLA: employee_documents (DOCUMENTI DIPENDENTE)
CREATE TABLE IF NOT EXISTS employee_documents (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    
    tipo VARCHAR(50) NOT NULL, -- 'contratto', 'busta_paga', 'certificato', 'privacy', 'regolamento'
    titolo VARCHAR(255) NOT NULL,
    descrizione TEXT,
    
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    
    -- Visibilità
    visibile_dipendente BOOLEAN DEFAULT true,
    visualizzato_dipendente BOOLEAN DEFAULT false,
    data_visualizzazione TIMESTAMP,
    
    -- Chi ha caricato
    caricato_da INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_employee_documents_employee ON employee_documents(employee_id);
CREATE INDEX idx_employee_documents_tipo ON employee_documents(tipo);

-- TABELLA: hr_notifications (NOTIFICHE HR)
CREATE TABLE IF NOT EXISTS hr_notifications (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    tipo VARCHAR(50) NOT NULL, -- 'nuova_busta_paga', 'pagamento_ricevuto', 'ferie_approvate', etc
    titolo VARCHAR(255) NOT NULL,
    messaggio TEXT,
    
    link_url TEXT,
    
    letta BOOLEAN DEFAULT false,
    data_lettura TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_hr_notifications_user ON hr_notifications(user_id);
CREATE INDEX idx_hr_notifications_letta ON hr_notifications(letta);

-- TABELLA: email_import_log (LOG IMPORT EMAIL)
CREATE TABLE IF NOT EXISTS email_import_log (
    id SERIAL PRIMARY KEY,
    
    email_from VARCHAR(255),
    email_subject TEXT,
    email_date TIMESTAMP,
    
    tipo_documento VARCHAR(50), -- 'busta_paga', 'f24', 'altro'
    filename VARCHAR(255),
    
    employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    payslip_id INTEGER REFERENCES payslips(id) ON DELETE SET NULL,
    
    stato VARCHAR(20), -- 'successo', 'errore', 'skip'
    errore TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_email_import_log_date ON email_import_log(email_date);
CREATE INDEX idx_email_import_log_stato ON email_import_log(stato);

-- TABELLA: payslip_disputes (CONTESTAZIONI BUSTE PAGA)
CREATE TABLE IF NOT EXISTS payslip_disputes (
    id SERIAL PRIMARY KEY,
    payslip_id INTEGER REFERENCES payslips(id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    
    data_contestazione DATE NOT NULL,
    data_creazione_contestazione TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Verifica scadenza
    data_disponibilita_busta DATE NOT NULL, -- Dalla payslip
    data_scadenza DATE NOT NULL, -- data_disponibilita + 180 giorni
    giorni_rimanenti INTEGER, -- Calcolato: scadenza - creazione
    contestazione_valida BOOLEAN DEFAULT true, -- false se fuori termine
    
    -- Tipo anomalia
    tipo_anomalia VARCHAR(50) NOT NULL, -- 'retribuzione', 'ore', 'contributi', 'irpef', 'ferie', 'tfr', 'altro'
    descrizione TEXT NOT NULL,
    
    -- Importi (opzionale)
    importo_indicato DECIMAL(10,2),
    importo_ritenuto_corretto DECIMAL(10,2),
    differenza DECIMAL(10,2),
    
    -- Documento allegato (modulo compilato)
    documento_path TEXT,
    presentazione VARCHAR(20) DEFAULT 'portale', -- 'portale', 'email', 'mano'
    
    stato VARCHAR(20) DEFAULT 'in_attesa', -- 'in_attesa', 'in_esame', 'accettata', 'rifiutata', 'risolta'
    
    -- Risposta azienda
    gestito_da INTEGER REFERENCES users(id) ON DELETE SET NULL,
    data_gestione TIMESTAMP,
    risposta TEXT,
    documento_risposta_path TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_payslip_disputes_payslip ON payslip_disputes(payslip_id);
CREATE INDEX idx_payslip_disputes_employee ON payslip_disputes(employee_id);
CREATE INDEX idx_payslip_disputes_stato ON payslip_disputes(stato);
CREATE INDEX idx_payslip_disputes_valida ON payslip_disputes(contestazione_valida);

-- TABELLA: payslip_download_log (LOG DOWNLOAD/STAMPE BUSTE)
CREATE TABLE IF NOT EXISTS payslip_download_log (
    id SERIAL PRIMARY KEY,
    payslip_id INTEGER REFERENCES payslips(id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    
    tipo VARCHAR(20) NOT NULL, -- 'visualizzazione', 'download_pdf', 'download_modulo'
    data_azione TIMESTAMP NOT NULL DEFAULT NOW(),
    
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    -- Stato contestazione al momento dell'azione
    giorni_rimanenti_contestazione INTEGER,
    contestazione_ancora_valida BOOLEAN,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_payslip_download_log_payslip ON payslip_download_log(payslip_id);
CREATE INDEX idx_payslip_download_log_employee ON payslip_download_log(employee_id);
CREATE INDEX idx_payslip_download_log_tipo ON payslip_download_log(tipo);

-- TABELLA: controllo_mensile (CONTROLLO CORRISPETTIVI VS POS)
CREATE TABLE IF NOT EXISTS controllo_mensile (
    id SERIAL PRIMARY KEY,
    anno INTEGER NOT NULL,
    mese INTEGER NOT NULL,
    data_controllo DATE NOT NULL,
    
    -- Corrispettivi
    totale_corrispettivi DECIMAL(12,2) DEFAULT 0,
    corrispettivi_contante DECIMAL(12,2) DEFAULT 0,
    corrispettivi_elettronici DECIMAL(12,2) DEFAULT 0,
    
    -- POS
    totale_pos DECIMAL(12,2) DEFAULT 0,
    numero_transazioni_pos INTEGER DEFAULT 0,
    
    -- Cassa
    totale_cassa DECIMAL(12,2) DEFAULT 0,
    
    -- Quadrature
    differenza_pos_corrispettivi DECIMAL(12,2) DEFAULT 0,
    differenza_cassa_corrispettivi DECIMAL(12,2) DEFAULT 0,
    quadrato BOOLEAN DEFAULT false,
    
    note TEXT,
    creato_da INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(anno, mese)
);

CREATE INDEX idx_controllo_mensile_anno_mese ON controllo_mensile(anno, mese);
CREATE INDEX idx_controllo_mensile_quadrato ON controllo_mensile(quadrato);

-- TABELLA: bonifici (GESTIONE BONIFICI BANCARI)
CREATE TABLE IF NOT EXISTS bonifici (
    id SERIAL PRIMARY KEY,
    
    data_bonifico DATE NOT NULL,
    beneficiario VARCHAR(255) NOT NULL,
    iban_beneficiario VARCHAR(27),
    importo DECIMAL(12,2) NOT NULL,
    causale TEXT,
    
    tipo VARCHAR(20) NOT NULL, -- 'dipendente', 'fornitore', 'altro'
    riferimento_id INTEGER, -- ID dipendente o fornitore
    
    -- Riconciliazione
    riconciliato BOOLEAN DEFAULT false,
    data_riconciliazione TIMESTAMP,
    payslip_id INTEGER REFERENCES payslips(id) ON DELETE SET NULL,
    fornitore_id INTEGER, -- Link a tabella fornitori
    
    -- Import da file
    file_import_path TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_bonifici_data ON bonifici(data_bonifico);
CREATE INDEX idx_bonifici_tipo ON bonifici(tipo);
CREATE INDEX idx_bonifici_riconciliato ON bonifici(riconciliato);
CREATE INDEX idx_bonifici_beneficiario ON bonifici(beneficiario);

-- COMMENTI TABELLE
COMMENT ON TABLE employees IS 'Anagrafica completa dipendenti';
COMMENT ON TABLE payslips IS 'Buste paga mensili con PDF e dati estratti';
COMMENT ON TABLE prima_nota_salari IS 'Registrazioni contabili salari e contributi';
COMMENT ON TABLE employee_payments IS 'Bonifici effettuati ai dipendenti';
COMMENT ON TABLE attendances IS 'Presenze giornaliere dipendenti';
COMMENT ON TABLE contracts IS 'Contratti di lavoro con firma digitale';
COMMENT ON TABLE leave_requests IS 'Richieste ferie e permessi';
COMMENT ON TABLE employee_documents IS 'Documenti condivisi con dipendenti';
COMMENT ON TABLE hr_notifications IS 'Notifiche sistema HR';
COMMENT ON TABLE email_import_log IS 'Log import automatico email';

-- ============================================================================
-- FINE MIGRATION 007
-- ============================================================================
