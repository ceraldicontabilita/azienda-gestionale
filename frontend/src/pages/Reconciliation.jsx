import React, { useState, useEffect } from 'react';
import { Link, Check } from 'lucide-react';

export default function Reconciliation() {
  const [movimenti, setMovimenti] = useState([]);
  const [loading, setLoading] = useState(true);
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    fetchMovimenti();
  }, []);

  const fetchMovimenti = async () => {
    try {
      const response = await fetch(`http://localhost:8001/reconciliation/?id_utente=${user.id}`);
      const data = await response.json();
      setMovimenti(data.data || []);
    } catch (error) {
      console.error('Errore:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRiconcilia = async (idMovimento, idFattura) => {
    if (!idFattura) {
      alert('Seleziona una fattura');
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8001/reconciliation/match?id_movimento=${idMovimento}&id_fattura=${idFattura}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id_utente: user.id })
        }
      );

      if (response.ok) {
        fetchMovimenti();
        alert('Riconciliazione completata!');
      }
    } catch (error) {
      console.error('Errore:', error);
      alert('Errore durante riconciliazione');
    }
  };

  if (loading) return <div className="flex justify-center items-center h-64">Caricamento...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Riconciliazione Bancaria</h1>
          <p className="text-gray-600 mt-1">{movimenti.length} movimenti da riconciliare</p>
        </div>
      </div>

      {movimenti.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <Check className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Tutto riconciliato!</h2>
          <p className="text-gray-600">Non ci sono movimenti bancari da riconciliare.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrizione</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Importo</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fattura Collegata</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Azioni</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {movimenti.map((mov) => (
                  <MovimentoRow
                    key={mov.id}
                    movimento={mov}
                    onRiconcilia={handleRiconcilia}
                    userId={user.id}
                  />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function MovimentoRow({ movimento, onRiconcilia, userId }) {
  const [fatture, setFatture] = useState([]);
  const [selectedFattura, setSelectedFattura] = useState('');

  useEffect(() => {
    fetchFatture();
  }, []);

  const fetchFatture = async () => {
    try {
      const response = await fetch(`http://localhost:8001/invoices/?id_utente=${userId}&pagata=false`);
      const data = await response.json();
      setFatture(data.data || []);
    } catch (error) {
      console.error('Errore:', error);
    }
  };

  return (
    <tr className="hover:bg-gray-50">
      <td className="px-6 py-4 text-sm text-gray-900">
        {new Date(movimento.data).toLocaleDateString()}
      </td>
      <td className="px-6 py-4 text-sm text-gray-600">{movimento.descrizione}</td>
      <td className="px-6 py-4 text-right text-sm font-medium text-red-600">
        -€{Math.abs(movimento.importo).toFixed(2)}
      </td>
      <td className="px-6 py-4">
        <select
          value={selectedFattura}
          onChange={(e) => setSelectedFattura(e.target.value)}
          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Seleziona fattura...</option>
          {fatture.map((f) => (
            <option key={f.id} value={f.id}>
              {f.numero_fattura} - {f.ragione_sociale_fornitore} - €{f.totale?.toFixed(2)}
            </option>
          ))}
        </select>
      </td>
      <td className="px-6 py-4 text-center">
        <button
          onClick={() => onRiconcilia(movimento.id, selectedFattura)}
          disabled={!selectedFattura}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Riconcilia
        </button>
      </td>
    </tr>
  );
}
