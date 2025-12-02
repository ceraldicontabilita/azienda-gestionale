import React, { useState, useEffect } from 'react'
import { Package, Plus } from 'lucide-react'
import axios from 'axios'

export default function Magazzino() {
  const [prodotti, setProdotti] = useState([])

  useEffect(() => {
    fetchProdotti()
  }, [])

  const fetchProdotti = async () => {
    try {
      const response = await axios.get('/api/warehouse/', { params: { id_utente: 1 } })
      setProdotti(response.data.data || [])
    } catch (error) {
      console.error('Errore:', error)
    }
  }

  const popolaDaFatture = async () => {
    if (!confirm('Popolare magazzino da fatture?')) return
    try {
      await axios.post('/api/warehouse/populate-from-invoices', 
        new FormData().append('id_utente', 1))
      alert('Magazzino popolato!')
      fetchProdotti()
    } catch (error) {
      alert('Errore')
    }
  }

  return (
    <div className="p-6">
      <div className="flex justify-between mb-6">
        <h1 className="text-2xl font-bold">Magazzino</h1>
        <button onClick={popolaDaFatture} className="btn-primary">
          Popola da Fatture
        </button>
      </div>

      <div className="bg-white rounded-lg shadow">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="table-header">Descrizione</th>
              <th className="table-header">Categoria</th>
              <th className="table-header">Quantità</th>
              <th className="table-header">Prezzo Acquisto</th>
            </tr>
          </thead>
          <tbody>
            {prodotti.map((p) => (
              <tr key={p.id}>
                <td className="table-cell">{p.descrizione}</td>
                <td className="table-cell">{p.categoria || '-'}</td>
                <td className="table-cell">{p.quantita || 0}</td>
                <td className="table-cell">
                  {p.prezzo_acquisto ? `€${parseFloat(p.prezzo_acquisto).toFixed(2)}` : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
