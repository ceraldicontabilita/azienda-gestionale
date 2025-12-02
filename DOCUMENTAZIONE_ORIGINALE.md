# 🏢 AZIENDA IN CLOUD - ERP Gestionale Completo

> **Sistema ERP completo per attività HORECA**
> Versione: 2.0 | Ultimo aggiornamento: 28 Novembre 2025

---

## 📋 INDICE

1. [Scopo dell'Applicazione](#1-scopo-dellapplicazione)
2. [Origine dei Dati](#2-origine-dei-dati)
3. [Flusso Primario: Fatture](#3-flusso-primario-fatture)
4. [Dettaglio Pagine](#4-dettaglio-pagine)
5. [Schema Relazionale Database](#5-schema-relazionale-database)
6. [Tecnologie](#6-tecnologie)
7. [Installazione](#7-installazione)

---

## 1. SCOPO DELL'APPLICAZIONE

Questa è un'applicazione **ERP (Enterprise Resource Planning)** per la gestione completa di un'attività commerciale, principalmente nel settore **HORECA** (Hotel, Ristoranti, Catering).

### Moduli Principali:
- **Fatture passive** (acquisti da fornitori)
- **Fatture attive** (vendite ai clienti)
- **Prima nota cassa** (movimenti giornalieri)
- **Dipendenti e buste paga**
- **HACCP** (sicurezza alimentare)
- **Magazzino e inventario**
- **Banca** (bonifici, assegni, riconciliazione)
- **IVA e adempimenti fiscali**
- **Gestione Erario** (F24, contributi, codici tributo)

---

## 2. ORIGINE DEI DATI

L'applicazione riceve dati da **4 fonti principali**:

### 2.1 FATTURE XML (SDI)
- Upload manuale singolo/multiplo
- Fetch automatico da Gmail
- Import da Fattura24
- **Formato:** FatturaPA XML italiano

### 2.2 FILE EXCEL
- Corrispettivi giornalieri (Agenzia Entrate)
- Transazioni POS
- Versamenti bancari
- Anagrafica dipendenti
- Bonifici bancari
- Estratti conto

### 2.3 PDF BUSTE PAGA
- Parser automatico Zucchetti
- Estrazione: nome, netto, acconto, mansione, mese

### 2.4 INSERIMENTO MANUALE
- Chiusure giornaliere cassa
- Temperature HACCP
- Sanificazioni
- Nuovi dipendenti/fornitori

---

## 3. FLUSSO PRIMARIO: FATTURE

La **FATTURA** è il documento centrale da cui derivano quasi tutti gli altri dati.

### 3.1 Upload Fattura XML

**File Frontend:** `/app/frontend/src/pages/Archive.js`
**Endpoint:** `POST /invoices/upload-bulk`

**Processo:**
1. Il backend legge il file XML (formato FatturaPA)
2. Estrae: fornitore, data, numero, importo, righe dettaglio, IVA
3. Crea record in tabella `fatture`
4. Crea record in tabella `righe_fattura` (dettaglio prodotti)
5. Crea/aggiorna record in tabella `fornitori`

### 3.2 Ciclo di Vita Fattura

```
Upload XML → Attive → Assegna Metodo Pagamento → In Attesa → Segna Pagata → Archiviate
```

---

## 4. DETTAGLIO PAGINE

### PAGINA 1: DASHBOARD (/dashboard)

**File:** `/app/frontend/src/pages/Dashboard.js`
**Scopo:** Panoramica generale dell'attività

| Card | Dato | Endpoint |
|------|------|----------|
| Fatture Mese | Totale € | GET /dashboard/stats |
| N. Fornitori | Conteggio | GET /dashboard/stats |
| Scadenze | Alert | GET /analytics/alerts |

---

### PAGINA 2: GESTIONE FATTURE (/archive)

**File:** `/app/frontend/src/pages/Archive.js`
**Scopo:** Gestione completa fatture passive (acquisti)

**Tab disponibili:**
| Tab | Descrizione | Endpoint |
|-----|-------------|----------|
| Archiviate | Fatture pagate | GET /invoices |
| Attive | Da pagare | GET /invoices?status=active |
| In Attesa | Bonifico in corso | GET /invoices/by-state/pending |
| Banca | Pagate via bonifico | GET /invoices/by-state/registered_bank |
| Cassa | Pagate in contanti | GET /invoices/by-state/registered_cash |
| Non Riconciliate | Pagate, non abbinate | GET /invoices/by-state/paid_not_reconciled |
| Non Gestite | Senza metodo | GET /invoices/by-state/unmanaged |

**Bottoni:**
- Upload Massivo XML → POST /invoices/upload-bulk
- Scarica nuove fatture → POST /documents/fetch-from-gmail
- Export Excel → GET /invoices/export-excel
- Popola Magazzino → POST /warehouse/populate-from-existing-invoices

---

### PAGINA 3: FORNITORI (/suppliers)

**File:** `/app/frontend/src/pages/Suppliers.js`
**Scopo:** Anagrafica fornitori e metodi di pagamento

**Come si popolano:**
1. **AUTOMATICO:** Da fatture XML (P.IVA nuova)
2. **MANUALE:** Bottone "Nuovo Fornitore"
3. **IMPORT:** Da fatture esistenti

**Tab per metodo pagamento:**
- Tutti | Banca | Cassa | Assegno | Misto

**Perché è importante:** Il metodo pagamento determina automaticamente dove va la fattura.

---

### PAGINA 4: PRIMA NOTA CASSA (/prima-nota-cassa)

**File:** `/app/frontend/src/pages/PrimaNotaCassa.js`
**Scopo:** Registro giornaliero dei movimenti di cassa

**Sezione "Chiusure Giornaliere Serali":**
- Corrispettivi (scontrini) → Totale cassa del giorno
- POS (carte) → Totale pagamenti carta
- Versamento in banca → Quanto portato in banca

**Formula:**
```
Saldo Cassa = Corrispettivi - POS - Versamenti
```

**Import automatico:**
| Tipo | Endpoint | File |
|------|----------|------|
| Corrispettivi XML | POST /cash-register/import-corrispettivi-xml | XML Agenzia Entrate |
| Corrispettivi Excel | POST /cash-register/import-corrispettivi | corrispettivi.xlsx |
| POS Excel | POST /cash-register/import-pos | pos.xlsx |
| Versamenti Excel | POST /cash-register/import-versamenti | versamenti.xlsx |

---

### PAGINA 5: GESTIONE DIPENDENTI (/gestione-dipendenti)

**File:** `/app/frontend/src/pages/GestioneDipendenti.js`
**Scopo:** Gestione completa del personale

**Tab disponibili:**
| Tab | Funzione | Endpoint |
|-----|----------|----------|
| Anagrafica | Lista dipendenti | GET /dipendenti |
| Turni Settimanali | Pianificazione | GET/POST /shifts/week |
| Libro Unico (Paghe) | Import buste paga | POST /haccp/libro-unico/upload |
| Libretti Sanitari | Scadenze | GET /haccp/libretti-sanitari |
| Prima Nota Salari | Registro paghe | GET /prima-nota-salari |

**Flusso Import PDF Buste Paga:**
```
1. Upload PDF → 2. Parser estrae dati → 3. Crea record:
   - dipendenti (se nuovo)
   - paghe_dipendenti (busta paga)
   - prima_nota_salari (movimento)
   - libretti_sanitari (scadenza)
```

---

### PAGINA 6: HACCP (/haccp)

**File:** `/app/frontend/src/pages/HACCP.js`
**Scopo:** Gestione sicurezza alimentare (obbligatorio HORECA)

**Card disponibili:**
| Card | Sottopagina | Scopo |
|------|-------------|-------|
| Temperature Frigoriferi | /haccp/temperature-frigoriferi | Registro temperature |
| Temperature Congelatori | /haccp/temperature-congelatori | Registro temperature |
| Sanificazioni | /haccp/sanificazioni | Registro pulizie |
| Disinfestazioni | /haccp/disinfestazioni | Pest control |
| Scadenzario Alimenti | /haccp/scadenzario | Scadenze prodotti |
| Tracciabilità | /tracciabilita-alimentare | Lotti e QR code |
| Schede Tecniche | /haccp/schede-tecniche | Documenti prodotti |
| Ricettario | /haccp/ricettario | Ricette e allergeni |

---

### PAGINA 7: GESTIONE BONIFICI (/gestione-bonifici)

**File:** `/app/frontend/src/pages/GestioneBonifici.js`
**Scopo:** Registrare bonifici e collegarli alle fatture

**Flusso:**
```
1. Upload Excel bonifici dalla banca
2. Sistema importa: data, importo, beneficiario, causale
3. Per ogni bonifico, "Collega" una fattura
4. Fattura passa da "In Attesa" a "Pagata Banca"
```

---

### PAGINA 8: GESTIONE ASSEGNI (/gestione-assegni)

**File:** `/app/frontend/src/pages/GestioneAssegni.js`
**Scopo:** Gestione carnet assegni

**Stati assegno:**
- `da_emettere` → nuovo
- `emesso` → compilato e consegnato
- `pagato` → incassato
- `annullato` → cancellato
- `distrutto` → fisicamente distrutto

---

### PAGINA 9: RICONCILIAZIONE BANCARIA (/riconciliazione-bancaria)

**File:** `/app/frontend/src/pages/RiconciliazioneBancaria.js`
**Scopo:** Abbinare movimenti estratto conto con documenti

**⚠️ IMPORTANTE: Non serve solo per fatture!**

La riconciliazione bancaria deve abbinare:

| Tipo Movimento | Documento da Abbinare | Azione Post-Abbinamento |
|----------------|----------------------|------------------------|
| Pagamento fornitore | Fattura | Marca fattura come pagata |
| Pagamento F24 Contributi | F24 Contributi | Registra in Gestione Erario |
| Pagamento F24 Erario | F24 Erario | Registra in Gestione Erario |
| Pagamento Stipendio | Busta Paga | Salda paga dipendente in Prima Nota Salari |
| Versamento Contanti | Movimento Cassa | Registra in Prima Nota Cassa |

**Flusso Riconciliazione Completo:**
```
1. Upload estratto conto banca (Excel/CSV)
       ↓
2. Sistema importa movimenti in "transazioni_bancarie"
       ↓
3. Per ogni movimento, identifica il tipo:
   - Se importo corrisponde a FATTURA → abbina a fattura
   - Se importo corrisponde a F24 → abbina a F24 + registra in Erario
   - Se importo corrisponde a STIPENDIO → abbina a busta paga + salda dipendente
       ↓
4. Aggiorna stato documenti collegati
```

**Tabelle coinvolte:**
- `transazioni_bancarie` (movimenti importati)
- `fatture` (da abbinare)
- `f24` (da abbinare)
- `paghe_dipendenti` (stipendi da saldare)
- `prima_nota_salari` (registrazione pagamento)
- `erario` (registrazione F24 pagati)

---

### PAGINA 10: GESTIONE ERARIO (/gestione-erario) ⭐ NUOVA

**File:** `/app/frontend/src/pages/GestioneErario.js`
**Scopo:** Gestione F24, contributi e codici tributo

**Card/Sezioni:**

#### 10.1 GESTIONE CONTRIBUTI
- F24 Contributi INPS
- F24 Contributi INAIL
- Contributi previdenziali
- Collegamento con buste paga

#### 10.2 GESTIONE ERARIO (TASSE)
- F24 Erario (IRPEF, IRES, IRAP)
- Addizionali regionali/comunali
- Ritenute d'acconto
- IVA da versare

#### 10.3 CODICI TRIBUTO

| Codice | Descrizione | Categoria |
|--------|-------------|----------|
| 1001 | IRPEF - Ritenute lavoro dipendente | Erario |
| 1040 | IRPEF - Ritenute lavoro autonomo | Erario |
| 1712 | Acconto imposta sostitutiva TFR | Erario |
| 1713 | Saldo imposta sostitutiva TFR | Erario |
| 3800 | IRAP - Acconto prima rata | Erario |
| 3801 | Addizionale regionale IRPEF | Erario |
| 3844 | Addizionale comunale IRPEF - Acconto | Erario |
| 3848 | Addizionale comunale IRPEF - Saldo | Erario |
| 6099 | IVA - Versamento annuale | IVA |
| 6001-6012 | IVA mensile (gen-dic) | IVA |
| DM10 | Contributi INPS | Contributi |
| DMRA | Contributi INPS artigiani | Contributi |

#### 10.4 RIEPILOGO CODICI TRIBUTO PAGATI

**Vista per Periodo:**
| Mese | Codice | Descrizione | Importo | Data Pagamento | Stato |
|------|--------|-------------|---------|----------------|-------|
| Nov 2025 | 1001 | IRPEF dipendenti | €1.500 | 16/11/2025 | ✅ Pagato |
| Nov 2025 | DM10 | INPS | €2.300 | 16/11/2025 | ✅ Pagato |
| Nov 2025 | 3801 | Add. Regionale | €450 | 16/11/2025 | ✅ Pagato |

**Relazione con Riconciliazione Bancaria:**
```
Estratto Conto → Movimento F24 → Abbina a F24 documento
                                         ↓
                              Registra in Gestione Erario
                                         ↓
                              Aggiorna Riepilogo Codici Tributo
```

---

### PAGINA 11: IVA (/iva)

**File:** `/app/frontend/src/pages/IVA.js`
**Scopo:** Calcolo liquidazione IVA

**Da dove prende i dati:**
- `fatture` → IVA acquisti (detraibile)
- `fatture_emesse` → IVA vendite (da versare)
- `movimenti_cassa.corrispettivi` → IVA incassata

**Calcolo:**
```
IVA DA VERSARE = IVA Vendite - IVA Acquisti

Se negativo → CREDITO IVA
Se positivo → DEBITO IVA
```

---

### PAGINA 12: MAGAZZINO (/warehouse)

**File:** `/app/frontend/src/pages/Magazzino.js`
**Scopo:** Gestione inventario

**Come si popola:**
1. AUTOMATICO da righe fattura
2. MANUALE
3. IMPORT EXCEL

---

### PAGINA 13: IMPOSTAZIONI (/impostazioni)

**File:** `/app/frontend/src/pages/Impostazioni.js`
**Scopo:** Configurazione sistema

**Tab:** Profilo | Documenti | HACCP & Email | Dati | Magazzino | Zona Pericolosa

---

## 5. SCHEMA RELAZIONALE DATABASE

```
utenti (1)
    │
    ├──► fatture (*)
    │        └──► righe_fattura (*)
    │        └──► fornitori (FK: partita_iva)
    │
    ├──► fornitori (*)
    │
    ├──► dipendenti (*)
    │        ├──► paghe_dipendenti (*)
    │        ├──► prima_nota_salari (*)
    │        ├──► contratti_dipendenti (*)
    │        ├──► documenti_dipendenti (*)
    │        ├──► libretti_sanitari (*)
    │        └──► turni (*)
    │
    ├──► movimenti_cassa (*)
    │
    ├──► bonifici (*) ──► fatture (FK)
    │
    ├──► assegni (*)
    │
    ├──► transazioni_bancarie (*)
    │        ├──► fatture (FK)
    │        ├──► f24 (FK)
    │        └──► paghe_dipendenti (FK)
    │
    ├──► f24 (*)
    │        └──► codici_tributo (*)
    │
    ├──► erario (*)
    │        └──► codici_tributo_pagati (*)
    │
    ├──► documenti (*)
    │
    ├──► temperature (*)
    │
    ├──► sanificazioni (*)
    │
    ├──► inventario (*)
    │        └──► tracciabilita (*)
    │
    └──► impostazioni_utente (1)
```

---

## 6. TECNOLOGIE

### Backend
- **FastAPI** (Python)
- **Supabase/PostgreSQL** database
- **PDFPlumber** per parsing PDF

### Frontend
- **React 19**
- **Shadcn UI** + Tailwind CSS
- **Recharts** per grafici
- **Axios** per HTTP

---

## 7. INSTALLAZIONE

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### Frontend

```bash
cd frontend
yarn install
yarn start
```

---

## 📝 CHANGELOG

| Data | Modifica |
|------|----------|
| 28/11/2025 | Creazione documentazione completa |
| 28/11/2025 | Aggiunta sezione Gestione Erario |
| 28/11/2025 | Aggiornata logica Riconciliazione Bancaria |
| 28/11/2025 | Implementati 298 endpoint backend |

---

> **Proprietario:** Ceraldi Group S.R.L.
> **Versione:** 2.0

---

## 🆕 Nuove Funzionalità (Aggiornamento 2025-11-28)

### 1. Card "Gestione Erario" (Dashboard)
Dalla Dashboard, espandi la card "Gestione Erario" per vedere:
- **IVA e Tributi**: Importi IVA, ritenute, IRES/IRAP da versare
- **Contributi**: INPS e INAIL da versare
- **Configurazione Email F24**: Aggiungi i mittenti da cui ricevi F24 (es. commercialista)
- **Auto-scaricamento F24**: Il sistema può scaricare automaticamente i PDF F24 dalle email
- **Auto-riconciliazione**: Abbina automaticamente i pagamenti F24 con l'estratto conto

### 2. Card "Riepilogo Alert" (Dashboard)
Dalla Dashboard, espandi la card "Riepilogo Alert" per vedere:
- **4 categorie**: Assegni da rientrare, F24 da pagare, Fatture scadute, Verifiche saldi
- **Lista alert**: Ogni alert mostra titolo, descrizione, importo e priorità
- **Bottone "Paga"**: Per ogni alert puoi registrare il pagamento direttamente

### 3. Sistema di Pagamento da Alert
Quando clicchi "Paga" su un alert, si apre un modal dove puoi scegliere:

| Metodo | Cosa succede |
|--------|--------------|
| **💵 Cassa** | Inserito in Prima Nota Cassa, fattura marcata come "pagata" |
| **🏦 Banca** | Inserito in Prima Nota Banca, fattura "pagata non riconciliata" |
| **📝 Assegno** | Crea/aggiorna record in Gestione Assegni, assegno "emesso non incassato" |
| **🔀 Misto** | Combinazione dei metodi sopra |

#### Flusso Assegno:
1. Clicchi "Paga" → Seleziona "Assegno"
2. Si apre modal per compilare: Numero, Banca, Data, Beneficiario, Importo
3. Confermi → L'assegno viene salvato in Gestione Assegni
4. La fattura diventa "pagata non riconciliata"
5. Quando l'assegno viene incassato, apparirà in riconciliazione bancaria

### 4. Riconciliazione Bancaria Potenziata
La riconciliazione ora gestisce anche:
- **F24**: Identifica pagamenti F24 tramite keyword (f24, tribut, erario, inps)
- **Stipendi**: Identifica bonifici stipendi tramite keyword (stip, salari, emolument)

---

## Tabelle Database Coinvolte

| Tabella | Descrizione |
|---------|-------------|
| `f24_registrati` | F24 registrati con codice tributo, importo, stato pagamento |
| `assegni` | Assegni emessi/ricevuti con stato (disponibile, emesso, incassato) |
| `prima_nota_banca` | Movimenti bancari registrati manualmente |
| `prima_nota_cassa` | Movimenti di cassa |
| `fatture` | Fatture con nuovo campo `riconciliata` e `stato_pagamento` |
| `paghe_dipendenti` | Stipendi con campi per riconciliazione |
| `transazioni_bancarie` | Movimenti importati da estratto conto |
| `impostazioni_utente` | Configurazione mittenti F24 email |


---

## 🏛️ PIANO DEI CONTI - Bar/Pasticceria (ATECO 56.10.30)

### Funzionalità Implementate

1. **81 voci di Piano dei Conti** specifiche per Bar/Pasticceria
2. **Mapping automatico** fatture → conto corretto basato su keywords
3. **Suggerimento intelligente** del conto al momento dell'inserimento
4. **Bilancino** con raggruppamento per categoria

### Endpoint API

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/accounting/piano-conti-template` | GET | Template completo 81 voci |
| `/accounting/chart-of-accounts/initialize` | POST | Inizializza piano conti per utente |
| `/accounting/suggerisci-conto` | POST | Suggerisce conto da descrizione/fornitore |
| `/accounting/registra-movimento` | POST | Registra movimento contabile |
| `/accounting/bilancino` | GET | Genera bilancino con saldi |

### Mapping Automatico Keywords → Conto

| Keywords | Conto | Descrizione |
|----------|-------|-------------|
| caffè, espresso, torrefazione | 5.1.1 | Acquisti caffè e derivati |
| bevande, bibite, coca cola | 5.1.2 | Acquisti bevande |
| farina, zucchero, uova, burro | 5.1.3 | Acquisti materie prime pasticceria |
| enel, energia elettrica, luce | 6.2.1 | Energia elettrica |
| gas, metano | 6.2.2 | Gas |
| commercialista, fiscale | 6.4.2 | Consulenza commercialista |
| stipendi, salari | 7.1.1 | Stipendi e salari |
| inps, dm10 | 7.1.2 | Contributi INPS |
| inail | 7.1.3 | Contributi INAIL |
| iva | 9.2.1 | IVA a debito |

---

## 📊 TABELLE DATABASE NECESSARIE

### Tabelle CORE (esistenti)
| Tabella | Descrizione |
|---------|-------------|
| `utenti` | Utenti del sistema |
| `fatture` | Fatture ricevute |
| `fatture_emesse` | Fatture emesse |
| `fornitori` | Anagrafica fornitori |
| `dipendenti` | Anagrafica dipendenti |

### Tabelle CONTABILITÀ (da verificare/creare)
| Tabella | Campi chiave |
|---------|--------------|
| `piano_dei_conti` | id, id_utente, codice_conto, descrizione, tipo, categoria, natura, saldo |
| `movimenti_contabili` | id, id_utente, codice_conto, descrizione, importo, tipo_movimento, data_operazione |
| `f24_registrati` | id, id_utente, codice_tributo, importo, stato, riconciliato |
| `prima_nota_banca` | id, id_utente, data_operazione, importo, tipo, descrizione, riconciliato |
| `prima_nota_cassa` | id, id_utente, data_operazione, importo, tipo, descrizione |
| `assegni` | id, id_utente, numero, banca, importo, stato, beneficiario |

### Tabelle OPERATIVITÀ
| Tabella | Descrizione |
|---------|-------------|
| `movimenti_cassa` | Movimenti di cassa da Excel |
| `transazioni_bancarie` | Movimenti banca importati |
| `corrispettivi` | Corrispettivi giornalieri |
| `paghe_dipendenti` | Buste paga |

