import React, { useState, useEffect } from 'react'
import { Plus, CheckSquare } from 'lucide-react'
import axios from 'axios'

export default function GestioneAssegni() {
  const [assegni, setAssegni] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    banca: '',
    numero_inizio: '',
    quantita: 10
  })

  useEffect(() => {
    fetchAssegni()
  }, [])

  const fetchAssegni = async () => {
    try {
      const response = await axios.get('/api/checks/', { params: { id_utente: 1 } })
      setAssegni(response.data.data || [])
    } catch (error) {
      console.error('Errore:', error)
    }
  }

  const handleCreaCarnet = async (e) => {
    e.preventDefault()
    const data = new FormData()
    data.append('id_utente', 1)
    data.append('banca', formData.banca)
    data.append('numero_inizio', formData.numero_inizio)
    data.append('quantita', formData.quantita)

    try {
      await axios.post('/api/checks/batch-create', data)
      alert('Carnet creato!')
      setShowModal(false)
      fetchAssegni()
    } catch (error) {
      alert('Errore: ' + (error.response?.data?.detail || 'Errore'))
    }
  }

  return (
    <div className="p-6">
      <div className="flex justify-between mb-6">
        <h1 className="text-2xl font-bold">Gestione Assegni</h1>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus size={20} />Crea Carnet
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="card">
          <p className="text-sm text-gray-600">Disponibili</p>
          <p className="text-2xl font-bold">{assegni.filter(a => a.stato === 'disponibile').length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Emessi</p>
          <p className="text-2xl font-bold">{assegni.filter(a => a.stato === 'emesso').length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Incassati</p>
          <p className="text-2xl font-bold">{assegni.filter(a => a.stato === 'incassato').length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Totali</p>
          <p className="text-2xl font-bold">{assegni.length}</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="table-header">Numero</th>
              <th className="table-header">Banca</th>
              <th className="table-header">Stato</th>
              <th className="table-header">Importo</th>
              <th className="table-header">Beneficiario</th>
            </tr>
          </thead>
          <tbody>
            {assegni.map((a) => (
              <tr key={a.id}>
                <td className="table-cell">{a.numero}</td>
                <td className="table-cell">{a.banca}</td>
                <td className="table-cell">
                  <span className={`px-2 py-1 rounded text-xs ${
                    a.stato === 'disponibile' ? 'bg-green-100 text-green-800' :
                    a.stato === 'emesso' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {a.stato}
                  </span>
                </td>
                <td className="table-cell">{a.importo ? `€${parseFloat(a.importo).toFixed(2)}` : '-'}</td>
                <td className="table-cell">{a.beneficiario || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Crea Carnet Assegni</h2>
            <form onSubmit={handleCreaCarnet} className="space-y-4">
              <div>
                <label className="label">Banca</label>
                <input type="text" className="input" required
                  value={formData.banca}
                  onChange={(e) => setFormData({...formData, banca: e.target.value})} />
              </div>
              <div>
                <label className="label">Numero Inizio</label>
                <input type="number" className="input" required
                  value={formData.numero_inizio}
                  onChange={(e) => setFormData({...formData, numero_inizio: e.target.value})} />
              </div>
              <div>
                <label className="label">Quantità</label>
                <input type="number" className="input" required min="1" max="100"
                  value={formData.quantita}
                  onChange={(e) => setFormData({...formData, quantita: e.target.value})} />
              </div>
              <div className="flex gap-2">
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">Annulla</button>
                <button type="submit" className="btn-primary">Crea</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
