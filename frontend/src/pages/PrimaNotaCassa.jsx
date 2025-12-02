import React, { useState, useEffect } from 'react'
import { DollarSign, Upload } from 'lucide-react'
import axios from 'axios'

export default function PrimaNotaCassa() {
  const [movimenti, setMovimenti] = useState([])
  const [saldo, setSaldo] = useState(0)
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    corrispettivi: 0,
    pos: 0,
    versamento: 0,
    data: new Date().toISOString().split('T')[0]
  })

  useEffect(() => {
    fetchMovimenti()
    fetchSaldo()
  }, [])

  const fetchMovimenti = async () => {
    try {
      const response = await axios.get('/api/cash-register/', { params: { id_utente: 1 } })
      setMovimenti(response.data.data || [])
    } catch (error) {
      console.error('Errore:', error)
    }
  }

  const fetchSaldo = async () => {
    try {
      const response = await axios.get('/api/cash-register/saldo', { params: { id_utente: 1 } })
      setSaldo(response.data.saldo || 0)
    } catch (error) {
      console.error('Errore:', error)
    }
  }

  const handleChiusura = async (e) => {
    e.preventDefault()
    const data = new FormData()
    data.append('id_utente', 1)
    data.append('data', formData.data)
    data.append('corrispettivi', formData.corrispettivi)
    data.append('pos', formData.pos)
    data.append('versamento', formData.versamento)

    try {
      await axios.post('/api/cash-register/chiusura-giornaliera', data)
      alert('Chiusura registrata!')
      setShowModal(false)
      fetchMovimenti()
      fetchSaldo()
    } catch (error) {
      alert('Errore: ' + (error.response?.data?.detail || 'Errore'))
    }
  }

  return (
    <div className="p-6">
      <div className="flex justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Prima Nota Cassa</h1>
          <p className="text-gray-600">Saldo: €{saldo.toFixed(2)}</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          Chiusura Giornaliera
        </button>
      </div>

      <div className="bg-white rounded-lg shadow">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="table-header">Data</th>
              <th className="table-header">Tipo</th>
              <th className="table-header">Importo</th>
              <th className="table-header">Descrizione</th>
            </tr>
          </thead>
          <tbody>
            {movimenti.map((m) => (
              <tr key={m.id}>
                <td className="table-cell">{new Date(m.data_operazione).toLocaleDateString('it-IT')}</td>
                <td className="table-cell">{m.tipo}</td>
                <td className={`table-cell ${m.importo > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  €{Math.abs(m.importo).toFixed(2)}
                </td>
                <td className="table-cell">{m.descrizione}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Chiusura Giornaliera</h2>
            <form onSubmit={handleChiusura} className="space-y-4">
              <div>
                <label className="label">Data</label>
                <input type="date" className="input" required
                  value={formData.data}
                  onChange={(e) => setFormData({...formData, data: e.target.value})} />
              </div>
              <div>
                <label className="label">Corrispettivi</label>
                <input type="number" className="input" step="0.01"
                  value={formData.corrispettivi}
                  onChange={(e) => setFormData({...formData, corrispettivi: e.target.value})} />
              </div>
              <div>
                <label className="label">POS</label>
                <input type="number" className="input" step="0.01"
                  value={formData.pos}
                  onChange={(e) => setFormData({...formData, pos: e.target.value})} />
              </div>
              <div>
                <label className="label">Versamento Banca</label>
                <input type="number" className="input" step="0.01"
                  value={formData.versamento}
                  onChange={(e) => setFormData({...formData, versamento: e.target.value})} />
              </div>
              <div className="flex gap-2">
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">Annulla</button>
                <button type="submit" className="btn-primary">Salva</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
