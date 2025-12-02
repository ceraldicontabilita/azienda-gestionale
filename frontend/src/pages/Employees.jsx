import React, { useState, useEffect } from 'react';
import { Users, Plus, Upload, Edit, FileText } from 'lucide-react';

export default function Employees() {
  const [dipendenti, setDipendenti] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showPagheModal, setShowPagheModal] = useState(false);
  const [selectedDipendente, setSelectedDipendente] = useState(null);
  const [paghe, setPaghe] = useState([]);
  const [formData, setFormData] = useState({
    nome: '',
    cognome: '',
    codice_fiscale: '',
    email: '',
    telefono: '',
    mansione: '',
    retribuzione_mensile: ''
  });
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    fetchDipendenti();
  }, []);

  const fetchDipendenti = async () => {
    try {
      const response = await fetch(`http://localhost:8001/dipendenti/?id_utente=${user.id}`);
      const data = await response.json();
      setDipendenti(data.data || []);
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
      const response = await fetch('http://localhost:8001/dipendenti/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formDataToSend
      });

      if (response.ok) {
        setShowModal(false);
        setFormData({
          nome: '',
          cognome: '',
          codice_fiscale: '',
          email: '',
          telefono: '',
          mansione: '',
          retribuzione_mensile: ''
        });
        fetchDipendenti();
        alert('Dipendente creato con successo!');
      }
    } catch (error) {
      console.error('Errore:', error);
      alert('Errore durante creazione');
    }
  };

  const handleUploadBustaPaga = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('id_utente', user.id);

    try {
      const response = await fetch('http://localhost:8001/dipendenti/upload-busta-paga', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        alert('Busta paga caricata con successo!');
        fetchDipendenti();
      }
    } catch (error) {
      console.error('Errore:', error);
    }
  };

  const openPagheModal = async (dipendente) => {
    setSelectedDipendente(dipendente);
    setShowPagheModal(true);
    
    try {
      const response = await fetch(
        `http://localhost:8001/dipendenti/${dipendente.id}/paghe?id_utente=${user.id}`
      );
      const data = await response.json();
      setPaghe(data.data || []);
    } catch (error) {
      console.error('Errore:', error);
    }
  };

  if (loading) return <div className="flex justify-center items-center h-64">Caricamento...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dipendenti</h1>
          <p className="text-gray-600 mt-1">{dipendenti.length} dipendenti attivi</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            Nuovo Dipendente
          </button>
          <label className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg cursor-pointer transition-colors">
            <Upload className="w-5 h-5" />
            Carica Busta Paga
            <input
              type="file"
              accept=".pdf"
              onChange={handleUploadBustaPaga}
              className="hidden"
            />
          </label>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {dipendenti.map((dip) => (
          <div key={dip.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{dip.nome} {dip.cognome}</h3>
                <p className="text-sm text-gray-500">{dip.mansione}</p>
              </div>
            </div>
            <div className="space-y-2 text-sm text-gray-600">
              <p>CF: {dip.codice_fiscale}</p>
              {dip.email && <p>Email: {dip.email}</p>}
              {dip.retribuzione_mensile && (
                <p className="font-medium text-gray-900">
                  €{dip.retribuzione_mensile.toFixed(2)}/mese
                </p>
              )}
            </div>
            <button
              onClick={() => openPagheModal(dip)}
              className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-lg transition-colors"
            >
              <FileText className="w-4 h-4" />
              Vedi Paghe
            </button>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Nuovo Dipendente</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
                  <input
                    type="text"
                    required
                    value={formData.nome}
                    onChange={(e) => setFormData({...formData, nome: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Cognome *</label>
                  <input
                    type="text"
                    required
                    value={formData.cognome}
                    onChange={(e) => setFormData({...formData, cognome: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Codice Fiscale *</label>
                <input
                  type="text"
                  required
                  maxLength={16}
                  value={formData.codice_fiscale}
                  onChange={(e) => setFormData({...formData, codice_fiscale: e.target.value.toUpperCase()})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Telefono</label>
                  <input
                    type="tel"
                    value={formData.telefono}
                    onChange={(e) => setFormData({...formData, telefono: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Mansione</label>
                  <input
                    type="text"
                    value={formData.mansione}
                    onChange={(e) => setFormData({...formData, mansione: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Retribuzione Mensile (€)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.retribuzione_mensile}
                    onChange={(e) => setFormData({...formData, retribuzione_mensile: e.target.value})}
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
                  Crea Dipendente
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showPagheModal && selectedDipendente && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">
                Buste Paga - {selectedDipendente.nome} {selectedDipendente.cognome}
              </h2>
              <button
                onClick={() => setShowPagheModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {paghe.length === 0 ? (
              <p className="text-center text-gray-500 py-8">Nessuna busta paga trovata</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Mese</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Lordo</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Netto</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">INPS</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">IRPEF</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {paghe.map((paga) => (
                      <tr key={paga.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm">{paga.mese_anno}</td>
                        <td className="px-4 py-3 text-sm text-right">€{paga.retribuzione_lorda?.toFixed(2)}</td>
                        <td className="px-4 py-3 text-sm text-right font-medium">€{paga.retribuzione_netta?.toFixed(2)}</td>
                        <td className="px-4 py-3 text-sm text-right">€{paga.inps?.toFixed(2)}</td>
                        <td className="px-4 py-3 text-sm text-right">€{paga.irpef?.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
