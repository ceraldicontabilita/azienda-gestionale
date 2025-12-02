import React, { useState, useEffect } from 'react';
import { Thermometer, Droplets, FileText, Plus } from 'lucide-react';

export default function HACCP() {
  const [activeTab, setActiveTab] = useState('temperature');
  const [temperature, setTemperature] = useState([]);
  const [sanificazioni, setSanificazioni] = useState([]);
  const [libretti, setLibretti] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTempModal, setShowTempModal] = useState(false);
  const [showSanModal, setShowSanModal] = useState(false);
  const [tempData, setTempData] = useState({
    tipo: 'frigorifero',
    temperatura: '',
    operatore: ''
  });
  const [sanData, setSanData] = useState({
    area: '',
    prodotto_usato: '',
    operatore: ''
  });
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [tempRes, sanRes, libRes] = await Promise.all([
        fetch(`http://localhost:8001/haccp/temperature?id_utente=${user.id}`),
        fetch(`http://localhost:8001/haccp/sanificazioni?id_utente=${user.id}`),
        fetch(`http://localhost:8001/haccp/libretti-sanitari?id_utente=${user.id}`)
      ]);
      const tempData = await tempRes.json();
      const sanData = await sanRes.json();
      const libData = await libRes.json();
      setTemperature(tempData.data || []);
      setSanificazioni(sanData.data || []);
      setLibretti(libData.data || []);
    } catch (error) {
      console.error('Errore:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRegTemp = async (e) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('id_utente', user.id);
    formData.append('tipo', tempData.tipo);
    formData.append('data', new Date().toISOString().split('T')[0]);
    formData.append('ora', new Date().toTimeString().split(' ')[0]);
    formData.append('temperatura', tempData.temperatura);
    formData.append('operatore', tempData.operatore);

    try {
      const response = await fetch('http://localhost:8001/haccp/temperature', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      if (response.ok) {
        setShowTempModal(false);
        setTempData({ tipo: 'frigorifero', temperatura: '', operatore: '' });
        fetchData();
      }
    } catch (error) {
      console.error('Errore:', error);
    }
  };

  const handleRegSan = async (e) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('id_utente', user.id);
    formData.append('data', new Date().toISOString().split('T')[0]);
    formData.append('area', sanData.area);
    formData.append('prodotto_usato', sanData.prodotto_usato);
    formData.append('operatore', sanData.operatore);

    try {
      const response = await fetch('http://localhost:8001/haccp/sanificazioni', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      if (response.ok) {
        setShowSanModal(false);
        setSanData({ area: '', prodotto_usato: '', operatore: '' });
        fetchData();
      }
    } catch (error) {
      console.error('Errore:', error);
    }
  };

  if (loading) return <div className="flex justify-center items-center h-64">Caricamento...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">HACCP</h1>
        {activeTab === 'temperature' && (
          <button
            onClick={() => setShowTempModal(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            <Plus className="w-5 h-5" />
            Registra Temperatura
          </button>
        )}
        {activeTab === 'sanificazioni' && (
          <button
            onClick={() => setShowSanModal(true)}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg"
          >
            <Plus className="w-5 h-5" />
            Registra Sanificazione
          </button>
        )}
      </div>

      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('temperature')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'temperature'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Temperature
        </button>
        <button
          onClick={() => setActiveTab('sanificazioni')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'sanificazioni'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Sanificazioni
        </button>
        <button
          onClick={() => setActiveTab('libretti')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'libretti'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Libretti Sanitari
        </button>
      </div>

      {activeTab === 'temperature' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data/Ora</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Temperatura</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Operatore</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {temperature.map((t) => (
                <tr key={t.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm">{new Date(t.data).toLocaleDateString()} {t.ora}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      t.tipo === 'frigorifero' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'
                    }`}>
                      {t.tipo}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium">{t.temperatura}°C</td>
                  <td className="px-6 py-4 text-sm">{t.operatore}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'sanificazioni' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Area</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prodotto</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Operatore</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {sanificazioni.map((s) => (
                <tr key={s.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm">{new Date(s.data).toLocaleDateString()}</td>
                  <td className="px-6 py-4 text-sm font-medium">{s.area}</td>
                  <td className="px-6 py-4 text-sm">{s.prodotto_usato}</td>
                  <td className="px-6 py-4 text-sm">{s.operatore}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'libretti' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {libretti.map((l) => (
            <div key={l.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <FileText className="w-8 h-8 text-green-600" />
                <div>
                  <h3 className="font-semibold">{l.nome_dipendente} {l.cognome_dipendente}</h3>
                  <p className="text-sm text-gray-500">Numero: {l.numero_libretto}</p>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                <p><span className="text-gray-600">Rilascio:</span> {new Date(l.data_rilascio).toLocaleDateString()}</p>
                <p><span className="text-gray-600">Scadenza:</span> {new Date(l.data_scadenza).toLocaleDateString()}</p>
                <p className={`font-medium ${
                  new Date(l.data_scadenza) < new Date() ? 'text-red-600' : 'text-green-600'
                }`}>
                  {new Date(l.data_scadenza) < new Date() ? 'SCADUTO' : 'Valido'}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {showTempModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-2xl font-bold mb-4">Registra Temperatura</h2>
            <form onSubmit={handleRegTemp} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo *</label>
                <select
                  value={tempData.tipo}
                  onChange={(e) => setTempData({...tempData, tipo: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="frigorifero">Frigorifero</option>
                  <option value="congelatore">Congelatore</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Temperatura (°C) *</label>
                <input
                  type="number"
                  step="0.1"
                  required
                  value={tempData.temperatura}
                  onChange={(e) => setTempData({...tempData, temperatura: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Operatore *</label>
                <input
                  type="text"
                  required
                  value={tempData.operatore}
                  onChange={(e) => setTempData({...tempData, operatore: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowTempModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  Annulla
                </button>
                <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
                  Registra
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showSanModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-2xl font-bold mb-4">Registra Sanificazione</h2>
            <form onSubmit={handleRegSan} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Area *</label>
                <input
                  type="text"
                  required
                  value={sanData.area}
                  onChange={(e) => setSanData({...sanData, area: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Laboratorio pasticceria"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Prodotto Usato *</label>
                <input
                  type="text"
                  required
                  value={sanData.prodotto_usato}
                  onChange={(e) => setSanData({...sanData, prodotto_usato: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Amuchina"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Operatore *</label>
                <input
                  type="text"
                  required
                  value={sanData.operatore}
                  onChange={(e) => setSanData({...sanData, operatore: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowSanModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  Annulla
                </button>
                <button type="submit" className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg">
                  Registra
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
