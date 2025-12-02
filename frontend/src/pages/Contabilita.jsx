import React, { useState } from 'react'
import { BarChart3, FileText } from 'lucide-react'
import axios from 'axios'

export default function Contabilita() {
  const [anno, setAnno] = useState(new Date().getFullYear())
  const [bilancio, setBilancio] = useState(null)

  const generaBilancio = async () => {
    try {
      const response = await axios.get('/api/contabilita/bilancio/conto-economico', {
        params: { id_utente: 1, anno }
      })
      setBilancio(response.data.data)
    } catch (error) {
      alert('Errore')
    }
  }

  const popolaPiano = async () => {
    if (!confirm('Popolare piano dei conti?')) return
    try {
      const formData = new FormData()
      formData.append('id_utente', 1)
      await axios.post('/api/contabilita/popola-piano-conti', formData)
      alert('Piano dei conti popolato!')
    } catch (error) {
      alert(error.response?.data?.detail || 'Errore')
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Contabilità</h1>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <button onClick={popolaPiano} className="card hover:shadow-lg transition-shadow">
          <FileText className="text-blue-600 mb-2" size={32} />
          <h3 className="font-bold">Popola Piano dei Conti</h3>
          <p className="text-sm text-gray-600">Crea 45+ conti base</p>
        </button>
        
        <div className="card">
          <BarChart3 className="text-green-600 mb-2" size={32} />
          <h3 className="font-bold">Conto Economico</h3>
          <div className="flex gap-2 mt-2">
            <input type="number" className="input" value={anno}
              onChange={(e) => setAnno(e.target.value)} />
            <button onClick={generaBilancio} className="btn-primary">Genera</button>
          </div>
        </div>
      </div>

      {bilancio && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-bold mb-4">Conto Economico {bilancio.anno}</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="card bg-green-50">
              <p className="text-sm text-gray-600">Ricavi</p>
              <p className="text-2xl font-bold text-green-600">€{bilancio.ricavi.totale.toFixed(2)}</p>
            </div>
            <div className="card bg-red-50">
              <p className="text-sm text-gray-600">Costi</p>
              <p className="text-2xl font-bold text-red-600">€{bilancio.costi.totale.toFixed(2)}</p>
            </div>
            <div className={`card ${bilancio.utile_perdita >= 0 ? 'bg-blue-50' : 'bg-orange-50'}`}>
              <p className="text-sm text-gray-600">{bilancio.utile_perdita >= 0 ? 'UTILE' : 'PERDITA'}</p>
              <p className={`text-2xl font-bold ${bilancio.utile_perdita >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                €{Math.abs(bilancio.utile_perdita).toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
