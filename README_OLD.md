# 🏢 Azienda in Cloud - ERP Sistema Gestionale Completo

Sistema ERP completo per attività **HORECA** (Hotel, Ristoranti, Catering) - Bar/Pasticceria

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

## 📋 Descrizione

**Azienda in Cloud** è un sistema ERP (Enterprise Resource Planning) completo progettato specificamente per attività HORECA. Gestisce tutti gli aspetti operativi di un'attività commerciale nel settore alimentare e della ristorazione.

### Moduli Principali

- 📄 **Fatture Passive** (acquisti fornitori)
- 💰 **Prima Nota Cassa** (corrispettivi, POS, versamenti)
- 👥 **Dipendenti & Buste Paga**
- 🦠 **HACCP** (sicurezza alimentare)
- 📦 **Magazzino & Inventario**
- 🏦 **Gestione Banca** (bonifici, assegni, riconciliazione)
- 🧾 **IVA** e adempimenti fiscali
- 💼 **Gestione Erario** (F24, contributi)
- 📊 **Piano dei Conti** (contabilità semplificata)

## 🎯 Caratteristiche Principali

### Import Automatico
- ✅ **XML FatturaPA** - Parser completo con namespace support
- ✅ **PDF Buste Paga** - Zucchetti format
- ✅ **Excel** - Corrispettivi, POS, versamenti bancari
- ✅ **Gmail** - Fetch automatico fatture da email

### Funzionalità Avanzate
- 🔄 **Riconciliazione bancaria** automatica
- 📈 **Dashboard** con statistiche real-time
- ⚠️ **Alert system** (scadenze, scorte, libretti sanitari)
- 🗂️ **Piano dei Conti** 81 voci per Bar/Pasticceria
- 🔍 **Tracciabilità alimentare** con QR code

## 🚀 Quick Start

### Prerequisiti

- **Python 3.9+**
- **Node.js 18+**
- **PostgreSQL 14+** o account **Supabase**

### 1. Backend Setup

```bash
# Clona il repository
git clone https://github.com/your-repo/azienda-cloud.git
cd azienda-cloud/backend

# Installa dipendenze
pip install -r requirements.txt

# Configura database
cp .env.example .env
# Modifica .env con le tue credenziali

# Crea schema database
psql -U user -d azienda_cloud -f schema.sql

# Avvia il server
python server.py
```

Backend disponibile su: `http://localhost:8001`

### 2. Frontend Setup

```bash
cd ../frontend

# Installa dipendenze
npm install

# Avvia development server
npm run dev
```

Frontend disponibile su: `http://localhost:3000`

## 📚 Documentazione

### API Documentation
Una volta avviato il backend:
- **Swagger UI**: http://localhost:8001/api/docs
- **ReDoc**: http://localhost:8001/api/redoc

### Documentazione Completa
- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
- [Documentazione Originale](./DOCUMENTAZIONE.md)

## 🗂️ Struttura Progetto

```
azienda-cloud/
├── backend/                  # FastAPI Backend
│   ├── server.py            # Server principale
│   ├── schema.sql           # Schema database
│   ├── requirements.txt     # Dipendenze Python
│   └── app/
│       ├── routers/         # 16 routers API (298+ endpoints)
│       ├── models/          # Modelli Pydantic
│       ├── parsers/         # XML, PDF, Excel parsers
│       └── services/        # Business logic
│
├── frontend/                # React Frontend
│   ├── src/
│   │   ├── pages/          # 13 pagine applicazione
│   │   ├── components/     # Componenti riutilizzabili
│   │   └── services/       # API client
│   └── package.json
│
└── README.md               # Questo file
```

## 🔧 Stack Tecnologico

### Backend
- **FastAPI** - Framework web Python
- **Supabase/PostgreSQL** - Database
- **PDFPlumber** - Parsing PDF
- **lxml** - Parsing XML
- **Pandas/Openpyxl** - Excel handling

### Frontend
- **React 19** - UI Framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Routing
- **Axios** - HTTP client
- **Recharts** - Grafici

## 📊 Database Schema

40+ tabelle tra cui:

- `utenti` - Utenti del sistema
- `fatture` - Fatture passive
- `fornitori` - Anagrafica fornitori
- `dipendenti` - Anagrafica dipendenti
- `movimenti_cassa` - Prima nota cassa
- `inventario` - Magazzino
- `piano_dei_conti` - Contabilità
- E molte altre...

Vedi [schema.sql](./backend/schema.sql) per lo schema completo.

## 🔌 API Endpoints (298+)

### Dashboard
- `GET /dashboard/stats` - Statistiche
- `GET /dashboard/quick-actions` - Azioni rapide

### Fatture
- `GET /invoices/` - Lista fatture
- `POST /invoices/upload-bulk` - Upload XML multiplo
- `GET /invoices/by-state/{state}` - Per stato
- `POST /invoices/{id}/mark-paid` - Segna pagata

### Fornitori, Dipendenti, HACCP, Magazzino...
Vedi documentazione API completa.

## 🎨 Pagine Frontend

1. **Dashboard** - Panoramica generale ✅
2. **Gestione Fatture** - Upload XML, gestione completa ✅
3. **Fornitori** - Anagrafica fornitori (stub)
4. **Prima Nota Cassa** - Movimenti giornalieri (stub)
5. **Gestione Dipendenti** - HR completo (stub)
6. **HACCP** - Sicurezza alimentare (stub)
7. **Gestione Bonifici** - Collegamento fatture (stub)
8. **Gestione Assegni** - Carnet assegni (stub)
9. **Riconciliazione Bancaria** - Matching automatico (stub)
10. **Gestione Erario** - F24 e tributi (stub)
11. **IVA** - Liquidazione IVA (stub)
12. **Magazzino** - Inventario (stub)
13. **Impostazioni** - Configurazione (stub)

## 🚧 Roadmap

### Fase 1 - Core (Completata)
- ✅ Struttura backend completa
- ✅ Database schema
- ✅ Parser XML FatturaPA
- ✅ Parser PDF buste paga
- ✅ Dashboard & Fatture frontend

### Fase 2 - In Corso
- ⏳ Implementazione router completi
- ⏳ Frontend pagine rimanenti
- ⏳ Autenticazione JWT
- ⏳ Testing suite

### Fase 3 - Avanzate
- 📋 Gmail API integration
- 📋 Export Excel/PDF
- 📋 Grafici e analytics
- 📋 Notifiche email
- 📋 Mobile app

## 🧪 Testing

```bash
# Backend
cd backend
pytest tests/

# Frontend
cd frontend
npm test
```

## 🏭 Deploy

### Backend (Docker)
```bash
docker build -t azienda-cloud-backend ./backend
docker run -p 8001:8001 azienda-cloud-backend
```

### Frontend
```bash
cd frontend
npm run build
# Deploy dist/ folder su hosting statico
```

## 🔒 Sicurezza

- Validazione input con Pydantic
- Protezione SQL injection
- CORS configurabile
- Rate limiting (da implementare)
- JWT authentication (da implementare)

## 📝 Licenza

**Proprietario**: Ceraldi Group S.R.L.  
**Versione**: 2.0  
**Data**: Dicembre 2025

Tutti i diritti riservati. Questo software è proprietario e non può essere distribuito, modificato o utilizzato senza autorizzazione scritta.

## 👨‍💻 Sviluppato da

Ceraldi Group S.R.L.  
Sistema ERP per Pasticcerie e Bar

## 📞 Supporto

Per assistenza tecnica o domande:
- 📧 Email: support@ceraldigroup.it
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)

---

Made with ❤️ for Italian HORECA businesses
