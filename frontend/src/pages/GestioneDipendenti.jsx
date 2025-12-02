import React, { useState, useEffect } from 'react'
import { Plus, Upload, Users } from 'lucide-react'
import axios from 'axios'

export default function GestioneDipendenti() {
  const [dipendenti, setDipendenti] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    fetchDipendenti()
  }, [])

  const fetchDipendenti = async () => {
    try {
      const response = await axios.get('/api/dipendenti/', { params: { id_utente: 1 } })
      setDipendenti(response.data.data || [])
    } catch (error) {
      console.error('Errore:', error)
    }
  }

  const handleUploadBustaPaga = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('id_utente', 1)

    try {
      await axios.post('/api/dipendenti/upload-busta-paga', formData)
      alert('Busta paga caricata!')
      fetchDipendenti()
    } catch (error) {
      alert('Errore: ' + (error.response?.data?.detail || 'Errore'))
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="p-6">
      <div className="flex justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Gestione Dipendenti</h1>
          <p className="text-gray-600">{dipendenti.length} dipendenti</p>
        </div>
        <div className="flex gap-2">
          <label className="btn-secondary flex items-center gap-2 cursor-pointer">
            <Upload size={20} />
            Upload Busta Paga
            <input type="file" accept=".pdf" onChange={handleUploadBustaPaga} className="hidden" />
          </label>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="table-header">Nome</th>
              <th className="table-header">Cognome</th>
              <th className="table-header">CF</th>
              <th className="table-header">Mansione</th>
              <th className="table-header">Stato</th>
            </tr>
          </thead>
          <tbody>
            {dipendenti.map((d) => (
              <tr key={d.id}>
                <td className="table-cell">{d.nome}</td>
                <td className="table-cell">{d.cognome}</td>
                <td className="table-cell">{d.codice_fiscale}</td>
                <td className="table-cell">{d.mansione || '-'}</td>
                <td className="table-cell">
                  <span className={`px-2 py-1 rounded text-xs ${
                    d.attivo ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {d.attivo ? 'Attivo' : 'Inattivo'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
