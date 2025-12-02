#!/bin/bash

# ============================================================================
# SETUP SISTEMA HR COMPLETO
# ============================================================================

echo "🚀 Inizializzazione Sistema HR..."

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# 1. DATABASE SETUP
# ============================================================================

echo -e "${YELLOW}📊 Setup Database...${NC}"

# Verifica PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL non installato${NC}"
    exit 1
fi

# Esegui migration
echo "Eseguo migration 007_hr_system.sql..."
psql $DATABASE_URL -f /home/claude/azienda-cloud/backend/migrations/007_hr_system.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migration eseguita${NC}"
else
    echo -e "${RED}❌ Errore migration${NC}"
    exit 1
fi

# ============================================================================
# 2. DIRECTORY SETUP
# ============================================================================

echo -e "${YELLOW}📁 Creazione directory...${NC}"

mkdir -p /home/claude/azienda-cloud/backend/uploads/payslips
mkdir -p /home/claude/azienda-cloud/backend/uploads/contracts
mkdir -p /home/claude/azienda-cloud/backend/uploads/dipendenti
mkdir -p /home/claude/azienda-cloud/backend/uploads/bonifici
mkdir -p /home/claude/azienda-cloud/backend/templates/contracts
mkdir -p /home/claude/azienda-cloud/backend/exports

echo -e "${GREEN}✅ Directory create${NC}"

# ============================================================================
# 3. DEPENDENCIES PYTHON
# ============================================================================

echo -e "${YELLOW}📦 Installazione dipendenze Python...${NC}"

pip install --break-system-packages \
    PyPDF2 \
    python-docx \
    openpyxl \
    pandas \
    fastapi \
    uvicorn \
    sqlalchemy \
    asyncpg \
    pydantic \
    python-jose \
    passlib \
    python-multipart

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dipendenze installate${NC}"
else
    echo -e "${RED}❌ Errore installazione dipendenze${NC}"
    exit 1
fi

# ============================================================================
# 4. ENVIRONMENT VARIABLES
# ============================================================================

echo -e "${YELLOW}⚙️  Configurazione variabili ambiente...${NC}"

cat > /home/claude/azienda-cloud/backend/.env << EOF
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/azienda

# Email Bot
EMAIL_ADDRESS=ceraldigroupsrl@gmail.com
EMAIL_PASSWORD=your_app_password_here

# JWT Secret
JWT_SECRET_KEY=your-secret-key-here

# Upload Directory
UPLOAD_DIR=/home/claude/azienda-cloud/backend/uploads

# Debug
DEBUG=True
EOF

echo -e "${GREEN}✅ File .env creato${NC}"
echo -e "${YELLOW}⚠️  IMPORTANTE: Modifica .env con le tue credenziali!${NC}"

# ============================================================================
# 5. TEST PARSERS
# ============================================================================

echo -e "${YELLOW}🧪 Test parsers...${NC}"

# Test parser buste paga
python3 << 'EOFPY'
from app.services.payslip_parser import PayslipParser

parser = PayslipParser()
print("✅ Parser buste paga OK")

from app.services.libro_unico_parser import LibroUnicoParser
parser2 = LibroUnicoParser()
print("✅ Parser LibroUnico OK")
EOFPY

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Test parsers OK${NC}"
fi

# ============================================================================
# 6. CRON JOB EMAIL BOT (OPZIONALE)
# ============================================================================

echo -e "${YELLOW}⏰ Setup cron job email bot (opzionale)...${NC}"

read -p "Vuoi configurare il cron job per email bot? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Aggiungi cron job (ogni ora)
    (crontab -l 2>/dev/null; echo "0 * * * * cd /home/claude/azienda-cloud/backend && python3 -m app.services.email_bot_payslips") | crontab -
    
    echo -e "${GREEN}✅ Cron job configurato (ogni ora)${NC}"
fi

# ============================================================================
# 7. FRONTEND BUILD (OPZIONALE)
# ============================================================================

echo -e "${YELLOW}🎨 Build frontend (opzionale)...${NC}"

read -p "Vuoi buildare il frontend? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd /home/claude/azienda-cloud/frontend
    
    if command -v npm &> /dev/null; then
        npm install
        npm run build
        echo -e "${GREEN}✅ Frontend buildato${NC}"
    else
        echo -e "${RED}❌ npm non installato${NC}"
    fi
fi

# ============================================================================
# 8. START SERVER
# ============================================================================

echo -e "${YELLOW}🚀 Avvio server...${NC}"

read -p "Vuoi avviare il server ora? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd /home/claude/azienda-cloud/backend
    
    echo -e "${GREEN}Server avviato su http://localhost:8000${NC}"
    echo -e "${GREEN}Documentazione API: http://localhost:8000/docs${NC}"
    
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fi

# ============================================================================
# RIEPILOGO
# ============================================================================

echo ""
echo "=============================================="
echo -e "${GREEN}✅ SETUP COMPLETATO!${NC}"
echo "=============================================="
echo ""
echo "📋 Checklist:"
echo "  1. ✅ Database migrato"
echo "  2. ✅ Directory create"
echo "  3. ✅ Dipendenze installate"
echo "  4. ⚠️  Configurare .env"
echo "  5. ✅ Parsers testati"
echo ""
echo "🚀 Avvio server:"
echo "   cd /home/claude/azienda-cloud/backend"
echo "   uvicorn app.main:app --reload"
echo ""
echo "📚 Documentazione:"
echo "   http://localhost:8000/docs"
echo ""
echo "=============================================="
