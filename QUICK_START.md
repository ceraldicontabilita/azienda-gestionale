# 🚀 Guida Rapida - Azienda in Cloud

## Setup Completo in 5 Minuti

### 1. Database Setup (Supabase)

#### Opzione A: Supabase (Consigliato)

1. Vai su [supabase.com](https://supabase.com)
2. Crea un nuovo progetto
3. Vai su SQL Editor
4. Copia e incolla il contenuto di `backend/schema.sql`
5. Esegui lo script
6. Copia le credenziali:
   - Project URL
   - Anon/Public key

#### Opzione B: PostgreSQL Locale

```bash
# Installa PostgreSQL
sudo apt install postgresql postgresql-contrib

# Crea database
sudo -u postgres psql
CREATE DATABASE azienda_cloud;
CREATE USER azienda_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE azienda_cloud TO azienda_user;
\q

# Importa schema
psql -U azienda_user -d azienda_cloud -f backend/schema.sql
```

### 2. Backend Setup

```bash
cd backend

# Crea virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate  # Windows

# Installa dipendenze
pip install -r requirements.txt

# Configura .env
cp .env.example .env
nano .env  # Modifica con le tue credenziali

# Avvia server
python server.py
```

✅ Backend pronto su http://localhost:8001

### 3. Frontend Setup

```bash
cd frontend

# Installa dipendenze
npm install

# Avvia development server
npm run dev
```

✅ Frontend pronto su http://localhost:3000

### 4. Test Rapido

1. Apri http://localhost:3000
2. Vai su "Dashboard" - dovresti vedere le statistiche
3. Vai su "Fatture" → clicca "Upload XML"
4. Carica un file XML FatturaPA

## 🔧 File `.env` Backend

```env
# Database Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxxxx.xxxxx.xxxxx

# Oppure PostgreSQL locale
DATABASE_URL=postgresql://azienda_user:password@localhost:5432/azienda_cloud

# Server
HOST=0.0.0.0
PORT=8001
RELOAD=True

# Logging
LOG_LEVEL=INFO
```

## 📝 Primo Utilizzo

### 1. Carica Prima Fattura

```bash
# Vai su http://localhost:3000/archive
# Clicca "Upload XML"
# Seleziona un file XML FatturaPA
# La fattura apparirà nella tabella "Attive"
```

### 2. Crea Primo Fornitore

```bash
# Vai su http://localhost:3000/suppliers
# Clicca "Nuovo Fornitore"
# Compila i dati
```

### 3. Visualizza Dashboard

```bash
# Vai su http://localhost:3000/dashboard
# Vedrai le statistiche aggiornate
```

## 🐛 Risoluzione Problemi

### Errore: "Cannot connect to database"
```bash
# Verifica credenziali in .env
# Verifica che PostgreSQL sia avviato
sudo systemctl status postgresql
```

### Errore: "Port 8001 already in use"
```bash
# Cambia porta in .env
PORT=8002
```

### Errore: "Module not found"
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### CORS Errors
```bash
# Verifica che nel backend ci sia:
allow_origins=["*"]
# O specifica l'origin del frontend:
allow_origins=["http://localhost:3000"]
```

## 📚 Prossimi Passi

1. ✅ Carica alcune fatture XML
2. ✅ Popola fornitori
3. ✅ Esplora le altre sezioni
4. 📖 Leggi [README.md](./README.md) per dettagli
5. 📖 Leggi documentazione API su http://localhost:8001/api/docs

## 🎓 Tutorial Video (Da creare)

- [ ] Setup iniziale
- [ ] Upload fatture
- [ ] Gestione fornitori
- [ ] Prima nota cassa
- [ ] HACCP

## 💡 Tips

- Usa `Ctrl + Shift + I` per aprire DevTools
- Controlla la console per errori
- Backend logs in terminale mostrano tutte le richieste
- Supabase dashboard mostra le query in tempo reale

## 🆘 Supporto

Problemi? Controlla:
1. Backend logs (terminale dove gira `python server.py`)
2. Frontend console (DevTools)
3. Supabase logs (se usi Supabase)
4. [GitHub Issues](https://github.com/your-repo/issues)

---

Buon lavoro! 🚀
