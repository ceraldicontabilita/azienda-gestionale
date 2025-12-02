import React, { useState, useEffect } from 'react'
import { Upload } from 'lucide-react'
import axios from 'axios'

export default function GestioneBonifici() {
  const [bonifici, setBonifici] = useState([])

  useEffect(() => {
    fetchBonifici()
  }, [])

  const fetchBonifici = async () => {
    try {
      const response = await axios.get('/api/bank/', { params: { id_utente: 1 } })
      setBonifici(response.data.data || [])
    } catch (error) {
      console.error('Errore:', error)
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Gestione Bonifici</h1>
      
      <div className="bg-white rounded-lg shadow">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="table-header">Data</th>
              <th className="table-header">Importo</th>
              <th className="table-header">Beneficiario</th>
              <th className="table-header">Stato</th>
            </tr>
          </thead>
          <tbody>
            {bonifici.map((b) => (
              <tr key={b.id}>
                <td className="table-cell">{new Date(b.data_bonifico).toLocaleDateString('it-IT')}</td>
                <td className="table-cell">€{parseFloat(b.importo).toFixed(2)}</td>
                <td className="table-cell">{b.beneficiario}</td>
                <td className="table-cell">
                  <span className={`px-2 py-1 rounded text-xs ${
                    b.collegato ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {b.collegato ? 'Collegato' : 'Da collegare'}
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
