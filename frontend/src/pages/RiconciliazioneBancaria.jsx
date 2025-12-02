import React, { useState, useEffect } from 'react'
import { Link } from 'lucide-react'
import axios from 'axios'

export default function RiconciliazioneBancaria() {
  const [movimenti, setMovimenti] = useState([])

  useEffect(() => {
    fetchMovimenti()
  }, [])

  const fetchMovimenti = async () => {
    try {
      const response = await axios.get('/api/reconciliation/', { params: { id_utente: 1 } })
      setMovimenti(response.data.data || [])
    } catch (error) {
      console.error('Errore:', error)
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Riconciliazione Bancaria</h1>
      
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b bg-gray-50">
          <h2 className="font-bold">Movimenti Non Riconciliati</h2>
        </div>
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
    </div>
  )
}
