import React, { useState, useEffect } from 'react';
import { Package, Plus, RefreshCw, Filter } from 'lucide-react';

export default function Warehouse() {
  const [prodotti, setProdotti] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [filtroCategoria, setFiltroCategoria] = useState('');
  const [formData, setFormData] = useState({
    codice_prodotto: '',
    descrizione: '',
    categoria: '',
    unita_misura: 'kg',
    quantita: '',
    prezzo_acquisto: ''
  });
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    fetchProdotti();
  }, []);

  const fetchProdotti = async () => {
    try {
      const url = filtroCategoria
        ? `http://localhost:8001/warehouse/?id_utente=${user.id}&categoria=${filtroCategoria}`
        : `http://localhost:8001/warehouse/?id_utente=${user.id}`;
      const response = await fetch(url);
      const data = await response.json();
      setProdotti(data.data || []);
    } catch (error) {
      console.error('Errore:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formDataToSend = new URLSearchParams();
    Object.keys(formData).forEach(key => {
      if (formData[key]) formDataToSend.append(key, formData[key]);
    });
    formDataToSend.append('id_utente', user.id);

    try {
      const response = await fetch('http://localhost:8001/warehouse/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formDataToSend
      });

      if (response.ok) {
        setShowModal(false);
        setFormData({
          codice_prodotto: '',
          descrizione: '',
          categoria: '',
          unita_misura: 'kg',
          quantita: '',
          prezzo_acquisto: ''
        });
        fetchProdotti();
        alert('Prodotto creato con successo!');
      }
    } catch (error) {
      console.error('Errore:', error);
      alert('Errore durante creazione');
    }
  };

  const handlePopola = async () => {
    if (!confirm('Popolare magazzino da fatture? Verranno creati prodotti per ogni riga fattura univoca.')) return;

    const formData = new URLSearchParams();
    formData.append('id_utente', user.id);

    try {
      const response = await fetch('http://localhost:8001/warehouse/populate-from-invoices', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        fetchProdotti();
        alert(`Magazzino popolato! ${data.prodotti_creati} prodotti creati.`);
      }
    } catch (error) {
      console.error('Errore:', error);
      alert('Errore durante popolamento');
    }
  };

  const categorie = [...new Set(prodotti.map(p => p.categoria).filter(Boolean))];
  const prodottiFiltrati = filtroCategoria
    ? prodotti.filter(p => p.categoria === filtroCategoria)
    : prodotti;

  if (loading) return <div className="flex justify-center items-center h-64">Caricamento...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Magazzino</h1>
          <p className="text-gray-600 mt-1">{prodotti.length} prodotti in inventario</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handlePopola}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
            Popola da Fatture
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            Nuovo Prodotto
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-gray-500" />
          <select
            value={filtroCategoria}
            onChange={(e) => {
              setFiltroCategoria(e.target.value);
              fetchProdotti();
            }}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tutte le categorie</option>
            {categorie.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
          <span className="text-sm text-gray-600">
            {prodottiFiltrati.length} prodotti
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Codice</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrizione</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Categoria</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Quantità</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Prezzo Acquisto</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {prodottiFiltrati.map((prod) => (
                <tr key={prod.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{prod.codice_prodotto}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{prod.descrizione}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                      {prod.categoria || 'N/D'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right text-sm">
                    {prod.quantita} {prod.unita_misura}
                  </td>
                  <td className="px-6 py-4 text-right text-sm font-medium">
                    €{prod.prezzo_acquisto?.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6">
            <h2 className="text-2xl font-bold mb-4">Nuovo Prodotto</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Codice Prodotto *</label>
                  <input
                    type="text"
                    required
                    value={formData.codice_prodotto}
                    onChange={(e) => setFormData({...formData, codice_prodotto: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
                  <input
                    type="text"
                    value={formData.categoria}
                    onChange={(e) => setFormData({...formData, categoria: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Descrizione *</label>
                <input
                  type="text"
                  required
                  value={formData.descrizione}
                  onChange={(e) => setFormData({...formData, descrizione: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Unità Misura *</label>
                  <select
                    value={formData.unita_misura}
                    onChange={(e) => setFormData({...formData, unita_misura: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="kg">kg</option>
                    <option value="litri">litri</option>
                    <option value="pezzi">pezzi</option>
                    <option value="confezioni">confezioni</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Quantità *</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={formData.quantita}
                    onChange={(e) => setFormData({...formData, quantita: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Prezzo Acquisto (€)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.prezzo_acquisto}
                    onChange={(e) => setFormData({...formData, prezzo_acquisto: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Annulla
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  Crea Prodotto
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
