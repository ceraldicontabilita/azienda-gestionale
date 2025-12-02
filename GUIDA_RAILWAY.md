# 🚀 GUIDA RAILWAY - DEPLOY COMPLETO PASSO-PASSO

**Tempo totale: 15-20 minuti**

---

## ✅ COSA VEDRAI IN TEMPO REALE SU RAILWAY

Railway ti mostra **TUTTO LIVE**:

```
📊 Dashboard in tempo reale:
├── 🟢 Status (Online/Building/Crashed)
├── 📈 CPU Usage (%)
├── 💾 RAM Usage (MB)
├── 📡 Network Traffic
├── 📝 Logs LIVE (scorri e vedi tutto)
├── 🔄 Deployments (tutti i deploy)
├── ⚙️ Variables (ambiente)
├── 💰 Usage ($$$)
└── 🔗 Domain pubblico
```

---

## 🎯 STEP 1: CREA ACCOUNT RAILWAY (2 minuti)

### 1. Vai su Railway

```
https://railway.app
```

### 2. Sign Up

```
1. Clicca "Login"
2. Scegli "Login with GitHub"
3. Autorizza Railway
4. ✅ Account creato!
```

### 3. Verifica Email

```
1. Controlla email
2. Clicca link verifica
3. ✅ Account verificato!
```

**💰 Riceverai $5 credito GRATIS per iniziare!**

---

## 🎯 STEP 2: CARICA PROGETTO SU GITHUB (5 minuti)

### A. Installa Git (se non ce l'hai)

**Windows:**
```bash
# Scarica: https://git-scm.com/download/win
# Installa con opzioni default
```

**Mac:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt install git
```

### B. Configura Git

```bash
git config --global user.name "Tuo Nome"
git config --global user.email "tua-email@example.com"
```

### C. Crea Repository GitHub

```
1. Vai su https://github.com
2. Clicca icona "+" → "New repository"
3. Nome: azienda-cloud
4. Descrizione: Sistema Gestionale Aziendale
5. Privacy: Private (raccomandato)
6. ✅ Clicca "Create repository"
```

### D. Carica Codice

```bash
# Dalla cartella progetto
cd /home/claude/azienda-cloud

# Inizializza Git
git init

# Aggiungi tutti i file
git add .

# Primo commit
git commit -m "Initial commit - Sistema HR completo"

# Collega a GitHub (copia URL dal tuo repo)
git remote add origin https://github.com/TUO-USERNAME/azienda-cloud.git

# Carica su GitHub
git branch -M main
git push -u origin main
```

**✅ Codice ora su GitHub!**

---

## 🎯 STEP 3: DEPLOY SU RAILWAY (3 minuti)

### 1. Nuovo Progetto

```
1. Vai su https://railway.app/dashboard
2. Clicca "New Project"
3. Scegli "Deploy from GitHub repo"
```

### 2. Connetti Repository

```
1. Clicca "Configure GitHub App"
2. Seleziona il tuo account
3. Scegli "azienda-cloud" repository
4. Clicca "Install & Authorize"
```

### 3. Seleziona Repository

```
1. Vedrai lista repo
2. Clicca su "azienda-cloud"
3. Railway inizia automatic detection
```

### 4. Railway Rileva Python

```
Railway auto-rileva:
✅ Python project
✅ requirements.txt
✅ Procfile
✅ Porta dinamica $PORT

Clicca "Deploy Now"
```

### 5. Guarda Deploy in Tempo Reale! 🎉

```
Vedrai schermo con:
📦 Building...
├── Installing Python
├── Installing dependencies
├── Running build command
└── ✅ Build successful!

🚀 Deploying...
├── Starting container
├── Running start command
└── ✅ Deploy successful!

🟢 ONLINE!
```

---

## 🎯 STEP 4: AGGIUNGI DATABASE (2 minuti)

### 1. Aggiungi PostgreSQL

```
1. Nella dashboard progetto
2. Clicca "New" → "Database" → "Add PostgreSQL"
3. Railway crea database istantaneamente
4. ✅ Database pronto!
```

### 2. Railway Auto-Connette

```
Railway crea automaticamente:
✅ DATABASE_URL (variabile ambiente)
✅ Connection string completo
✅ Credentials sicure

Il tuo backend si connette automaticamente!
```

---

## 🎯 STEP 5: CONFIGURA VARIABILI (2 minuti)

### 1. Vai su Variables

```
Dashboard → Tuo servizio → Variables
```

### 2. Aggiungi Variabili

Railway **già ha DATABASE_URL**, aggiungi le altre:

```env
# JWT
JWT_SECRET_KEY=genera-stringa-random-lunga-64-caratteri
JWT_ALGORITHM=HS256

# Email (opzionale per ora)
EMAIL_ADDRESS=ceraldigroupsrl@gmail.com
EMAIL_PASSWORD=lascia-vuoto-per-ora

# App
DEBUG=False
ENVIRONMENT=production
CORS_ORIGINS=https://tuo-frontend.vercel.app

# Supabase (opzionale)
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=
```

### 3. Salva

```
Clicca "Add" per ogni variabile
Railway fa auto-redeploy
```

---

## 🎯 STEP 6: ESEGUI MIGRATION DATABASE (3 minuti)

### Opzione A: Da Railway CLI

```bash
# Installa Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link progetto
railway link

# Connetti al DB
railway run psql

# Esegui migration
\i backend/migrations/007_hr_system.sql

# Verifica tabelle
\dt
```

### Opzione B: Da Locale

```bash
# Copia DATABASE_URL da Railway dashboard
# Variables → DATABASE_URL → Copy

# Esegui migration
psql "postgresql://postgres:XXX@containers-us-west-XXX.railway.app:XXXX/railway" \
  -f backend/migrations/007_hr_system.sql
```

### Opzione C: Da Railway Dashboard

```
1. Vai su Database
2. Clicca "Data"
3. Clicca "Query"
4. Copia-incolla contenuto di 007_hr_system.sql
5. Esegui
6. ✅ Tabelle create!
```

---

## 🎯 STEP 7: VERIFICA FUNZIONAMENTO (2 minuti)

### 1. Ottieni URL Pubblico

```
Dashboard → Settings → Generate Domain
Railway crea: https://tuo-progetto.up.railway.app
```

### 2. Testa API

```
Apri browser:
https://tuo-progetto.up.railway.app/docs

Dovresti vedere:
✅ Swagger UI con tutte le API
✅ Endpoints funzionanti
✅ Database connesso
```

### 3. Test Login

```
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}

Dovresti ricevere token JWT!
```

---

## 📊 MONITORING IN TEMPO REALE

### Dashboard Railway

```
🟢 Status:
├── Online
├── CPU: 5%
├── RAM: 120 MB
└── Uptime: 99.9%

📝 Logs Live:
INFO: Application startup complete
INFO: Uvicorn running on http://0.0.0.0:XXXX
✅ Database connected

📈 Metrics (ultimi 7 giorni):
├── Requests: 1,234
├── Errors: 0
└── Response time: 45ms

💰 Usage:
$0.50 / $5.00 used questo mese
```

### Logs in Tempo Reale

```
1. Dashboard → Logs tab
2. Vedi TUTTO in live:
   - Ogni richiesta API
   - Ogni errore
   - Ogni query database
   - Startup/shutdown
```

---

## 🐛 TROUBLESHOOTING

### Deploy Failed

```
1. Guarda logs
2. Cerca errore rosso
3. Solitamente è:
   - Dipendenza mancante → Aggiungi a requirements.txt
   - Porta sbagliata → Usa $PORT
   - Database non connesso → Verifica DATABASE_URL
```

### Database Connection Error

```
1. Verifica DATABASE_URL presente
2. Dashboard → Variables → DATABASE_URL
3. Deve iniziare con: postgresql://
```

### 500 Internal Error

```
1. Logs → Cerca stack trace
2. Spesso è:
   - Tabelle mancanti → Esegui migration
   - Variabile ambiente mancante
```

---

## 💰 COSTI RAILWAY

### Piano Hobby ($5/mese)

```
Include:
✅ 500 ore server
✅ PostgreSQL database
✅ 5 progetti
✅ 8GB RAM
✅ Custom domains
✅ Logs illimitati
✅ Auto-SSL

Per te: PERFETTO!
```

### Usage Monitor

```
Dashboard → Usage
Vedi in tempo reale:
- $ spesi oggi
- Ore consumate
- Stima fine mese
```

---

## 🎯 COMANDI UTILI

### Redeploy

```bash
# Da locale, dopo modifiche
git add .
git commit -m "Update feature"
git push

# Railway auto-redeploy!
```

### Logs Live

```bash
# Da terminale
railway logs

# Follow mode
railway logs --follow
```

### Variabili

```bash
# Lista variabili
railway variables

# Aggiungi variabile
railway variables set KEY=value
```

---

## 🚀 PROSSIMI PASSI

### 1. Custom Domain (opzionale)

```
Settings → Domains → Add Custom Domain
Esempio: api.tuosito.com
```

### 2. Backup Automatici

```
Railway fa backup automatici del DB
Retention: 7 giorni
```

### 3. Monitoring

```
Integra:
- Sentry (errori)
- Better Stack (uptime)
- Grafana (metrics)
```

---

## ✅ CHECKLIST FINALE

- [ ] Account Railway creato
- [ ] $5 credito ricevuto
- [ ] Codice su GitHub
- [ ] Deploy completato
- [ ] Database aggiunto
- [ ] Migration eseguita
- [ ] Variabili configurate
- [ ] URL pubblico funzionante
- [ ] /docs accessibile
- [ ] Login testato
- [ ] Logs visualizzati

---

## 🎉 COMPLIMENTI!

Il tuo sistema è **ONLINE E FUNZIONANTE**!

**URL:** https://tuo-progetto.up.railway.app/docs

Ora puoi:
- ✅ Testare tutte le API
- ✅ Vedere logs in tempo reale
- ✅ Monitorare performance
- ✅ Aggiungere dipendenti
- ✅ Import buste paga
- ✅ Tutto online 24/7!

---

**Serve aiuto?** Railway ha supporto Discord attivo 24/7!

*Guida creata: 02/12/2025*
