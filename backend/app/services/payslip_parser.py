"""
Parser Buste Paga PDF Zucchetti
Estrae dati da PDF buste paga formato Zucchetti
"""
import re
from decimal import Decimal
from typing import Dict, Optional
try:
    import PyPDF2
    from io import BytesIO
except ImportError:
    PyPDF2 = None
    BytesIO = None


class PayslipParser:
    """Parser per buste paga PDF formato Zucchetti"""
    
    def parse_pdf(self, pdf_data: bytes) -> Optional[Dict]:
        """
        Parse PDF busta paga e estrae tutti i dati
        
        Returns dict con:
        - codice_fiscale
        - nome, cognome
        - periodo (YYYY-MM)
        - retribuzione_lorda
        - netto_in_busta
        - contributi, irpef, ecc
        - ferie, permessi
        - iban
        """
        if not PyPDF2:
            print("❌ PyPDF2 non installato. Installa con: pip install PyPDF2")
            return None
            
        try:
            # Leggi PDF
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
            
            # Estrai tutto il testo
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Parse dati
            data = self._extract_data(text)
            
            return data
            
        except Exception as e:
            print(f"Errore parsing PDF: {e}")
            return None
    
    def _extract_data(self, text: str) -> Dict:
        """Estrae dati dal testo PDF"""
        
        data = {}
        
        # CODICE FISCALE (16 caratteri)
        cf_match = re.search(r'\b([A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z])\b', text)
        if cf_match:
            data['codice_fiscale'] = cf_match.group(1)
        
        # NOME E COGNOME
        # Cerca pattern "COGNOME NOME" o "Lavoratore: COGNOME NOME"
        name_match = re.search(r'(?:Lavoratore:|COGNOME.*NOME)\s*([A-Z\s]+)', text)
        if name_match:
            full_name = name_match.group(1).strip()
            parts = full_name.split()
            if len(parts) >= 2:
                data['cognome'] = parts[0]
                data['nome'] = ' '.join(parts[1:])
        
        # PERIODO (Marzo 2025)
        periodo_match = re.search(r'(Gennaio|Febbraio|Marzo|Aprile|Maggio|Giugno|Luglio|Agosto|Settembre|Ottobre|Novembre|Dicembre)\s+(\d{4})', text)
        if periodo_match:
            mese_nome = periodo_match.group(1)
            anno = periodo_match.group(2)
            
            mesi = {
                'Gennaio': '01', 'Febbraio': '02', 'Marzo': '03',
                'Aprile': '04', 'Maggio': '05', 'Giugno': '06',
                'Luglio': '07', 'Agosto': '08', 'Settembre': '09',
                'Ottobre': '10', 'Novembre': '11', 'Dicembre': '12'
            }
            
            mese = mesi.get(mese_nome, '01')
            data['periodo'] = f"{anno}-{mese}"
            data['anno'] = int(anno)
            data['mese'] = int(mese)
        
        # RETRIBUZIONE LORDA (cerca "Retribuzione" e importo)
        retr_match = re.search(r'Z00001\s+Retribuzione\s+[\d,\.]+\s+[\d,\.]+\s+ORE\s+([\d,\.]+)', text)
        if retr_match:
            data['retribuzione_lorda'] = self._parse_decimal(retr_match.group(1))
        
        # NETTO IN BUSTA (ultima riga con €)
        netto_match = re.search(r'NETTO.*MESE\s+([\d,\.]+)\s*€', text, re.IGNORECASE)
        if netto_match:
            data['netto_in_busta'] = self._parse_decimal(netto_match.group(1))
        
        # CONTRIBUTI INPS
        inps_match = re.search(r'Z00000\s+Contributo IVS\s+[\d,\.]+\s+[\d,\.]+\s*%\s+([\d,\.]+)', text)
        if inps_match:
            data['inps_dipendente'] = self._parse_decimal(inps_match.group(1))
        
        # IRPEF
        irpef_match = re.search(r'F03020\s+Ritenute IRPEF\s+([\d,\.]+)', text)
        if irpef_match:
            data['irpef'] = self._parse_decimal(irpef_match.group(1))
        
        # ADDIZIONALE REGIONALE
        add_reg_match = re.search(r'F09110\s+Addizionale regionale.*?\s+([\d,\.]+)', text)
        if add_reg_match:
            data['addizionale_regionale'] = self._parse_decimal(add_reg_match.group(1))
        
        # ADDIZIONALE COMUNALE
        add_com_match = re.search(r'F09130\s+Addizionale comunale.*?\s+([\d,\.]+)', text)
        if add_com_match:
            data['addizionale_comunale'] = self._parse_decimal(add_com_match.group(1))
        
        # TFR MATURATO
        tfr_match = re.search(r'Quota anno\s+([\d,\.]+)', text)
        if tfr_match:
            data['tfr_maturato'] = self._parse_decimal(tfr_match.group(1))
        
        # TFR PROGRESSIVO
        tfr_prog_match = re.search(r'F\.do 31/12\s+([\d,\.]+)', text)
        if tfr_prog_match:
            data['tfr_progressivo'] = self._parse_decimal(tfr_prog_match.group(1))
        
        # FERIE
        ferie_match = re.search(r'Ferie\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+([-\d,\.]+)', text)
        if ferie_match:
            data['ferie_residue_ap'] = self._parse_decimal(ferie_match.group(1))
            data['ferie_maturate'] = self._parse_decimal(ferie_match.group(2))
            data['ferie_godute'] = self._parse_decimal(ferie_match.group(3))
            data['ferie_residue'] = self._parse_decimal(ferie_match.group(4))
        
        # PERMESSI
        permessi_match = re.search(r'Permessi\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+ORE', text)
        if permessi_match:
            data['permessi_residui_ap'] = self._parse_decimal(permessi_match.group(1))
            data['permessi_maturati'] = self._parse_decimal(permessi_match.group(2))
            data['permessi_residui'] = self._parse_decimal(permessi_match.group(3))
        
        # ORE LAVORATE
        ore_match = re.search(r'Z00001\s+Retribuzione\s+([\d,\.]+)\s+([\d,\.]+)\s+ORE', text)
        if ore_match:
            data['ore_ordinarie'] = self._parse_decimal(ore_match.group(2))
        
        # IBAN
        iban_match = re.search(r'IBAN\s+([A-Z]{2}\d{2}[A-Z0-9]+)', text)
        if iban_match:
            data['iban'] = iban_match.group(1)
        
        # BANCA
        banca_match = re.search(r'IBAN.*?\n([A-Z\s\.]+?)\n', text)
        if banca_match:
            data['banca'] = banca_match.group(1).strip()
        
        # LIVELLO E MANSIONE
        livello_match = re.search(r"OPE\s+(\d['']?\s*Livello(?:\s+Super)?)", text)
        if livello_match:
            data['livello'] = livello_match.group(1)
        
        mansione_match = re.search(r'Livello(?:\s+Super)?\n([A-Z\s]+?)\n', text)
        if mansione_match:
            data['mansione'] = mansione_match.group(1).strip()
        
        # GIORNI LAVORATI
        giorni_match = re.search(r'Giorni\nLavorati.*?(\d+)', text, re.DOTALL)
        if giorni_match:
            data['giorni_lavorati'] = int(giorni_match.group(1))
        
        return data
    
    def _parse_decimal(self, value: str) -> Decimal:
        """Converte stringa in Decimal (gestisce . e ,)"""
        if not value:
            return Decimal('0')
        
        # Rimuovi spazi
        value = value.strip()
        
        # Sostituisci , con .
        value = value.replace(',', '.')
        
        # Rimuovi punti come separatori migliaia (es: 1.234,56 -> 1234.56)
        parts = value.split('.')
        if len(parts) > 2:
            value = ''.join(parts[:-1]) + '.' + parts[-1]
        
        try:
            return Decimal(value)
        except:
            return Decimal('0')
    
    def identify_employee_from_pdf(self, pdf_data: bytes) -> Optional[str]:
        """
        Identifica il codice fiscale dal PDF
        Utile per associare la busta al dipendente
        """
        data = self.parse_pdf(pdf_data)
        return data.get('codice_fiscale') if data else None


# Test parser
if __name__ == '__main__':
    # Test con un PDF di esempio
    parser = PayslipParser()
    
    test_pdf_path = '/mnt/user-data/uploads/LibroUnico_Nome_E_Indirizzo_01-2009.pdf'
    
    try:
        with open(test_pdf_path, 'rb') as f:
            data = parser.parse_pdf(f.read())
            
        if data:
            print("✅ PARSING RIUSCITO!")
            print(f"Codice Fiscale: {data.get('codice_fiscale')}")
            print(f"Nome: {data.get('nome')} {data.get('cognome')}")
            print(f"Periodo: {data.get('periodo')}")
            print(f"Netto: €{data.get('netto_in_busta')}")
        else:
            print("❌ Parsing fallito")
            
    except Exception as e:
        print(f"❌ Errore: {e}")
