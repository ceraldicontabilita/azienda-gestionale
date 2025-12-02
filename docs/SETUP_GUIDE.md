# 🚀 AZIENDA IN CLOUD - Guida Setup e Sviluppo

## 📦 Struttura Progetto Completata

```
azienda-cloud/
├── backend/                    # Backend FastAPI
│   ├── api/                   # Router API (298 endpoint da implementare)
│   │   ├── _template_router.py  # Template per nuovi router ⭐
│   │   ├── auth.py            # ✅ Autenticazione completa
│   │   ├── dashboard.py       # 🔨 Da implementare
│   │   ├── invoices.py        # 🔨 Da implementare
│   │   ├── suppliers.py       # 🔨 Da implementare
│   │   ├── employees.py       # 🔨 Da implementare
│   │   ├── cash_register.py   # 🔨 Da implementare
│   │   ├── haccp.py           # 🔨 Da implementare
│   │   ├── bank.py            # 🔨 Da implementare
│   │   ├── reconciliation.py  # 🔨 Da implementare
│   │   ├── iva.py             # 🔨 Da implementare
│   │   ├── warehouse.py       # 🔨 Da implementare
│   │   ├── accounting.py      # 🔨 Da implementare
│   │   ├── documents.py       # 🔨 Da implementare
│   │   ├── analytics.py       # 🔨 Da implementare
│   │   └── settings.py        # 🔨 Da implementare
│   ├── models/                # Modelli Pydantic
│   │   └── schemas.py         # ✅ Tutti i modelli principali
│   ├── parsers/               # Parser per file
│   │   └── fatturapa_parser.py # ✅ Parser XML FatturaPA completo
│   ├── utils/                 # Utilities
│   │   └── auth.py            # ✅ Sistema autenticazione JWT
│   ├── database.py            # ✅ Connessione database
│   ├── server.py              # ✅ Server FastAPI principale
│   ├── requirements.txt       # ✅ Dipendenze Python
│   └── .env.example           # ✅ Template variabili ambiente
├── database/                   # Database SQL
│   └── schema.sql             # ✅ Schema completo 22 tabelle
├── frontend/                   # Frontend React (da creare)
│   └── README.md              # Guida frontend
├── docs/                       # Documentazione
│   └── API.md                 # Documentazione API
└── README.md                   # ✅ README principale

```

---

## 🏗️ Stato Attuale del Progetto

### ✅ Completato (Base Funzionante)

1. **Database Schema** - 22 tabelle complete
2. **Sistema Autenticazione** - JWT completo con login/register
3. **Parser FatturaPA** - Parsing XML fatture elettroniche
4. **Modelli Pydantic** - Validation per tutte le entity principali
5. **Server FastAPI** - Configurazione base con CORS e middleware
6. **Template Router** - Pattern per implementare nuovi endpoint

### 🔨 Da Implementare (Seguendo il Template)

Tutti i router API sono stati creati come stub. Per implementarli:

1. Apri `backend/api/_template_router.py`
2. Copia il pattern appropriato (GET, POST, PUT, DELETE, etc.)
3. Adatta al tuo modulo specifico
4. Usa i modelli Pydantic già creati in `models/schemas.py`

---

## 📚 Guida Rapida Implementation

### Step 1: Setup Ambiente

```bash
# 1. Crea virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Configura variabili ambiente
cp .env.example .env
# Modifica .env con le tue credenziali
```

### Step 2: Setup Database

```bash
# 1. Crea database PostgreSQL o Supabase project

# 2. Esegui schema
psql -U postgres -d azienda_cloud -f ../database/schema.sql

# 3. Verifica connessione in .env
DATABASE_URL=postgresql://user:pass@localhost:5432/azienda_cloud
```

### Step 3: Avvia Server

```bash
# Development mode
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Production mode
uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
```

### Step 4: Test API

```bash
# Apri browser
http://localhost:8001/api/docs

# Test authentication
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

---

## 🛠️ Come Implementare un Nuovo Endpoint

### Esempio: Implementare GET /api/invoices

```python
# File: backend/api/invoices.py

from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID

from utils.auth import get_current_user_id
from database import DatabaseHelper
from models.schemas import InvoiceResponse, InvoiceListResponse

router = APIRouter()
db = DatabaseHelper()

@router.get("/", response_model=InvoiceListResponse)
async def list_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    stato: Optional[str] = None,
    user_id: str = Depends(get_current_user_id)
):
    """
    List fatture with pagination
    
    - **page**: Page number
    - **page_size**: Items per page
    - **stato**: Filter by status (optional)
    """
    try:
        filters = {"id_utente": user_id}
        if stato:
            filters["stato"] = stato
        
        # Query database
        fatture = await db.execute_query(
            table="fatture",
            operation="select",
            filters=filters
        )
        
        # Pagination
        total = len(fatture) if fatture else 0
        start = (page - 1) * page_size
        end = start + page_size
        items = fatture[start:end] if fatture else []
        
        return InvoiceListResponse(
            fatture=[InvoiceResponse(**f) for f in items],
            total=total,
            page=page,
            page_size=page_size
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📋 Checklist Implementazione Moduli

### Modulo Fatture (Priority: 🔴 High)

- [ ] GET /api/invoices - List fatture
- [ ] GET /api/invoices/{id} - Get singola fattura
- [ ] POST /api/invoices - Create fattura manuale
- [ ] PUT /api/invoices/{id} - Update fattura
- [ ] DELETE /api/invoices/{id} - Delete fattura
- [ ] POST /api/invoices/upload-bulk - Upload XML massivo
- [ ] POST /api/invoices/upload-single - Upload XML singolo
- [ ] GET /api/invoices/by-state/{state} - Fatture per stato
- [ ] PUT /api/invoices/{id}/payment - Segna come pagata
- [ ] GET /api/invoices/export-excel - Export Excel

### Modulo Fornitori (Priority: 🔴 High)

- [ ] GET /api/suppliers - List fornitori
- [ ] GET /api/suppliers/{id} - Get fornitore
- [ ] POST /api/suppliers - Create fornitore
- [ ] PUT /api/suppliers/{id} - Update fornitore
- [ ] DELETE /api/suppliers/{id} - Delete fornitore
- [ ] GET /api/suppliers/by-payment-method/{method} - Per metodo pagamento

### Modulo Dashboard (Priority: 🔴 High)

- [ ] GET /api/dashboard/stats - Statistiche generali
- [ ] GET /api/dashboard/alerts - Alert e notifiche
- [ ] GET /api/dashboard/charts/revenue - Grafico ricavi
- [ ] GET /api/dashboard/charts/expenses - Grafico spese

### Modulo Prima Nota Cassa (Priority: 🟡 Medium)

- [ ] GET /api/cash-register/movements - Lista movimenti
- [ ] POST /api/cash-register/movement - Registra movimento
- [ ] POST /api/cash-register/daily-closing - Chiusura giornaliera
- [ ] POST /api/cash-register/import-corrispettivi - Import corrispettivi
- [ ] POST /api/cash-register/import-pos - Import POS
- [ ] POST /api/cash-register/import-versamenti - Import versamenti

### Modulo Dipendenti (Priority: 🟡 Medium)

- [ ] GET /api/employees - List dipendenti
- [ ] POST /api/employees - Create dipendente
- [ ] GET /api/employees/{id}/shifts - Turni dipendente
- [ ] POST /api/employees/upload-payslip - Upload busta paga
- [ ] GET /api/employees/libretti-sanitari - Libretti sanitari

### Modulo HACCP (Priority: 🟡 Medium)

- [ ] POST /api/haccp/temperature - Registra temperatura
- [ ] GET /api/haccp/temperature - Lista temperature
- [ ] POST /api/haccp/sanification - Registra sanificazione
- [ ] GET /api/haccp/recipes - Lista ricette
- [ ] POST /api/haccp/recipe - Create ricetta

### Modulo Banca (Priority: 🟡 Medium)

- [ ] GET /api/bank/transactions - Transazioni bancarie
- [ ] POST /api/bank/import-transactions - Import estratto conto
- [ ] GET /api/bank/bonifici - Lista bonifici
- [ ] POST /api/bank/bonifico - Crea bonifico
- [ ] GET /api/bank/assegni - Lista assegni
- [ ] POST /api/bank/assegno - Emetti assegno

### Modulo Riconciliazione (Priority: 🟢 Low)

- [ ] GET /api/reconciliation/pending - Transazioni da riconciliare
- [ ] POST /api/reconciliation/match - Riconcilia transazione
- [ ] POST /api/reconciliation/auto-match - Auto-riconciliazione

### Modulo IVA (Priority: 🟢 Low)

- [ ] GET /api/iva/calculate - Calcola liquidazione IVA
- [ ] GET /api/iva/report/{trimestre} - Report IVA trimestre

### Modulo Magazzino (Priority: 🟢 Low)

- [ ] GET /api/warehouse/items - Lista articoli
- [ ] POST /api/warehouse/item - Aggiungi articolo
- [ ] POST /api/warehouse/movement - Movimento magazzino
- [ ] POST /api/warehouse/populate-from-invoices - Popola da fatture

### Modulo Contabilità (Priority: 🟢 Low)

- [ ] GET /api/accounting/chart-of-accounts - Piano dei conti
- [ ] POST /api/accounting/initialize - Inizializza piano conti
- [ ] GET /api/accounting/bilancino - Bilancino
- [ ] POST /api/accounting/movement - Registra movimento

---

## 🎯 Roadmap Sviluppo Suggerita

### Fase 1: Core Business (Settimana 1-2)
1. ✅ Setup progetto e database
2. ✅ Autenticazione
3. 🔨 Modulo Fatture completo
4. 🔨 Modulo Fornitori
5. 🔨 Dashboard base

### Fase 2: Operatività (Settimana 3-4)
6. Prima Nota Cassa
7. Gestione Dipendenti
8. HACCP base
9. Upload fatture XML automatico

### Fase 3: Banking (Settimana 5)
10. Gestione Banca
11. Bonifici e Assegni
12. Riconciliazione Bancaria

### Fase 4: Compliance (Settimana 6)
13. Calcolo IVA
14. Gestione F24
15. Piano dei Conti
16. Report contabili

### Fase 5: Advanced (Settimana 7+)
17. Magazzino
18. Ricettario HACCP
19. Analytics avanzate
20. Export e Report PDF

---

## 🔧 Strumenti Utili

### Testing API

```bash
# HTTPie (più user-friendly di curl)
pip install httpie

# Test login
http POST localhost:8001/api/auth/login email=test@test.com password=test123

# Test con token
http GET localhost:8001/api/invoices "Authorization:Bearer YOUR_TOKEN"
```

### Database GUI

- **pgAdmin** - GUI PostgreSQL desktop
- **Supabase Dashboard** - Se usi Supabase
- **DBeaver** - Universal DB tool

### API Testing

- **Postman** - Collection API testing
- **Insomnia** - Alternative a Postman
- **Thunder Client** - VS Code extension

---

## 📖 Documentazione API Auto-Generata

Una volta avviato il server, la documentazione interattiva è disponibile a:

- **Swagger UI**: http://localhost:8001/api/docs
- **ReDoc**: http://localhost:8001/api/redoc

---

## 🐛 Troubleshooting

### Errore: Module not found

```bash
# Assicurati di essere nella directory backend
cd backend
# Attiva virtual environment
source venv/bin/activate
# Reinstalla dipendenze
pip install -r requirements.txt
```

### Errore: Database connection

```bash
# Verifica .env
cat .env | grep DATABASE_URL
# Test connessione
psql $DATABASE_URL -c "SELECT 1"
```

### Errore: JWT decode error

```bash
# Rigenera SECRET_KEY in .env
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📞 Support & Contributi

Per domande o contributi:
1. Consulta questa documentazione
2. Guarda `_template_router.py` per esempi
3. Segui i pattern esistenti in `auth.py`
4. Mantieni coerenza con `models/schemas.py`

---

## 📝 Note Finali

Questo progetto è una base solida per un ERP completo. Il sistema di autenticazione, il database schema e i parser sono pronti per l'uso in produzione. 

Gli endpoint sono strutturati per essere implementati rapidamente seguendo il template fornito. Ogni modulo può essere sviluppato indipendentemente.

**Tempo stimato per completamento**: 6-8 settimane per un developer esperto full-time.

---

**Versione**: 2.0  
**Ultimo aggiornamento**: Dicembre 2025  
**Proprietario**: Ceraldi Group S.R.L.
