"""
Parser XML FatturaPA Ottimizzato per File Reali
Analizzato da fatture reali: Google Cloud, TIM, ecc.
"""
import xml.etree.ElementTree as ET

def parse_fattura_xml(xml_content):
    """
    Parse XML FatturaPA con gestione namespace automatica
    
    Returns:
        dict con chiavi:
        - numero_fattura: str
        - data_fattura: str (YYYY-MM-DD)
        - partita_iva_fornitore: str
        - ragione_sociale_fornitore: str
        - imponibile: float
        - iva: float
        - totale: float
        - righe: list[dict]
    """
    
    root = ET.fromstring(xml_content)
    
    # Namespace FatturaPA standard
    ns = {'p': 'http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2'}
    
    def get_text(elem, path, default=''):
        """Helper: cerca con e senza namespace"""
        # Con namespace
        result = elem.find(path, ns)
        if result is not None and result.text:
            return result.text.strip()
        
        # Senza namespace (fallback)
        path_clean = path.replace('p:', '').replace('.//p:', './/')
        result = elem.find(path_clean)
        if result is not None and result.text:
            return result.text.strip()
        
        return default
    
    # Inizializza risultato
    data = {
        'numero_fattura': None,
        'data_fattura': None,
        'partita_iva_fornitore': None,
        'ragione_sociale_fornitore': None,
        'imponibile': 0.0,
        'iva': 0.0,
        'totale': 0.0,
        'righe': []
    }
    
    # ========== HEADER - FORNITORE ==========
    cedente = root.find('.//p:CedentePrestatore', ns)
    if cedente is None:
        cedente = root.find('.//CedentePrestatore')
    
    if cedente is not None:
        # P.IVA Fornitore
        piva = get_text(cedente, './/p:IdFiscaleIVA/p:IdCodice')
        if not piva:
            piva = get_text(cedente, './/IdFiscaleIVA/IdCodice')
        data['partita_iva_fornitore'] = piva
        
        # Ragione Sociale
        ragione = get_text(cedente, './/p:Anagrafica/p:Denominazione')
        if not ragione:
            ragione = get_text(cedente, './/Anagrafica/Denominazione')
        data['ragione_sociale_fornitore'] = ragione
    
    # ========== BODY - FATTURA ==========
    body = root.find('.//p:FatturaElettronicaBody', ns)
    if body is None:
        body = root.find('.//FatturaElettronicaBody')
    
    if body is not None:
        # Numero e Data Fattura
        numero = get_text(body, './/p:DatiGeneraliDocumento/p:Numero')
        if not numero:
            numero = get_text(body, './/DatiGeneraliDocumento/Numero')
        data['numero_fattura'] = numero
        
        data_fattura = get_text(body, './/p:DatiGeneraliDocumento/p:Data')
        if not data_fattura:
            data_fattura = get_text(body, './/DatiGeneraliDocumento/Data')
        data['data_fattura'] = data_fattura
        
        # Righe Fattura
        dettagli = body.findall('.//p:DettaglioLinee', ns)
        if not dettagli:
            dettagli = body.findall('.//DettaglioLinee')
        
        for det in dettagli:
            riga = {
                'descrizione': get_text(det, './/p:Descrizione') or get_text(det, './/Descrizione') or 'N/D',
                'quantita': float(get_text(det, './/p:Quantita') or get_text(det, './/Quantita') or '1.0'),
                'prezzo_unitario': float(get_text(det, './/p:PrezzoUnitario') or get_text(det, './/PrezzoUnitario') or '0.0'),
                'totale_riga': float(get_text(det, './/p:PrezzoTotale') or get_text(det, './/PrezzoTotale') or '0.0'),
                'aliquota_iva': float(get_text(det, './/p:AliquotaIVA') or get_text(det, './/AliquotaIVA') or '22.0')
            }
            data['righe'].append(riga)
        
        # Totali
        riepilogo = body.find('.//p:DatiRiepilogo', ns)
        if riepilogo is None:
            riepilogo = body.find('.//DatiRiepilogo')
        
        if riepilogo is not None:
            imponibile = get_text(riepilogo, './/p:ImponibileImporto') or get_text(riepilogo, './/ImponibileImporto')
            imposta = get_text(riepilogo, './/p:Imposta') or get_text(riepilogo, './/Imposta')
            
            data['imponibile'] = float(imponibile) if imponibile else 0.0
            data['iva'] = float(imposta) if imposta else 0.0
            data['totale'] = data['imponibile'] + data['iva']
    
    return data
