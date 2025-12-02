import React, { useState, useEffect } from 'react'
import { Upload, Download, RefreshCw, Trash2 } from 'lucide-react'
import axios from 'axios'
import PaymentModal from '../components/PaymentModal'

const TABS = [
  { id: 'archiviate', label: 'Archiviate', state: null, pagata: true },
  { id: 'attive', label: 'Attive', state: 'active', pagata: false },
  { id: 'pending', label: 'In Attesa', state: 'pending' },
  { id: 'registered_bank', label: 'Banca', state: 'registered_bank' },
  { id: 'registered_cash', label: 'Cassa', state: 'registered_cash' },
  { id: 'paid_not_reconciled', label: 'Non Riconciliate', state: 'paid_not_reconciled' },
  { id: 'unmanaged', label: 'Non Gestite', state: 'unmanaged' },
]

export default function Archive() {
  const [activeTab, setActiveTab] = useState('attive')
  const [fatture, setFatture] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploadingFiles, setUploadingFiles] = useState(false)
  const [selectedFattura, setSelectedFattura] = useState(null)
  const [showPaymentModal, setShowPaymentModal] = useState(false)

  useEffect(() => {
    fetchFatture()
  }, [activeTab])

  const fetchFatture = async () => {
    setLoading(true)
    try {
      const tab = TABS.find(t => t.id === activeTab)
      
      let url = '/api/invoices/'
      let params = { id_utente: 1 }

      if (tab.state === 'pending' || tab.state === 'registered_bank' || 
          tab.state === 'registered_cash' || tab.state === 'paid_not_reconciled' || 
          tab.state === 'unmanaged') {
        url = `/api/invoices/by-state/${tab.state}`
      } else {
        if (tab.state) params.status = tab.state
        if (tab.pagata !== undefined) params.pagata = tab.pagata
      }

      const response = await axios.get(url, { params })
      setFatture(response.data.data || [])
    } catch (error) {
      console.error('Errore caricamento fatture:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUploadXML = async (event) => {
    const files = Array.from(event.target.files)
    if (files.length === 0) return

    setUploadingFiles(true)
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    formData.append('id_utente', '1')

    try {
      const response = await axios.post('/api/invoices/upload-bulk', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      alert(`Upload completato!\nCaricate: ${response.data.uploaded}\nErrori: ${response.data.errors}`)
      fetchFatture()
    } catch (error) {
      console.error('Errore upload:', error)
      alert('Errore durante l\'upload dei file')
    } finally {
      setUploadingFiles(false)
    }
  }

  const handleMarkPaid = async (fattura) => {
    setSelectedFattura(fattura)
    setShowPaymentModal(true)
  }

  const handlePaymentSuccess = () => {
    fetchFatture()
  }

  const handleDeleteFattura = async (id_fattura) => {
    if (!confirm('Eliminare questa fattura?')) return

    try {
      await axios.delete(`/api/invoices/${id_fattura}`, {
        params: { id_utente: 1 }
      })
      alert('Fattura eliminata!')
      fetchFatture()
    } catch (error) {
      console.error('Errore:', error)
      alert('Errore durante l\'eliminazione')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestione Fatture</h1>
          <p className="text-gray-600 mt-1">Fatture passive (acquisti fornitori)</p>
        </div>
        
        <div className="flex gap-3">
          <label className="btn-primary cursor-pointer">
            <Upload size={18} />
            <span>Upload XML</span>
            <input
              type="file"
              multiple
              accept=".xml"
              onChange={handleUploadXML}
              className="hidden"
              disabled={uploadingFiles}
            />
          </label>

          <button 
            onClick={fetchFatture}
            className="btn-secondary"
            disabled={loading}
          >
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
            <span>Aggiorna</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <div className="flex overflow-x-auto">
            {TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 text-sm font-medium whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : fatture.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              Nessuna fattura trovata in questa sezione
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Numero
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Data
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Fornitore
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Importo
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                    Metodo
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                    Azioni
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {fatture.map(fattura => (
                  <tr key={fattura.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {fattura.numero_fattura}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {new Date(fattura.data_fattura).toLocaleDateString('it-IT')}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {fattura.ragione_sociale_fornitore}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-gray-900">
                      €{parseFloat(fattura.totale).toLocaleString('it-IT', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      {fattura.metodo_pagamento ? (
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          fattura.metodo_pagamento === 'banca' ? 'bg-blue-100 text-blue-800' :
                          fattura.metodo_pagamento === 'cassa' ? 'bg-green-100 text-green-800' :
                          fattura.metodo_pagamento === 'assegno' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {fattura.metodo_pagamento}
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <div className="flex items-center justify-center gap-2">
                        {!fattura.pagata && (
                          <button
                            onClick={() => handleMarkPaid(fattura)}
                            className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium"
                          >
                            Paga
                          </button>
                        )}
                        <button
                          onClick={() => handleDeleteFattura(fattura.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Payment Modal */}
      {showPaymentModal && selectedFattura && (
        <PaymentModal
          fattura={selectedFattura}
          onClose={() => {
            setShowPaymentModal(false)
            setSelectedFattura(null)
          }}
          onSuccess={handlePaymentSuccess}
        />
      )}
    </div>
  )
}
