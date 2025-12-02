"""
Servizio Relazioni - Delete Cascata e Update Propagazione
Gestisce tutte le operazioni che impattano relazioni tra entità
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from app.database import get_table

logger = logging.getLogger(__name__)

class RelationshipService:
    """Servizio per gestione relazioni tra entità"""
    
    # ==================== DELETE OPERATIONS ====================
    
    @staticmethod
    async def delete_fattura_with_cascade(id_utente: int, id_fattura: int) -> Dict:
        """
        Elimina fattura con cascata completa
        
        Elimina/Scollega:
        1. Righe fattura
        2. Movimenti Prima Nota Cassa
        3. Movimenti Prima Nota Banca
        4. Collegamenti Bonifici
        5. Collegamenti Assegni
        """
        try:
            fatture_table = get_table('fatture')
            righe_table = get_table('righe_fattura')
            cassa_table = get_table('movimenti_cassa')
            banca_table = get_table('prima_nota_banca')
            bonifici_table = get_table('bonifici')
            assegni_table = get_table('assegni')
            
            # Verifica fattura esiste
            fattura = fatture_table.select('*')\
                .eq('id', id_fattura)\
                .eq('id_utente', id_utente)\
                .execute()
            
            if not fattura.data:
                raise ValueError("Fattura non trovata")
            
            deleted_items = {
                'righe_fattura': 0,
                'movimenti_cassa': 0,
                'movimenti_banca': 0,
                'bonifici_scollegati': 0,
                'assegni_scollegati': 0
            }
            
            # 1. Elimina righe fattura
            righe = righe_table.select('*').eq('id_fattura', id_fattura).execute()
            if righe.data:
                righe_table.delete().eq('id_fattura', id_fattura).execute()
                deleted_items['righe_fattura'] = len(righe.data)
            
            # 2. Elimina movimenti cassa collegati
            mov_cassa = cassa_table.select('*')\
                .eq('id_utente', id_utente)\
                .eq('id_fattura', id_fattura)\
                .execute()
            if mov_cassa.data:
                cassa_table.delete()\
                    .eq('id_utente', id_utente)\
                    .eq('id_fattura', id_fattura)\
                    .execute()
                deleted_items['movimenti_cassa'] = len(mov_cassa.data)
            
            # 3. Elimina movimenti banca collegati
            mov_banca = banca_table.select('*')\
                .eq('id_utente', id_utente)\
                .eq('id_fattura', id_fattura)\
                .execute()
            if mov_banca.data:
                banca_table.delete()\
                    .eq('id_utente', id_utente)\
                    .eq('id_fattura', id_fattura)\
                    .execute()
                deleted_items['movimenti_banca'] = len(mov_banca.data)
            
            # 4. Scollega bonifici (non elimina il bonifico)
            bonifici = bonifici_table.select('*')\
                .eq('id_utente', id_utente)\
                .eq('id_fattura', id_fattura)\
                .execute()
            if bonifici.data:
                bonifici_table.update({
                    'id_fattura': None,
                    'collegato': False
                })\
                .eq('id_utente', id_utente)\
                .eq('id_fattura', id_fattura)\
                .execute()
                deleted_items['bonifici_scollegati'] = len(bonifici.data)
            
            # 5. Scollega assegni (riporta a disponibile se non incassato)
            assegni = assegni_table.select('*')\
                .eq('id_utente', id_utente)\
                .eq('id_fattura', id_fattura)\
                .execute()
            if assegni.data:
                for assegno in assegni.data:
                    new_stato = 'disponibile' if assegno['stato'] == 'emesso' else assegno['stato']
                    assegni_table.update({
                        'id_fattura': None,
                        'stato': new_stato,
                        'importo': None,
                        'beneficiario': None,
                        'data_emissione': None
                    }).eq('id', assegno['id']).execute()
                deleted_items['assegni_scollegati'] = len(assegni.data)
            
            # 6. Elimina fattura
            fatture_table.delete()\
                .eq('id', id_fattura)\
                .eq('id_utente', id_utente)\
                .execute()
            
            logger.info(f"Fattura {id_fattura} eliminata con cascata: {deleted_items}")
            
            return {
                "success": True,
                "message": "Fattura eliminata con tutti i collegamenti",
                "deleted": deleted_items
            }
            
        except Exception as e:
            logger.error(f"Errore delete_fattura_with_cascade: {str(e)}")
            raise
    
    @staticmethod
    async def delete_fornitore_safe(id_utente: int, partita_iva: str, force: bool = False) -> Dict:
        """
        Elimina fornitore con controlli
        
        Se ha fatture:
        - force=False → BLOCCA (default)
        - force=True → SOFT DELETE (disattiva)
        """
        try:
            fornitori_table = get_table('fornitori')
            fatture_table = get_table('fatture')
            
            # Verifica fornitore esiste
            fornitore = fornitori_table.select('*')\
                .eq('id_utente', id_utente)\
                .eq('partita_iva', partita_iva)\
                .execute()
            
            if not fornitore.data:
                raise ValueError("Fornitore non trovato")
            
            # Controlla fatture collegate
            fatture = fatture_table.select('id')\
                .eq('id_utente', id_utente)\
                .eq('partita_iva_fornitore', partita_iva)\
                .execute()
            
            if fatture.data and len(fatture.data) > 0:
                if not force:
                    raise ValueError(
                        f"Impossibile eliminare: fornitore ha {len(fatture.data)} fatture collegate. "
                        f"Usa force=true per disattivarlo."
                    )
                else:
                    # SOFT DELETE
                    fornitori_table.update({
                        'attivo': False,
                        'updated_at': datetime.now().isoformat()
                    })\
                    .eq('id_utente', id_utente)\
                    .eq('partita_iva', partita_iva)\
                    .execute()
                    
                    return {
                        "success": True,
                        "message": f"Fornitore disattivato (ha {len(fatture.data)} fatture)",
                        "operation": "soft_delete"
                    }
            else:
                # HARD DELETE (nessuna fattura collegata)
                fornitori_table.delete()\
                    .eq('id_utente', id_utente)\
                    .eq('partita_iva', partita_iva)\
                    .execute()
                
                return {
                    "success": True,
                    "message": "Fornitore eliminato definitivamente",
                    "operation": "hard_delete"
                }
                
        except Exception as e:
            logger.error(f"Errore delete_fornitore_safe: {str(e)}")
            raise
    
    @staticmethod
    async def delete_dipendente_safe(id_utente: int, id_dipendente: int, force: bool = False) -> Dict:
        """
        Elimina dipendente con controlli
        
        Se ha paghe o turni:
        - force=False → BLOCCA
        - force=True → SOFT DELETE
        """
        try:
            dipendenti_table = get_table('dipendenti')
            paghe_table = get_table('paghe_dipendenti')
            turni_table = get_table('turni')
            
            # Verifica dipendente esiste
            dipendente = dipendenti_table.select('*')\
                .eq('id', id_dipendente)\
                .eq('id_utente', id_utente)\
                .execute()
            
            if not dipendente.data:
                raise ValueError("Dipendente non trovato")
            
            # Controlla paghe
            paghe = paghe_table.select('id')\
                .eq('id_utente', id_utente)\
                .eq('id_dipendente', id_dipendente)\
                .execute()
            
            # Controlla turni
            turni = turni_table.select('id')\
                .eq('id_utente', id_utente)\
                .eq('id_dipendente', id_dipendente)\
                .execute()
            
            total_records = len(paghe.data or []) + len(turni.data or [])
            
            if total_records > 0:
                if not force:
                    raise ValueError(
                        f"Impossibile eliminare: dipendente ha {len(paghe.data or [])} paghe "
                        f"e {len(turni.data or [])} turni. Usa force=true per disattivarlo."
                    )
                else:
                    # SOFT DELETE
                    dipendenti_table.update({
                        'attivo': False,
                        'updated_at': datetime.now().isoformat()
                    })\
                    .eq('id', id_dipendente)\
                    .eq('id_utente', id_utente)\
                    .execute()
                    
                    return {
                        "success": True,
                        "message": f"Dipendente disattivato (ha {total_records} record collegati)",
                        "operation": "soft_delete"
                    }
            else:
                # HARD DELETE
                dipendenti_table.delete()\
                    .eq('id', id_dipendente)\
                    .eq('id_utente', id_utente)\
                    .execute()
                
                return {
                    "success": True,
                    "message": "Dipendente eliminato definitivamente",
                    "operation": "hard_delete"
                }
                
        except Exception as e:
            logger.error(f"Errore delete_dipendente_safe: {str(e)}")
            raise
    
    @staticmethod
    async def delete_assegno_safe(id_utente: int, id_assegno: int) -> Dict:
        """
        Elimina assegno con controlli
        
        Può eliminare solo se stato = 'disponibile'
        """
        try:
            assegni_table = get_table('assegni')
            
            assegno = assegni_table.select('*')\
                .eq('id', id_assegno)\
                .eq('id_utente', id_utente)\
                .execute()
            
            if not assegno.data:
                raise ValueError("Assegno non trovato")
            
            stato = assegno.data[0]['stato']
            
            if stato != 'disponibile':
                raise ValueError(
                    f"Impossibile eliminare: assegno è '{stato}'. "
                    f"Solo assegni 'disponibili' possono essere eliminati."
                )
            
            assegni_table.delete()\
                .eq('id', id_assegno)\
                .eq('id_utente', id_utente)\
                .execute()
            
            return {
                "success": True,
                "message": "Assegno eliminato"
            }
            
        except Exception as e:
            logger.error(f"Errore delete_assegno_safe: {str(e)}")
            raise
    
    # ==================== UPDATE PROPAGATION ====================
    
    @staticmethod
    async def update_fornitore_propagate(
        id_utente: int,
        partita_iva: str,
        update_data: Dict
    ) -> Dict:
        """
        Aggiorna fornitore e propaga modifiche alle fatture
        
        Campi propagati:
        - ragione_sociale → fatture.ragione_sociale_fornitore
        """
        try:
            fornitori_table = get_table('fornitori')
            fatture_table = get_table('fatture')
            
            # Aggiorna fornitore
            fornitori_table.update(update_data)\
                .eq('id_utente', id_utente)\
                .eq('partita_iva', partita_iva)\
                .execute()
            
            # Propaga ragione sociale a fatture
            if 'ragione_sociale' in update_data:
                fatture_table.update({
                    'ragione_sociale_fornitore': update_data['ragione_sociale']
                })\
                .eq('id_utente', id_utente)\
                .eq('partita_iva_fornitore', partita_iva)\
                .execute()
                
                # Conta fatture aggiornate
                fatture = fatture_table.select('id')\
                    .eq('id_utente', id_utente)\
                    .eq('partita_iva_fornitore', partita_iva)\
                    .execute()
                
                return {
                    "success": True,
                    "message": "Fornitore aggiornato",
                    "propagated": {
                        "fatture_updated": len(fatture.data) if fatture.data else 0
                    }
                }
            
            return {
                "success": True,
                "message": "Fornitore aggiornato (nessuna propagazione necessaria)"
            }
            
        except Exception as e:
            logger.error(f"Errore update_fornitore_propagate: {str(e)}")
            raise
    
    @staticmethod
    async def update_dipendente_propagate(
        id_utente: int,
        id_dipendente: int,
        update_data: Dict
    ) -> Dict:
        """
        Aggiorna dipendente e propaga modifiche
        
        Campi propagati:
        - nome/cognome → Paghe (via JOIN, nessuna modifica necessaria)
        - Note: le paghe usano id_dipendente, quindi nessuna propagazione diretta
        """
        try:
            dipendenti_table = get_table('dipendenti')
            
            # Aggiorna dipendente
            dipendenti_table.update(update_data)\
                .eq('id', id_dipendente)\
                .eq('id_utente', id_utente)\
                .execute()
            
            return {
                "success": True,
                "message": "Dipendente aggiornato (le paghe usano id_dipendente, nessuna propagazione necessaria)"
            }
            
        except Exception as e:
            logger.error(f"Errore update_dipendente_propagate: {str(e)}")
            raise
    
    # ==================== INTEGRITY CHECKS ====================
    
    @staticmethod
    async def check_can_delete_bonifico(id_utente: int, id_bonifico: int) -> Tuple[bool, str]:
        """Verifica se bonifico può essere eliminato"""
        try:
            bonifici_table = get_table('bonifici')
            
            bonifico = bonifici_table.select('*')\
                .eq('id', id_bonifico)\
                .eq('id_utente', id_utente)\
                .execute()
            
            if not bonifico.data:
                return False, "Bonifico non trovato"
            
            if bonifico.data[0].get('collegato'):
                return False, "Bonifico collegato a fattura. Scollegalo prima di eliminare."
            
            return True, "OK"
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    async def check_can_modify_fattura_pagata(id_utente: int, id_fattura: int) -> Tuple[bool, str]:
        """Verifica se fattura pagata può essere modificata"""
        try:
            fatture_table = get_table('fatture')
            
            fattura = fatture_table.select('*')\
                .eq('id', id_fattura)\
                .eq('id_utente', id_utente)\
                .execute()
            
            if not fattura.data:
                return False, "Fattura non trovata"
            
            if fattura.data[0].get('pagata'):
                return False, "Fattura già pagata. Annulla il pagamento prima di modificare."
            
            return True, "OK"
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    async def get_fornitore_dependencies(id_utente: int, partita_iva: str) -> Dict:
        """Ottieni tutte le dipendenze di un fornitore"""
        try:
            fatture_table = get_table('fatture')
            
            fatture = fatture_table.select('*')\
                .eq('id_utente', id_utente)\
                .eq('partita_iva_fornitore', partita_iva)\
                .execute()
            
            if not fatture.data:
                return {
                    "can_delete": True,
                    "dependencies": {},
                    "total": 0
                }
            
            fatture_pagate = len([f for f in fatture.data if f.get('pagata')])
            fatture_non_pagate = len([f for f in fatture.data if not f.get('pagata')])
            
            return {
                "can_delete": False,
                "dependencies": {
                    "fatture_totali": len(fatture.data),
                    "fatture_pagate": fatture_pagate,
                    "fatture_non_pagate": fatture_non_pagate
                },
                "total": len(fatture.data),
                "message": f"Fornitore ha {len(fatture.data)} fatture. Usa soft delete (disattivazione)."
            }
            
        except Exception as e:
            logger.error(f"Errore get_fornitore_dependencies: {str(e)}")
            raise
