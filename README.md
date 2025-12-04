# 🚀 AZIENDA GESTIONALE - SETUP COMPLETO

## 📋 CONTENUTO

```
├── auth.py                    # Nuovo file auth (copia su GitHub)
├── requirements.txt           # Dependencies (copia su GitHub)
├── GUIDA_RENDER.md           # Guida deploy su Render
├── GUIDA_EMERGENT_SH.md      # Guida deploy su Emergent.sh
├── SETUP_SUPABASE.sql        # SQL per creare utente admin
└── README.md                 # Questo file
```

## ⚡ QUICK START (5 minuti)

### 1. Aggiorna GitHub

Sostituisci questi file nel tuo repo:
- `backend/app/routers/auth.py` → copia il nuovo `auth.py`
- `backend/requirements.txt` → copia il nuovo `requirements.txt`

```bash
git add backend/app/routers/auth.py backend/requirements.txt
git commit -m "Fix: Authentication and dependencies"
git push
```

### 2. Setup Supabase

1. Vai a: https://supabase.com/dashboard
2. Accedi con: `ceraldicontabilita@gmail.com`
3. Seleziona progetto `azienda-gestionale`
4. Vai a "SQL Editor" → "New Query"
5. Copia il contenuto di `SETUP_SUPABASE.sql`
6. Clicca "RUN"

Questo crea la tabella `users` e l'utente `admin@tuaazienda.it` con password `password`.

### 3. Deploy

Scegli una piattaforma:

**OPZIONE A: RENDER (Consigliato - più stabile)**
- Segui: `GUIDA_RENDER.md`
- Tempo: 5 minuti
- Costo: Gratuito

**OPZIONE B: EMERGENT.SH (Alternativa italiana)**
- Segui: `GUIDA_EMERGENT_SH.md`
- Tempo: 5 minuti
- Costo: Dipende dal piano

## 🔑 CREDENZIALI DI TEST

Una volta deployato, usa queste credenziali per testare il login:

```
Email: admin@tuaazienda.it
Password: password
```

Vai a: `https://your-backend-url/docs`

Clicca `POST /api/auth/token` e prova il login.

## ❌ SE NON FUNZIONA

### Errore: "Auth router not loaded"

**Soluzione:**
1. Verifica che `auth.py` sia in: `backend/app/routers/auth.py`
2. Il file deve avere esattamente 97 righe
3. Controlla che `requirements.txt` abbia `PyJWT` e `bcrypt`

### Errore: "Credenziali non valide"

**Soluzione:**
1. Verifica che l'utente `admin@tuaazienda.it` esista in Supabase
2. Controlla che il password_hash sia: `$2b$12$UDbMJc5v3Vn7MdkdB0pvfe32w8WIC.32CvL2fXsSNCuafWZHQRkrW`
3. Fai una query di verifica in Supabase: `SELECT * FROM users WHERE email = 'admin@tuaazienda.it';`

### Errore: "Database connection failed"

**Soluzione:**
1. Controlla che `DATABASE_URL` sia corretta su Render/Emergent.sh
2. Controlla che `SUPABASE_URL` e `SUPABASE_SERVICE_KEY` siano corretti
3. Verifica che la password Supabase sia: `Ceraldicloud2025`

## 📞 SUPPORT

Se hai problemi:
1. Leggi i logs della piattaforma (Render o Emergent.sh)
2. Verifica che tutti i file siano stati caricati su GitHub
3. Controlla che tutte le variabili d'ambiente siano impostate

## ✅ CHECKLIST FINALE

- [ ] `auth.py` caricato su GitHub
- [ ] `requirements.txt` caricato su GitHub
- [ ] SQL di Supabase eseguito (tabella `users` creata)
- [ ] Utente `admin@tuaazienda.it` creato in Supabase
- [ ] Deploy completato su Render o Emergent.sh
- [ ] Tutte le variabili d'ambiente configurate
- [ ] Test login effettuato con successo

## 🎉 FATTO!

Una volta completati tutti gli step, il tuo backend è live e il login funziona!

Buona fortuna! 🚀
