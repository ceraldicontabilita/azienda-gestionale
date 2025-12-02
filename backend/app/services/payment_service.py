"""
Servizio Gestione Pagamenti Relazionali
Collega fatture a: Prima Nota Cassa, Prima Nota Banca, Bonifici, Assegni
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, List
import logging

from app.database import get_table

logger = logging.getLogger(__name__)

class PaymentService:
    """Servizio per gestione pagamenti e collegamenti relazionali"""
    
    @staticmethod
    async def registra_pagamento_fattura(
        id_utente: int,
        id_fattura: int,
        metodo: str,
        importo: Decimal,
        data_pagamento: datetime,
        id_assegno: Optional[int] = None,
        id_bonifico: Optional[int] = None,
        note: Optional[str] = None
    ) -> Dict:
        """
        Registra pagamento fattura e crea movimento contabile
        
        Args:
            metodo: 'cassa', 'banca_bonifico', 'banca_rid', 'assegno', 'misto'
            id_assegno: Se metodo='assegno', ID assegno da collegare
            id_bonifico: Se metodo='banca_bonifico', ID bonifico da collegare
        
        Returns:
            Dict con risultati operazione
        """
        try:
            fatture_table = get_table('fatture')
            
            # Verifica fattura esiste
            fattura = fatture_table.select('*')\
                .eq('id', id_fattura)\
                .eq('id_utente', id_utente)\
                .execute()
            
            if not fattura.data:
                raise ValueError("Fattura non trovata")
            
            fattura_data = fattura.data[0]
            
            # Aggiorna fattura
            fatture_table.update({
                'pagata': True,
                'metodo_pagamento': metodo,
                'data_pagamento': data_pagamento.isoformat(),
                'updated_at': datetime.now().isoformat()
            }).eq('id', id_fattura).execute()
            
            # Crea movimento in base al metodo
            if metodo == 'cassa':
                await PaymentService._registra_prima_nota_cassa(
                    id_utente, id_fattura, fattura_data, importo, data_pagamento, note
                )
            
            elif metodo in ['banca_bonifico', 'banca_rid']:
                await PaymentService._registra_prima_nota_banca(
                    id_utente, id_fattura, fattura_data, importo, data_pagamento, 
                    metodo, id_bonifico, note
                )
            
            elif metodo == 'assegno':
                if not id_assegno:
                    raise ValueError("ID assegno richiesto per pagamento con assegno")
                await PaymentService._collega_assegno(
                    id_utente, id_fattura, id_assegno, importo, data_pagamento, note
                )
            
            elif metodo == 'misto':
                # Per misto, gestione separata con split importi
                pass
            
            return {
                "success": True,
                "message": f"Pagamento registrato: {metodo}",
                "id_fattura": id_fattura,
                "metodo": metodo
            }
            
        except Exception as e:
            logger.error(f"Errore registra_pagamento_fattura: {str(e)}")
            raise
    
    @staticmethod
    async def _registra_prima_nota_cassa(
        id_utente: int,
        id_fattura: int,
        fattura_data: Dict,
        importo: Decimal,
        data_pagamento: datetime,
        note: Optional[str]
    ):
        """Registra movimento in Prima Nota Cassa"""
        cassa_table = get_table('movimenti_cassa')
        
        cassa_table.insert({
            'id_utente': id_utente,
            'data_operazione': data_pagamento.date().isoformat(),
            'tipo': 'pagamento_fattura',
            'importo': -float(importo),  # Negativo perché è uscita
            'descrizione': f"Pagamento fattura {fattura_data['numero_fattura']} - {fattura_data['ragione_sociale_fornitore']}",
            'note': note,
            'id_fattura': id_fattura,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        logger.info(f"Registrato in Prima Nota Cassa: Fattura {id_fattura}")
    
    @staticmethod
    async def _registra_prima_nota_banca(
        id_utente: int,
        id_fattura: int,
        fattura_data: Dict,
        importo: Decimal,
        data_pagamento: datetime,
        tipo_banca: str,
        id_bonifico: Optional[int],
        note: Optional[str]
    ):
        """Registra movimento in Prima Nota Banca"""
        banca_table = get_table('prima_nota_banca')
        
        movimento_data = {
            'id_utente': id_utente,
            'data_operazione': data_pagamento.date().isoformat(),
            'importo': -float(importo),  # Negativo perché è uscita
            'tipo': 'pagamento_fattura_' + tipo_banca,
            'descrizione': f"Pagamento fattura {fattura_data['numero_fattura']} - {fattura_data['ragione_sociale_fornitore']}",
            'id_fattura': id_fattura,
            'riconciliato': False,
            'created_at': datetime.now().isoformat()
        }
        
        banca_table.insert(movimento_data).execute()
        
        # Se c'è bonifico, collega
        if id_bonifico and tipo_banca == 'bonifico':
            bonifici_table = get_table('bonifici')
            bonifici_table.update({
                'id_fattura': id_fattura,
                'collegato': True
            }).eq('id', id_bonifico).execute()
        
        logger.info(f"Registrato in Prima Nota Banca ({tipo_banca}): Fattura {id_fattura}")
    
    @staticmethod
    async def _collega_assegno(
        id_utente: int,
        id_fattura: int,
        id_assegno: int,
        importo: Decimal,
        data_pagamento: datetime,
        note: Optional[str]
    ):
        """Collega assegno a fattura"""
        assegni_table = get_table('assegni')
        
        # Verifica assegno disponibile
        assegno = assegni_table.select('*')\
            .eq('id', id_assegno)\
            .eq('id_utente', id_utente)\
            .eq('stato', 'disponibile')\
            .execute()
        
        if not assegno.data:
            raise ValueError("Assegno non disponibile")
        
        # Aggiorna assegno come emesso
        assegni_table.update({
            'stato': 'emesso',
            'data_emissione': data_pagamento.date().isoformat(),
            'id_fattura': id_fattura,
            'importo': float(importo),
            'note': note or f"Pagamento fattura {id_fattura}"
        }).eq('id', id_assegno).execute()
        
        # Registra anche in Prima Nota Banca
        banca_table = get_table('prima_nota_banca')
        banca_table.insert({
            'id_utente': id_utente,
            'data_operazione': data_pagamento.date().isoformat(),
            'importo': -float(importo),
            'tipo': 'pagamento_fattura_assegno',
            'descrizione': f"Pagamento con assegno n.{assegno.data[0]['numero']}",
            'id_fattura': id_fattura,
            'id_assegno': id_assegno,
            'riconciliato': False,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        logger.info(f"Assegno {id_assegno} collegato a Fattura {id_fattura}")
    
    @staticmethod
    async def get_assegni_disponibili(id_utente: int) -> List[Dict]:
        """Ottieni lista assegni disponibili per pagamento"""
        assegni_table = get_table('assegni')
        
        result = assegni_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('stato', 'disponibile')\
            .order('numero')\
            .execute()
        
        return result.data if result.data else []
    
    @staticmethod
    async def get_bonifici_non_collegati(id_utente: int) -> List[Dict]:
        """Ottieni lista bonifici non ancora collegati a fatture"""
        bonifici_table = get_table('bonifici')
        
        result = bonifici_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('collegato', False)\
            .order('data_bonifico', desc=True)\
            .execute()
        
        return result.data if result.data else []
    
    @staticmethod
    async def suggerisci_collegamento_bonifico(
        id_utente: int,
        id_bonifico: int
    ) -> Optional[Dict]:
        """
        Suggerisce fattura da collegare a bonifico basato su:
        - Importo simile
        - Beneficiario corrispondente
        - Data compatibile
        """
        bonifici_table = get_table('bonifici')
        fatture_table = get_table('fatture')
        
        # Ottieni bonifico
        bonifico = bonifici_table.select('*')\
            .eq('id', id_bonifico)\
            .eq('id_utente', id_utente)\
            .execute()
        
        if not bonifico.data:
            return None
        
        bonifico_data = bonifico.data[0]
        importo = float(bonifico_data['importo'])
        beneficiario = bonifico_data['beneficiario'].lower()
        
        # Cerca fatture non pagate con importo simile
        fatture = fatture_table.select('*')\
            .eq('id_utente', id_utente)\
            .eq('pagata', False)\
            .execute()
        
        if not fatture.data:
            return None
        
        # Trova miglior match
        best_match = None
        best_score = 0
        
        for fattura in fatture.data:
            score = 0
            
            # Match importo (±2%)
            fattura_importo = float(fattura['totale'])
            diff_percentuale = abs(fattura_importo - importo) / importo * 100
            if diff_percentuale <= 2:
                score += 50
            
            # Match beneficiario
            fornitore = fattura['ragione_sociale_fornitore'].lower()
            if beneficiario in fornitore or fornitore in beneficiario:
                score += 50
            
            if score > best_score:
                best_score = score
                best_match = fattura
        
        return best_match if best_score >= 60 else None
