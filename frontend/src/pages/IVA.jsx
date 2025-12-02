import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Calendar } from 'lucide-react';

export default function IVA() {
  const [liquidazione, setLiquidazione] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mese, setMese] = useState(new Date().getMonth() + 1);
  const [anno, setAnno] = useState(new Date().getFullYear());
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const fetchLiquidazione = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8001/iva/liquidazione?id_utente=${user.id}&mese=${mese}&anno=${anno}`
      );
      const data = await response.json();
      setLiquidazione(data.data);
    } catch (error) {
      console.error('Errore:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiquidazione();
  }, []);

  const mesi = [
    'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
    'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Liquidazione IVA</h1>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Mese</label>
            <select
              value={mese}
              onChange={(e) => setMese(parseInt(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {mesi.map((m, i) => (
                <option key={i} value={i + 1}>{m}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Anno</label>
            <select
              value={anno}
              onChange={(e) => setAnno(parseInt(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {[2023, 2024, 2025, 2026].map(a => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </div>
          <button
            onClick={fetchLiquidazione}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? 'Caricamento...' : 'Calcola'}
          </button>
        </div>
      </div>

      {liquidazione && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow-sm border border-green-200 p-6">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-green-700 font-medium">IVA Vendite</p>
                  <p className="text-xs text-green-600">(Da versare)</p>
                </div>
              </div>
              <p className="text-3xl font-bold text-green-900">
                €{liquidazione.iva_vendite?.toFixed(2) || '0.00'}
              </p>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow-sm border border-blue-200 p-6">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                  <TrendingDown className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-blue-700 font-medium">IVA Acquisti</p>
                  <p className="text-xs text-blue-600">(Detraibile)</p>
                </div>
              </div>
              <p className="text-3xl font-bold text-blue-900">
                €{liquidazione.iva_acquisti?.toFixed(2) || '0.00'}
              </p>
            </div>

            <div className={`bg-gradient-to-br ${
              liquidazione.iva_da_versare >= 0 
                ? 'from-red-50 to-red-100 border-red-200' 
                : 'from-yellow-50 to-yellow-100 border-yellow-200'
            } rounded-lg shadow-sm border p-6`}>
              <div className="flex items-center gap-3 mb-2">
                <div className={`w-12 h-12 ${
                  liquidazione.iva_da_versare >= 0 ? 'bg-red-600' : 'bg-yellow-600'
                } rounded-full flex items-center justify-center`}>
                  <DollarSign className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className={`text-sm font-medium ${
                    liquidazione.iva_da_versare >= 0 ? 'text-red-700' : 'text-yellow-700'
                  }`}>
                    {liquidazione.tipo === 'debito' ? 'IVA da Versare' : 'IVA a Credito'}
                  </p>
                  <p className={`text-xs ${
                    liquidazione.iva_da_versare >= 0 ? 'text-red-600' : 'text-yellow-600'
                  }`}>
                    {liquidazione.tipo === 'debito' ? 'Debito' : 'Credito'}
                  </p>
                </div>
              </div>
              <p className={`text-3xl font-bold ${
                liquidazione.iva_da_versare >= 0 ? 'text-red-900' : 'text-yellow-900'
              }`}>
                €{Math.abs(liquidazione.iva_da_versare)?.toFixed(2) || '0.00'}
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Riepilogo Liquidazione</h2>
            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">Periodo:</span>
                <span className="font-medium">{mesi[mese - 1]} {anno}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">IVA Vendite (da versare):</span>
                <span className="font-medium text-green-600">
                  +€{liquidazione.iva_vendite?.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">IVA Acquisti (detraibile):</span>
                <span className="font-medium text-blue-600">
                  -€{liquidazione.iva_acquisti?.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between py-3 bg-gray-50 rounded-lg px-4">
                <span className="font-bold text-gray-900">Risultato:</span>
                <span className={`font-bold text-lg ${
                  liquidazione.tipo === 'debito' ? 'text-red-600' : 'text-yellow-600'
                }`}>
                  {liquidazione.tipo === 'debito' ? 'DEBITO' : 'CREDITO'} di €
                  {Math.abs(liquidazione.iva_da_versare)?.toFixed(2)}
                </span>
              </div>
            </div>

            {liquidazione.tipo === 'debito' && liquidazione.iva_da_versare > 0 && (
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-800">
                  <strong>Attenzione:</strong> Devi versare €{liquidazione.iva_da_versare.toFixed(2)} 
                  entro il 16 del mese successivo al trimestre.
                </p>
              </div>
            )}

            {liquidazione.tipo === 'credito' && (
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <strong>Nota:</strong> Hai un credito IVA di €{Math.abs(liquidazione.iva_da_versare).toFixed(2)} 
                  che puoi compensare con versamenti futuri.
                </p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
