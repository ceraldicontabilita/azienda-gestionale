"""
Parser PDF Buste Paga Zucchetti
Estrae: nome, cognome, netto, acconto, saldo, mansione, mese/anno
"""

import pdfplumber
import re
from typing import Dict, Optional
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class BustaPagaParser:
    """Parser per PDF buste paga Zucchetti"""
    
    # Pattern regex per estrazione dati
    PATTERNS = {
        'nome_cognome': r'(?:Sig\.|Sig\.ra|Dott\.|Dott\.ssa)?\s*([A-Z][a-zà-ù]+)\s+([A-Z][A-ZÀ-Ù]+)',
        'codice_fiscale': r'C\.F\.\s*:?\s*([A-Z0-9]{16})',
        'netto': r'(?:NETTO|Netto|NET)\s*:?\s*€?\s*([\d.]+[,\d]*)',
        'acconto': r'(?:ACCONTO|Acconto)\s*:?\s*€?\s*([\d.]+[,\d]*)',
        'saldo': r'(?:SALDO|Saldo)\s*:?\s*€?\s*([\d.]+[,\d]*)',
        'lordo': r'(?:LORDO|Lordo|IMPONIBILE)\s*:?\s*€?\s*([\d.]+[,\d]*)',
        'mansione': r'(?:Mansione|Qualifica|Livello)\s*:?\s*([A-Za-z\s]+)',
        'mese_anno': r'(?:Periodo|Mese|Competenza)\s*:?\s*(\d{1,2})[\/\-](\d{4})',
        'inps': r'(?:INPS|Contr\.\s*INPS)\s*:?\s*€?\s*([\d.]+[,\d]*)',
        'inail': r'(?:INAIL)\s*:?\s*€?\s*([\d.]+[,\d]*)',
        'irpef': r'(?:IRPEF)\s*:?\s*€?\s*([\d.]+[,\d]*)',
    }
    
    def parse_pdf(self, pdf_path: str) -> Dict:
        """
        Parse PDF busta paga
        
        Args:
            pdf_path: Path del file PDF
            
        Returns:
            Dict con dati estratti
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Estrae testo da tutte le pagine
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
                
                return self._extract_data(full_text)
                
        except Exception as e:
            logger.error(f"Errore parsing PDF busta paga: {str(e)}")
            raise ValueError(f"Impossibile leggere il PDF: {str(e)}")
    
    def _extract_data(self, text: str) -> Dict:
        """Estrae dati strutturati dal testo"""
        
        data = {
            'nome': None,
            'cognome': None,
            'codice_fiscale': None,
            'netto': None,
            'acconto': None,
            'saldo': None,
            'lordo': None,
            'mansione': None,
            'mese': None,
            'anno': None,
            'inps_dipendente': None,
            'inail': None,
            'irpef': None,
        }
        
        # Nome e Cognome
        nome_match = re.search(self.PATTERNS['nome_cognome'], text)
        if nome_match:
            data['nome'] = nome_match.group(1).strip()
            data['cognome'] = nome_match.group(2).strip()
        
        # Codice Fiscale
        cf_match = re.search(self.PATTERNS['codice_fiscale'], text)
        if cf_match:
            data['codice_fiscale'] = cf_match.group(1).strip()
        
        # Netto
        netto_match = re.search(self.PATTERNS['netto'], text)
        if netto_match:
            data['netto'] = self._parse_currency(netto_match.group(1))
        
        # Acconto
        acconto_match = re.search(self.PATTERNS['acconto'], text)
        if acconto_match:
            data['acconto'] = self._parse_currency(acconto_match.group(1))
        
        # Saldo
        saldo_match = re.search(self.PATTERNS['saldo'], text)
        if saldo_match:
            data['saldo'] = self._parse_currency(saldo_match.group(1))
        
        # Se non c'è saldo, calcola: saldo = netto - acconto
        if data['netto'] and data['acconto'] and not data['saldo']:
            data['saldo'] = data['netto'] - data['acconto']
        
        # Lordo
        lordo_match = re.search(self.PATTERNS['lordo'], text)
        if lordo_match:
            data['lordo'] = self._parse_currency(lordo_match.group(1))
        
        # Mansione
        mansione_match = re.search(self.PATTERNS['mansione'], text)
        if mansione_match:
            data['mansione'] = mansione_match.group(1).strip()
        
        # Mese e Anno
        mese_anno_match = re.search(self.PATTERNS['mese_anno'], text)
        if mese_anno_match:
            data['mese'] = int(mese_anno_match.group(1))
            data['anno'] = int(mese_anno_match.group(2))
        else:
            # Fallback: cerca pattern alternativi
            for month_name, month_num in [
                ('gennaio', 1), ('febbraio', 2), ('marzo', 3), ('aprile', 4),
                ('maggio', 5), ('giugno', 6), ('luglio', 7), ('agosto', 8),
                ('settembre', 9), ('ottobre', 10), ('novembre', 11), ('dicembre', 12)
            ]:
                if month_name.lower() in text.lower():
                    data['mese'] = month_num
                    # Cerca anno vicino al mese
                    year_match = re.search(rf'{month_name}\s*(\d{{4}})', text, re.IGNORECASE)
                    if year_match:
                        data['anno'] = int(year_match.group(1))
                    break
        
        # INPS
        inps_match = re.search(self.PATTERNS['inps'], text)
        if inps_match:
            data['inps_dipendente'] = self._parse_currency(inps_match.group(1))
        
        # INAIL
        inail_match = re.search(self.PATTERNS['inail'], text)
        if inail_match:
            data['inail'] = self._parse_currency(inail_match.group(1))
        
        # IRPEF
        irpef_match = re.search(self.PATTERNS['irpef'], text)
        if irpef_match:
            data['irpef'] = self._parse_currency(irpef_match.group(1))
        
        return data
    
    def _parse_currency(self, value: str) -> Optional[Decimal]:
        """Converte stringa valuta in Decimal"""
        try:
            # Rimuove punti come separatori delle migliaia
            value = value.replace('.', '')
            # Sostituisce virgola con punto per decimali
            value = value.replace(',', '.')
            # Rimuove spazi e simboli
            value = value.strip().replace('€', '').replace(' ', '')
            return Decimal(value) if value else None
        except:
            return None
    
    def validate_data(self, data: Dict) -> bool:
        """
        Valida che i dati essenziali siano presenti
        
        Args:
            data: Dati estratti
            
        Returns:
            True se validi, False altrimenti
        """
        required_fields = ['nome', 'cognome', 'netto']
        return all(data.get(field) for field in required_fields)


def parse_busta_paga(pdf_path: str) -> Dict:
    """
    Funzione helper per parsing PDF busta paga
    
    Args:
        pdf_path: Path del file PDF
        
    Returns:
        Dict con dati estratti
    """
    parser = BustaPagaParser()
    data = parser.parse_pdf(pdf_path)
    
    if not parser.validate_data(data):
        raise ValueError("Dati estratti non validi o incompleti")
    
    return data
