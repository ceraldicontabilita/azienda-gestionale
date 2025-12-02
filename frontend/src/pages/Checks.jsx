import React, { useState, useEffect } from 'react';
import { FileText, Plus, CheckCircle, Filter } from 'lucide-react';

export default function Checks() {
  const [assegni, setAssegni] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showCarnetModal, setShowCarnetModal] = useState(false);
  const [filtroStato, setFiltroStato] = useState('');
  const [carnetData, setCarnetData] = useState({
    banca: '',
    numero_inizio: '',
    quantita: ''
  });
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [assegniRes, statsRes] = await Promise.all([
        fetch(`http://localhost:8001/checks/?id_utente=${user.id}`),
        fetch(`http://localhost:8001/checks/stats?id_utente=${user.id}`)
      ]);
      const assegniData = await assegniRes.json();
      const statsData = await statsRes.json();
      setAssegni(assegniData.data || []);
      setStats(statsData.data || {});
    } catch (error) {
      console.error('Errore:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreaCarnet = async (e) => {
    e.preventDefault();
    
    const formData = new URLSearchParams();
    formData.append('id_utente', user.id);
    formData.append('banca', carnetData.banca);
    formData.append('numero_inizio', carnetData.numero_inizio);
    formData.append('quantita', carnetData.quantita);

    try {
      const response = await fetch('http://localhost:8001/checks/batch-create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      if (response.ok) {
        setShowCarnetModal(false);
        setCarnetData({ banca: '', numero_inizio: '', quantita: '' });
        fetchData();
        alert('Carnet creato con successo!');
      }
    } catch (error) {
      console.error('Errore:', error);
      alert('Errore durante creazione carnet');
    }
  };

  const handleSegnaIncassato = async (id) => {
    if (!confirm('Segnare questo assegno come incassato?')) return;

    const formData = new URLSearchParams();
    formData.append('id_utente', user.id);

    try {
      const response = await fetch(`http://localhost:8001/checks/${id}/mark-incassato`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      if (response.ok) {
        fetchData();
      }
    } catch (error) {
      console.error('Errore:', error);
    }
  };

  const getStatoBadge = (stato) => {
    const colors = {
      disponibile: 'bg-green-100 text-green-800',
      emesso: 'bg-yellow-100 text-yellow-800',
      incassato: 'bg-blue-100 text-blue-800',
      annullato: 'bg-red-100 text-red-800'
    };
    return colors[stato] || 'bg-gray-100 text-gray-800';
  };

  const assegniFiltrati = filtroStato 
    ? assegni.filter(a => a.stato === filtroStato)
    : assegni;

  if (loading) return <div className="flex justify-center items-center h-64">Caricamento...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestione Assegni</h1>
          <p className="text-gray-600 mt-1">{assegni.length} assegni totali</p>
        </div>
        <button
          onClick={() => setShowCarnetModal(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          Crea Carnet
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Object.entries(stats).map(([key, value]) => (
          <div key={key} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <p className="text-sm text-gray-600 capitalize">{key.replace('_', ' ')}</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-gray-500" />
          <select
            value={filtroStato}
            onChange={(e) => setFiltroStato(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tutti gli stati</option>
            <option value="disponibile">Disponibile</option>
            <option value="emesso">Emesso</option>
            <option value="incassato">Incassato</option>
            <option value="annullato">Annullato</option>
          </select>
          <span className="text-sm text-gray-600">
            {assegniFiltrati.length} assegni
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Numero</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Banca</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stato</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Beneficiario</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Importo</th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Azioni</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {assegniFiltrati.map((assegno) => (
                <tr key={assegno.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{assegno.numero_assegno}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{assegno.banca}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatoBadge(assegno.stato)}`}>
                      {assegno.stato}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{assegno.beneficiario || '-'}</td>
                  <td className="px-6 py-4 text-right text-sm font-medium text-gray-900">
                    {assegno.importo ? `€${assegno.importo.toFixed(2)}` : '-'}
                  </td>
                  <td className="px-6 py-4 text-center">
                    {assegno.stato === 'emesso' && (
                      <button
                        onClick={() => handleSegnaIncassato(assegno.id)}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        Segna Incassato
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showCarnetModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-2xl font-bold mb-4">Crea Carnet Assegni</h2>
            <form onSubmit={handleCreaCarnet} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Banca *
                </label>
                <input
                  type="text"
                  required
                  value={carnetData.banca}
                  onChange={(e) => setCarnetData({...carnetData, banca: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Intesa Sanpaolo"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Numero Primo Assegno *
                </label>
                <input
                  type="text"
                  required
                  value={carnetData.numero_inizio}
                  onChange={(e) => setCarnetData({...carnetData, numero_inizio: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="1001"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quantità Assegni *
                </label>
                <input
                  type="number"
                  required
                  min="1"
                  max="50"
                  value={carnetData.quantita}
                  onChange={(e) => setCarnetData({...carnetData, quantita: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="25"
                />
                <p className="text-xs text-gray-500 mt-1">Es: Da 1001 a 1025 (25 assegni)</p>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCarnetModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Annulla
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  Crea Carnet
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
