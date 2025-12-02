import React, { useState, useEffect } from 'react';
import { BarChart3, PieChart, TrendingUp, Calendar } from 'lucide-react';

export default function Analytics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [periodo, setPeriodo] = useState('mese');
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    fetchStats();
  }, [periodo]);

  const fetchStats = async () => {
    try {
      const response = await fetch(`http://localhost:8001/dashboard/?id_utente=${user.id}`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Errore:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="flex justify-center items-center h-64">Caricamento...</div>;
  if (!stats) return <div className="text-center text-gray-500 py-8">Nessun dato disponibile</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <select
          value={periodo}
          onChange={(e) => setPeriodo(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="settimana">Ultima Settimana</option>
          <option value="mese">Ultimo Mese</option>
          <option value="trimestre">Ultimo Trimestre</option>
          <option value="anno">Ultimo Anno</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            <div>
              <p className="text-sm text-gray-600">Fatture Totali</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totale_fatture || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <PieChart className="w-8 h-8 text-green-600" />
            <div>
              <p className="text-sm text-gray-600">Fatture Pagate</p>
              <p className="text-2xl font-bold text-green-600">{stats.fatture_pagate || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-8 h-8 text-yellow-600" />
            <div>
              <p className="text-sm text-gray-600">Da Pagare</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.fatture_da_pagare || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Calendar className="w-8 h-8 text-purple-600" />
            <div>
              <p className="text-sm text-gray-600">Fornitori</p>
              <p className="text-2xl font-bold text-purple-600">{stats.totale_fornitori || 0}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Riepilogo Importi</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-gray-600 mb-2">Importo Totale Fatture</p>
            <p className="text-3xl font-bold text-gray-900">
              €{stats.importo_totale?.toFixed(2) || '0.00'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-2">Media per Fattura</p>
            <p className="text-3xl font-bold text-blue-600">
              €{stats.totale_fatture > 0 
                ? (stats.importo_totale / stats.totale_fatture).toFixed(2) 
                : '0.00'}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Andamento nel Tempo</h2>
        <div className="h-64 flex items-center justify-center text-gray-500">
          <p>Grafico in arrivo (integrazione con Chart.js)</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Top 5 Fornitori per Importo</h2>
          <div className="space-y-3">
            <p className="text-center text-gray-500">Dati in elaborazione...</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Distribuzione per Categoria</h2>
          <div className="space-y-3">
            <p className="text-center text-gray-500">Dati in elaborazione...</p>
          </div>
        </div>
      </div>
    </div>
  );
}
