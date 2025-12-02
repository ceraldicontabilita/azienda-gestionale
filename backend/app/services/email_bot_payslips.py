"""
Email Bot - Import automatico buste paga da email

Controlla inbox ceraldigroupsrl@gmail.com
Cerca email con allegati PDF buste paga
Importa automaticamente
"""
import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime, date
from typing import List, Dict
import re
from .hr_service import HRService


class EmailBotPayslips:
    """Bot per import automatico buste paga da email"""
    
    def __init__(self, db):
        self.db = db
        self.hr_service = HRService(db)
        
        # Configurazione email
        self.imap_server = 'imap.gmail.com'
        self.imap_port = 993
        self.email_address = os.getenv('EMAIL_ADDRESS', 'ceraldigroupsrl@gmail.com')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        # Filtri
        self.sender_filter = 'noreply@zucchetti.it'  # Email mittente buste paga
        self.subject_keywords = ['busta paga', 'cedolino', 'stipendio']
    
    async def check_and_import(self) -> Dict:
        """
        Controlla email e importa buste paga
        
        Returns:
            {
                'success': bool,
                'imported': int,
                'skipped': int,
                'errors': list
            }
        """
        
        results = {
            'success': True,
            'imported': 0,
            'skipped': 0,
            'errors': []
        }
        
        try:
            # Connetti IMAP
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.email_password)
            
            # Seleziona inbox
            mail.select('INBOX')
            
            # Cerca email non lette con allegati PDF
            search_criteria = f'(UNSEEN FROM "{self.sender_filter}")'
            status, messages = mail.search(None, search_criteria)
            
            if status != 'OK':
                results['success'] = False
                results['errors'].append('Errore ricerca email')
                return results
            
            email_ids = messages[0].split()
            
            print(f"📧 Trovate {len(email_ids)} email da processare")
            
            for email_id in email_ids:
                try:
                    result = await self._process_email(mail, email_id)
                    
                    if result['success']:
                        results['imported'] += 1
                    else:
                        results['skipped'] += 1
                        if result.get('error'):
                            results['errors'].append(result['error'])
                    
                except Exception as e:
                    results['errors'].append(f"Errore email {email_id}: {str(e)}")
                    results['skipped'] += 1
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            results['success'] = False
            results['errors'].append(f"Errore connessione email: {str(e)}")
        
        return results
    
    async def _process_email(self, mail, email_id: bytes) -> Dict:
        """Processa singola email"""
        
        status, msg_data = mail.fetch(email_id, '(RFC822)')
        
        if status != 'OK':
            return {'success': False, 'error': 'Errore fetch email'}
        
        # Parse email
        email_body = msg_data[0][1]
        email_message = email.message_from_bytes(email_body)
        
        # Info email
        from_email = email_message['From']
        subject = self._decode_subject(email_message['Subject'])
        date_email = email_message['Date']
        
        print(f"📬 Processando: {subject} da {from_email}")
        
        # Verifica che sia una busta paga
        if not self._is_payslip_email(subject):
            await self._log_import(
                from_email, subject, date_email,
                None, None, None,
                'skip', 'Non è una busta paga'
            )
            return {'success': False, 'error': 'Non è una busta paga'}
        
        # Cerca allegati PDF
        pdf_attachments = self._extract_pdf_attachments(email_message)
        
        if not pdf_attachments:
            await self._log_import(
                from_email, subject, date_email,
                None, None, None,
                'skip', 'Nessun PDF allegato'
            )
            return {'success': False, 'error': 'Nessun PDF allegato'}
        
        # Processa ogni PDF
        imported_count = 0
        
        for filename, pdf_data in pdf_attachments:
            try:
                # Import busta paga
                result = await self.hr_service.import_payslip_from_pdf(
                    pdf_data, 
                    filename,
                    data_disponibilita=date.today()
                )
                
                if result['success']:
                    await self._log_import(
                        from_email, subject, date_email,
                        filename, result.get('employee'), result.get('payslip_id'),
                        'successo', None
                    )
                    imported_count += 1
                    print(f"✅ Importata: {filename} - {result['employee']['nome']} {result['employee']['cognome']}")
                else:
                    await self._log_import(
                        from_email, subject, date_email,
                        filename, None, None,
                        'errore', result.get('error')
                    )
                
            except Exception as e:
                await self._log_import(
                    from_email, subject, date_email,
                    filename, None, None,
                    'errore', str(e)
                )
        
        # Marca email come letta
        if imported_count > 0:
            mail.store(email_id, '+FLAGS', '\\Seen')
        
        return {
            'success': imported_count > 0,
            'imported': imported_count
        }
    
    def _decode_subject(self, subject: str) -> str:
        """Decodifica subject email"""
        if not subject:
            return ''
        
        decoded = decode_header(subject)
        result = []
        
        for part, encoding in decoded:
            if isinstance(part, bytes):
                result.append(part.decode(encoding or 'utf-8'))
            else:
                result.append(part)
        
        return ''.join(result)
    
    def _is_payslip_email(self, subject: str) -> bool:
        """Verifica se email contiene busta paga"""
        subject_lower = subject.lower()
        
        return any(keyword in subject_lower for keyword in self.subject_keywords)
    
    def _extract_pdf_attachments(self, email_message) -> List[tuple]:
        """Estrae allegati PDF da email"""
        
        pdf_attachments = []
        
        for part in email_message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            
            if part.get('Content-Disposition') is None:
                continue
            
            filename = part.get_filename()
            
            if filename and filename.lower().endswith('.pdf'):
                pdf_data = part.get_payload(decode=True)
                pdf_attachments.append((filename, pdf_data))
        
        return pdf_attachments
    
    async def _log_import(
        self,
        from_email: str,
        subject: str,
        date_email: str,
        filename: str,
        employee: dict,
        payslip_id: int,
        stato: str,
        errore: str
    ):
        """Log import in database"""
        
        await self.db.execute("""
            INSERT INTO email_import_log (
                email_from, email_subject, email_date,
                tipo_documento, filename,
                employee_id, payslip_id,
                stato, errore
            ) VALUES (
                :from, :subject, :date,
                'busta_paga', :filename,
                :emp_id, :payslip_id,
                :stato, :errore
            )
        """, {
            'from': from_email,
            'subject': subject,
            'date': date_email,
            'filename': filename,
            'emp_id': employee['id'] if employee else None,
            'payslip_id': payslip_id,
            'stato': stato,
            'errore': errore
        })


# ============================================================================
# CRON JOB / SCHEDULER
# ============================================================================

async def run_email_import_job(db):
    """
    Job schedulato per import automatico
    
    Esegui ogni ora o ogni giorno
    """
    
    bot = EmailBotPayslips(db)
    
    print(f"🤖 [Email Bot] Inizio controllo email - {datetime.now()}")
    
    results = await bot.check_and_import()
    
    print(f"📊 [Email Bot] Risultati:")
    print(f"  ✅ Importate: {results['imported']}")
    print(f"  ⏭️  Skippate: {results['skipped']}")
    print(f"  ❌ Errori: {len(results['errors'])}")
    
    if results['errors']:
        for error in results['errors']:
            print(f"  ⚠️  {error}")
    
    return results


# ============================================================================
# TEST
# ============================================================================

if __name__ == '__main__':
    import asyncio
    from app.database import get_db
    
    async def test():
        async with get_db() as db:
            await run_email_import_job(db)
    
    asyncio.run(test())
