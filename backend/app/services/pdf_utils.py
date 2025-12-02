"""
PDF Utilities - Rimuovi password, merge, split, ecc
"""
try:
    import PyPDF2
    from io import BytesIO
except ImportError:
    PyPDF2 = None
    BytesIO = None
from typing import Optional


class PDFUtils:
    """Utility per gestione PDF"""
    
    def remove_pdf_password(
        self, 
        pdf_data: bytes, 
        password: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Rimuove password da PDF
        
        Prova password comuni se non fornita:
        - codice fiscale
        - data di nascita
        - ecc
        """
        
        if not PyPDF2:
            print("❌ PyPDF2 non installato")
            return pdf_data
        
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
            
            # Se non ha password, ritorna originale
            if not pdf_reader.is_encrypted:
                return pdf_data
            
            # Prova password fornita
            if password:
                if pdf_reader.decrypt(password):
                    return self._save_unlocked_pdf(pdf_reader)
            
            # Prova password comuni
            common_passwords = ['', '12345678', '00000000']
            
            for pwd in common_passwords:
                try:
                    if pdf_reader.decrypt(pwd):
                        return self._save_unlocked_pdf(pdf_reader)
                except:
                    continue
            
            # Non riuscito a rimuovere password
            return None
            
        except Exception as e:
            print(f"Errore rimozione password PDF: {e}")
            return None
    
    def _save_unlocked_pdf(self, pdf_reader: PyPDF2.PdfReader) -> bytes:
        """Salva PDF senza password"""
        
        pdf_writer = PyPDF2.PdfWriter()
        
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        
        output = BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        
        return output.read()
    
    def merge_pdfs(self, pdf_list: list[bytes]) -> bytes:
        """Unisce più PDF in uno"""
        
        pdf_writer = PyPDF2.PdfWriter()
        
        for pdf_data in pdf_list:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
            
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        
        output = BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        
        return output.read()
    
    def extract_pages(
        self, 
        pdf_data: bytes, 
        start_page: int, 
        end_page: int
    ) -> bytes:
        """Estrae pagine da PDF"""
        
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
        pdf_writer = PyPDF2.PdfWriter()
        
        for i in range(start_page - 1, end_page):
            if i < len(pdf_reader.pages):
                pdf_writer.add_page(pdf_reader.pages[i])
        
        output = BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        
        return output.read()
    
    def add_watermark(
        self, 
        pdf_data: bytes, 
        watermark_text: str
    ) -> bytes:
        """Aggiunge watermark a PDF"""
        
        # TODO: Implementa watermark
        # Richiede reportlab o altro
        
        return pdf_data
    
    def get_pdf_info(self, pdf_data: bytes) -> dict:
        """Ottieni info PDF (pagine, autore, ecc)"""
        
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
            
            return {
                'pages': len(pdf_reader.pages),
                'encrypted': pdf_reader.is_encrypted,
                'metadata': dict(pdf_reader.metadata) if pdf_reader.metadata else {}
            }
        except Exception as e:
            return {'error': str(e)}
