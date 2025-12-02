# ⚙️ CONFIGURAZIONE SUPABASE

**Sistema Gestionale Aziendale - Cloud Database**

---

## 📝 CREDENZIALI NECESSARIE

Per configurare Supabase, ho bisogno di:

### 1. **Supabase Project URL**
```
Esempio: https://xyzabcdefg.supabase.co
```
**Dove trovarla:**
- Login su https://supabase.com
- Vai su Project Settings → API
- Copia "Project URL"

### 2. **Supabase Anon/Public Key**
```
Esempio: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
**Dove trovarla:**
- Project Settings → API
- Copia "anon" key (public key)

### 3. **Supabase Service Role Key** (Admin)
```
Esempio: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
**Dove trovarla:**
- Project Settings → API
- Copia "service_role" key
- ⚠️ IMPORTANTE: Questa chiave ha accesso completo al DB

### 4. **Database Connection String**
```
Esempio: postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
```
**Dove trovarla:**
- Project Settings → Database
- Copia "Connection string" (URI format)
- Sostituisci `[YOUR-PASSWORD]` con la password del DB

---

## 🔧 COME CONFIGURARE

### Opzione A: File .env (Raccomandato)

Crea/modifica file `backend/.env`:

```env
# ============================================================================
# SUPABASE CONFIGURATION
# ============================================================================

# Project URL
SUPABASE_URL=https://INSERISCI-QUI-PROJECT-URL.supabase.co

# Public Key (anon)
SUPABASE_ANON_KEY=INSERISCI-QUI-ANON-KEY

# Service Role Key (admin - NON COMMITTARE SU GIT!)
SUPABASE_SERVICE_KEY=INSERISCI-QUI-SERVICE-ROLE-KEY

# Database Connection String
DATABASE_URL=postgresql://postgres.INSERISCI-QUI-CONNECTION-STRING

# ============================================================================
# OTHER SETTINGS
# ============================================================================

# JWT Secret (per auth custom)
JWT_SECRET_KEY=GENERA-STRINGA-RANDOM-SICURA

# Email Bot
EMAIL_ADDRESS=ceraldigroupsrl@gmail.com
EMAIL_PASSWORD=INSERISCI-APP-PASSWORD-GMAIL

# Environment
DEBUG=True
ENVIRONMENT=development
```

### Opzione B: Variabili d'Ambiente Sistema

```bash
# Linux/Mac
export SUPABASE_URL="https://..."
export SUPABASE_ANON_KEY="eyJ..."
export DATABASE_URL="postgresql://..."

# Windows CMD
set SUPABASE_URL=https://...
set SUPABASE_ANON_KEY=eyJ...

# Windows PowerShell
$env:SUPABASE_URL="https://..."
$env:SUPABASE_ANON_KEY="eyJ..."
```

---

## 📋 CHECKLIST SETUP

- [ ] **Creato progetto Supabase**
- [ ] **Copiata Project URL**
- [ ] **Copiata Anon Key**
- [ ] **Copiata Service Role Key**
- [ ] **Copiata Connection String**
- [ ] **Creato file .env**
- [ ] **Testata connessione**

---

## 🧪 TEST CONNESSIONE

Dopo aver configurato le credenziali:

```bash
cd backend
python3 -c "
import os
from dotenv import load_dotenv

load_dotenv()

print('🔍 Verifica Configurazione Supabase:')
print()
print(f'SUPABASE_URL: {os.getenv(\"SUPABASE_URL\")[:30]}...')
print(f'SUPABASE_ANON_KEY: {os.getenv(\"SUPABASE_ANON_KEY\")[:30]}...')
print(f'DATABASE_URL: {os.getenv(\"DATABASE_URL\")[:30]}...')
print()
print('✅ Configurazione presente!')
"
```

---

## 🚀 INTEGRAZIONE NEL CODICE

### File: `backend/app/database.py`

```python
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import asyncpg

load_dotenv()

# Supabase Client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Database Pool (asyncpg)
database_url = os.getenv("DATABASE_URL")

async def get_db():
    """Get database connection"""
    conn = await asyncpg.connect(database_url)
    try:
        yield conn
    finally:
        await conn.close()
```

### File: `backend/app/main.py`

```python
from app.database import supabase, get_db

# Usa supabase per operazioni real-time
# Usa get_db() per query SQL dirette
```

---

## 📊 MIGRAZIONE DATABASE

Una volta connesso, esegui migration:

```bash
# Connetti a Supabase
psql "postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"

# Esegui migration
\i backend/migrations/007_hr_system.sql

# Verifica tabelle
\dt
```

**Oppure via Supabase Dashboard:**
1. Vai su SQL Editor
2. Copia contenuto di `007_hr_system.sql`
3. Esegui query

---

## 🔐 SICUREZZA

### ⚠️ IMPORTANTE

1. **MAI committare .env su Git**
   ```bash
   # Aggiungi a .gitignore
   echo ".env" >> .gitignore
   echo "**/.env" >> .gitignore
   ```

2. **Service Role Key = Admin**
   - NON esporre mai nel frontend
   - Solo per backend
   - Accesso completo al DB

3. **Anon Key = Public**
   - OK da usare nel frontend
   - Accesso limitato da RLS (Row Level Security)

4. **Abilita Row Level Security**
   ```sql
   -- Esempio policy
   ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
   
   CREATE POLICY "Users can view their own data"
   ON employees
   FOR SELECT
   USING (auth.uid() = user_id);
   ```

---

## 📦 DIPENDENZE PYTHON

Installa client Supabase:

```bash
pip install --break-system-packages \
    supabase-py \
    asyncpg \
    python-dotenv
```

---

## 🎯 TEMPLATE .env COMPLETO

```env
# ============================================================================
# SUPABASE
# ============================================================================
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.[...]
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.[...]
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:5432/postgres

# ============================================================================
# JWT
# ============================================================================
JWT_SECRET_KEY=[GENERA-STRINGA-RANDOM-64-CARATTERI]
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================================================
# EMAIL BOT
# ============================================================================
EMAIL_ADDRESS=ceraldigroupsrl@gmail.com
EMAIL_PASSWORD=[GMAIL-APP-PASSWORD]
EMAIL_SERVER=imap.gmail.com
EMAIL_PORT=993

# ============================================================================
# APPLICATION
# ============================================================================
DEBUG=True
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# ============================================================================
# FILE UPLOAD
# ============================================================================
UPLOAD_DIR=/home/claude/azienda-cloud/backend/uploads
MAX_FILE_SIZE=10485760  # 10MB

# ============================================================================
# MONITORING (Optional)
# ============================================================================
SENTRY_DSN=
LOG_LEVEL=INFO
```

---

## 🆘 TROUBLESHOOTING

### Errore: "Connection refused"
```bash
# Verifica URL
echo $SUPABASE_URL

# Ping server
curl -I https://[PROJECT-REF].supabase.co
```

### Errore: "Invalid API key"
```bash
# Verifica lunghezza key
echo $SUPABASE_ANON_KEY | wc -c
# Deve essere ~300+ caratteri
```

### Errore: "Database does not exist"
```bash
# Verifica connection string
# Deve contenere: postgres.[PROJECT-REF]
```

---

## 📞 SUPPORTO

**Dove trovare le credenziali:**
1. Login: https://supabase.com
2. Seleziona progetto
3. Settings → API
4. Settings → Database

**Documentazione Supabase:**
- https://supabase.com/docs
- https://supabase.com/docs/guides/database

---

**Una volta fornite le credenziali, implementerò:**
✅ Connessione database  
✅ Client Supabase  
✅ Auth con JWT  
✅ Row Level Security  
✅ Real-time subscriptions

---

*File creato: SUPABASE_SETUP.md*
