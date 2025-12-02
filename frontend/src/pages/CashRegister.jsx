import React, { useState, useEffect } from 'react';
import { Wallet, Plus, TrendingDown, TrendingUp, Calendar, Upload } from 'lucide-react';

export default function CashRegister() {
  const [movimenti, setMovimenti] = useState([]);
  const [saldo, setSaldo] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showChiusuraModal, setShowChiusuraModal] = useState(false);
  const [chiusuraData, setChiusuraData] = useState({
    data: new Date().toISOString().split('T')[0],
    corrispettivi: '',
    pos: '',
    versamento: ''
  });
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [movRes, saldoRes] = await Promise.all([
        fetch(`http://localhost:8001/cash-register/?id_utente=${user.id}`),
        fetch(`http://localhost:8001/cash-register/saldo?id_utente=${user.id}`)
      ]);
      const movData = await movRes.json();
      const saldoData = await saldoRes.json();
      setMovimenti(movData.data || []);
      setSaldo(saldoData.saldo || 0);
    } catch (error) {
      console.error('Errore:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChiusura = async (e) => {
    e.preventDefault();
    
    const formData = new URLSearchParams();
    formData.append('id_utente', user.id);
    formData.append('data', chiusuraData.data);
    formData.append('corrispettivi', chiusuraData.corrispettivi);
    formData.append('pos', chiusuraData.pos);
    formData.append('versamento', chiusuraData.versamento);

    try {
      const response = await fetch('http://localhost:8001/cash-register/chiusura-giornaliera', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      if (response.ok) {
        setShowChiusuraModal(false);
        setChiusuraData({
          data: new Date().toISOString().split('T')[0],
          corrispettivi: '',
          pos: '',
          versamento: ''
        });
        fetchData();
        alert('Chiusura registrata con successo!');
      }
    } catch (error) {
      console.error('Errore:', error);
      alert('Errore durante la chiusura');
    }
  };

  const handleImportExcel = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('id_utente', user.id);

    try {
      const response = await fetch('http://localhost:8001/cash-register/import-corrispettivi', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        fetchData();
        alert('File importato con successo!');
      }
    } catch (error) {
      console.error('Errore:', error);
      alert('Errore durante import');
    }
  };

  if (loading) return <div className="flex justify-center items-center h-64">Caricamento...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Prima Nota Cassa</h1>
          <p className="text-gray-600 mt-1">{movimenti.length} movimenti registrati</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm text-gray-600">Saldo Cassa</p>
            <p className={`text-3xl font-bold ${saldo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              €{saldo.toFixed(2)}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowChiusuraModal(true)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <Calendar className="w-5 h-5" />
              Chiusura Giornaliera
            </button>
            <label className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg cursor-pointer transition-colors">
              <Upload className="w-5 h-5" />
              Import Excel
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleImportExcel}
                className="hidden"
              />
            </label>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrizione</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Importo</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {movimenti.map((mov) => (
                <tr key={mov.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {new Date(mov.data).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                      {mov.tipo}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{mov.descrizione}</td>
                  <td className="px-6 py-4 text-right">
                    <span className={`font-medium ${mov.importo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {mov.importo >= 0 ? '+' : ''}€{mov.importo.toFixed(2)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showChiusuraModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-2xl font-bold mb-4">Chiusura Giornaliera</h2>
            <form onSubmit={handleChiusura} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Data</label>
                <input
                  type="date"
                  required
                  value={chiusuraData.data}
                  onChange={(e) => setChiusuraData({...chiusuraData, data: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Corrispettivi (€)
                </label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={chiusuraData.corrispettivi}
                  onChange={(e) => setChiusuraData({...chiusuraData, corrispettivi: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="1500.00"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Transazioni POS (€)
                </label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={chiusuraData.pos}
                  onChange={(e) => setChiusuraData({...chiusuraData, pos: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="800.00"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Versamento in Banca (€)
                </label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={chiusuraData.versamento}
                  onChange={(e) => setChiusuraData({...chiusuraData, versamento: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="500.00"
                />
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Saldo Calcolato:</p>
                <p className="text-2xl font-bold text-gray-900">
                  €{(
                    parseFloat(chiusuraData.corrispettivi || 0) -
                    parseFloat(chiusuraData.pos || 0) -
                    parseFloat(chiusuraData.versamento || 0)
                  ).toFixed(2)}
                </p>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowChiusuraModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Annulla
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  Registra Chiusura
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
