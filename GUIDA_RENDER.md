# 🚀 GUIDA DEPLOY SU RENDER

## STEP 1: Prepara GitHub

1. Sostituisci il file `backend/app/routers/auth.py` con il nuovo `auth.py` fornito
2. Sostituisci `backend/requirements.txt` con il nuovo requirements.txt fornito
3. Fai commit e push su GitHub

```bash
git add backend/app/routers/auth.py backend/requirements.txt
git commit -m "Fix: Authentication login endpoint"
git push
```

## STEP 2: Crea account Render

1. Vai a: https://render.com
2. Clicca "Sign up" → "Continue with GitHub"
3. Autorizza Render ad accedere ai tuoi repo

## STEP 3: Crea Web Service

1. Dashboard Render → Click "New+" → "Web Service"
2. Seleziona il repo `azienda-gestionale`
3. Clicca "Connect"

## STEP 4: Configura Deploy

**Nome e Ambiente:**
- Name: `azienda-backend`
- Environment: `Python 3`
- Branch: `main`
- Root Directory: `backend`

**Build Command:**
```
pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command:**
```
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## STEP 5: Aggiungi Variabili d'Ambiente

Clicca "Add Environment Variable" per ogni variabile:

```
DATABASE_URL=postgresql://postgres:Ceraldicloud2025@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://ccwbndzimwplzzbgmrdn.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjd2JuZHppbXdwbHp6YmdtcmRuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDY2ODEyMywiZXhwIjoyMDgwMjQ0MTIzfQ.1AdBSIkncG2nMrgtN2LLsKTyR6CvSkSHb2yh6VJFFYo
JWT_SECRET_KEY=84b78ce64da758816769172816a8bec4ef6b8ee18cf145d5336aa83a5dfd65ff
DEBUG=False
ENVIRONMENT=production
PORT=8080
```

## STEP 6: Deploy

1. Scorri in basso
2. Clicca il pulsante blu "Create Web Service"
3. Render fa il deploy automatico (3-5 minuti)

## STEP 7: Verifica

1. Una volta completato, vai all'URL pubblico che Render ti mostra
2. Aggiungi `/docs` all'URL
3. Dovrebbe mostrare lo Swagger con "Authentication" in cima
4. Clicca `POST /api/auth/token`
5. Prova il login:
   - username: `admin@tuaazienda.it`
   - password: `password`

## ✅ FATTO!

Il tuo backend è live su Render! 🎉

Se vedi errori nei logs, controlla:
- La DATABASE_URL è corretta?
- L'utente admin@tuaazienda.it esiste in Supabase?
- Tutte le variabili d'ambiente sono configurate?
