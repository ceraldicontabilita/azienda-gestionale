import React, { useState, useEffect } from 'react'
import { X, CreditCard, Wallet, CheckSquare, Building2 } from 'lucide-react'
import axios from 'axios'

export default function PaymentModal({ fattura, onClose, onSuccess }) {
  const [metodo, setMetodo] = useState('')
  const [assegniDisponibili, setAssegniDisponibili] = useState([])
  const [assegnoSelezionato, setAssegnoSelezionato] = useState(null)
  const [bonificiDisponibili, setBonificiDisponibili] = useState([])
  const [bonificoSelezionato, setBonificoSelezionato] = useState(null)
  const [dataPagamento, setDataPagamento] = useState(new Date().toISOString().split('T')[0])
  const [note, setNote] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (metodo === 'assegno') {
      fetchAssegni()
    } else if (metodo === 'banca_bonifico') {
      fetchBonifici()
    }
  }, [metodo])

  const fetchAssegni = async () => {
    try {
      const response = await axios.get('/api/invoices/payment-options/assegni', {
        params: { id_utente: 1 }
      })
      setAssegniDisponibili(response.data.data || [])
    } catch (error) {
      console.error('Errore caricamento assegni:', error)
    }
  }

  const fetchBonifici = async () => {
    try {
      const response = await axios.get('/api/invoices/payment-options/bonifici', {
        params: { id_utente: 1 }
      })
      setBonificiDisponibili(response.data.data || [])
    } catch (error) {
      console.error('Errore caricamento bonifici:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!metodo) {
      alert('Seleziona un metodo di pagamento')
      return
    }

    if (metodo === 'assegno' && !assegnoSelezionato) {
      alert('Seleziona un assegno')
      return
    }

    if (metodo === 'banca_bonifico' && !bonificoSelezionato) {
      alert('Seleziona un bonifico o procedi senza collegamento')
    }

    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('metodo', metodo)
      formData.append('data_pagamento', dataPagamento)
      if (note) formData.append('note', note)
      if (assegnoSelezionato) formData.append('id_assegno', assegnoSelezionato)
      if (bonificoSelezionato) formData.append('id_bonifico', bonificoSelezionato)

      await axios.post(
        `/api/invoices/${fattura.id}/mark-paid`,
        formData,
        { params: { id_utente: 1 } }
      )

      alert('Pagamento registrato con successo!')
      onSuccess()
      onClose()
    } catch (error) {
      console.error('Errore registrazione pagamento:', error)
      alert('Errore durante la registrazione del pagamento')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Registra Pagamento</h2>
            <p className="text-sm text-gray-600 mt-1">
              Fattura {fattura.numero_fattura} - €{parseFloat(fattura.totale).toFixed(2)}
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={24} />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Metodo Pagamento */}
          <div>
            <label className="label">Metodo di Pagamento</label>
            <div className="grid grid-cols-2 gap-3 mt-2">
              <button
                type="button"
                onClick={() => setMetodo('cassa')}
                className={`p-4 border-2 rounded-lg flex items-center gap-3 transition-colors ${
                  metodo === 'cassa'
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Wallet className={metodo === 'cassa' ? 'text-blue-600' : 'text-gray-400'} />
                <div className="text-left">
                  <div className="font-medium">Cassa</div>
                  <div className="text-xs text-gray-500">Contanti</div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setMetodo('banca_bonifico')}
                className={`p-4 border-2 rounded-lg flex items-center gap-3 transition-colors ${
                  metodo === 'banca_bonifico'
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Building2 className={metodo === 'banca_bonifico' ? 'text-blue-600' : 'text-gray-400'} />
                <div className="text-left">
                  <div className="font-medium">Bonifico</div>
                  <div className="text-xs text-gray-500">Banca</div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setMetodo('banca_rid')}
                className={`p-4 border-2 rounded-lg flex items-center gap-3 transition-colors ${
                  metodo === 'banca_rid'
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <CreditCard className={metodo === 'banca_rid' ? 'text-blue-600' : 'text-gray-400'} />
                <div className="text-left">
                  <div className="font-medium">RID Bancario</div>
                  <div className="text-xs text-gray-500">Addebito diretto</div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setMetodo('assegno')}
                className={`p-4 border-2 rounded-lg flex items-center gap-3 transition-colors ${
                  metodo === 'assegno'
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <CheckSquare className={metodo === 'assegno' ? 'text-blue-600' : 'text-gray-400'} />
                <div className="text-left">
                  <div className="font-medium">Assegno</div>
                  <div className="text-xs text-gray-500">Da carnet</div>
                </div>
              </button>
            </div>
          </div>

          {/* Selezione Assegno */}
          {metodo === 'assegno' && (
            <div>
              <label className="label">Seleziona Assegno</label>
              {assegniDisponibili.length === 0 ? (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
                  Nessun assegno disponibile. Crea assegni in Gestione Assegni.
                </div>
              ) : (
                <select
                  value={assegnoSelezionato || ''}
                  onChange={(e) => setAssegnoSelezionato(e.target.value)}
                  className="input"
                  required
                >
                  <option value="">-- Seleziona assegno --</option>
                  {assegniDisponibili.map(assegno => (
                    <option key={assegno.id} value={assegno.id}>
                      Assegno n.{assegno.numero} - {assegno.banca}
                    </option>
                  ))}
                </select>
              )}
            </div>
          )}

          {/* Selezione Bonifico */}
          {metodo === 'banca_bonifico' && (
            <div>
              <label className="label">Collega Bonifico (Opzionale)</label>
              {bonificiDisponibili.length === 0 ? (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
                  Nessun bonifico da collegare. Puoi procedere senza collegamento.
                </div>
              ) : (
                <select
                  value={bonificoSelezionato || ''}
                  onChange={(e) => setBonificoSelezionato(e.target.value)}
                  className="input"
                >
                  <option value="">-- Procedi senza collegamento --</option>
                  {bonificiDisponibili.map(bonifico => (
                    <option key={bonifico.id} value={bonifico.id}>
                      {new Date(bonifico.data_bonifico).toLocaleDateString('it-IT')} - 
                      €{parseFloat(bonifico.importo).toFixed(2)} - 
                      {bonifico.beneficiario}
                    </option>
                  ))}
                </select>
              )}
            </div>
          )}

          {/* Data Pagamento */}
          <div>
            <label className="label">Data Pagamento</label>
            <input
              type="date"
              value={dataPagamento}
              onChange={(e) => setDataPagamento(e.target.value)}
              className="input"
              required
            />
          </div>

          {/* Note */}
          <div>
            <label className="label">Note (Opzionale)</label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="input"
              rows="3"
              placeholder="Note aggiuntive..."
            />
          </div>

          {/* Riepilogo */}
          {metodo && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-2">Riepilogo Operazione</h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Importo:</span>
                  <span className="font-medium">€{parseFloat(fattura.totale).toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Metodo:</span>
                  <span className="font-medium capitalize">{metodo.replace('_', ' ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Registrato in:</span>
                  <span className="font-medium">
                    {metodo === 'cassa' ? 'Prima Nota Cassa' : 'Prima Nota Banca'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 justify-end pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
              disabled={loading}
            >
              Annulla
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading || !metodo}
            >
              {loading ? 'Registrazione...' : 'Registra Pagamento'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
