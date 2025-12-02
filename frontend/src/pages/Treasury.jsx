import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Calendar } from 'lucide-react';

export default function Treasury() {
  const [saldoCassa, setSaldoCassa] = useState(0);
  const [saldoBanca, setSaldoBanca] = useState(0);
  const [fattureNonPagate, setFattureNonPagate] = useState([]);
  const [loading, setLoading] = useState(true);
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [cassaRes, fattureRes] = await Promise.all([
        fetch(`http://localhost:8001/cash-register/saldo?id_utente=${user.id}`),
        fetch(`http://localhost:8001/invoices/?id_utente=${user.id}&pagata=false`)
      ]);
      
      const cassaData = await cassaRes.json();
      const fattureData = await fattureRes.json();
      
      setSaldoCassa(cassaData.saldo || 0);
      setFattureNonPagate(fattureData.data || []);
      
      const totaleBanca = (fattureData.data || []).reduce((acc, f) => acc + (f.totale || 0), 0);
      setSaldoBanca(-totaleBanca);
    } catch (error) {
      console.error('Errore:', error);
    } finally {
      setLoading(false);
    }
  };

  const totaleLiquidita = saldoCassa + saldoBanca;
  const totaleDaPagare = fattureNonPagate.reduce((acc, f) => acc + (f.totale || 0), 0);

  if (loading) return <div className="flex justify-center items-center h-64">Caricamento...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Tesoreria</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow-sm border border-green-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-green-700 font-medium">Liquidità Totale</p>
              <p className="text-xs text-green-600">Cassa + Banca</p>
            </div>
          </div>
          <p className={`text-3xl font-bold ${totaleLiquidita >= 0 ? 'text-green-900' : 'text-red-900'}`}>
            €{totaleLiquidita.toFixed(2)}
          </p>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow-sm border border-blue-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-blue-700 font-medium">Saldo Cassa</p>
              <p className="text-xs text-blue-600">Contanti disponibili</p>
            </div>
          </div>
          <p className="text-3xl font-bold text-blue-900">
            €{saldoCassa.toFixed(2)}
          </p>
        </div>

        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg shadow-sm border border-red-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center">
              <TrendingDown className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-red-700 font-medium">Da Pagare</p>
              <p className="text-xs text-red-600">{fattureNonPagate.length} fatture</p>
            </div>
          </div>
          <p className="text-3xl font-bold text-red-900">
            €{totaleDaPagare.toFixed(2)}
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Previsione Flussi di Cassa</h2>
        <div className="space-y-3">
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">Liquidità attuale:</span>
            <span className="font-medium text-green-600">€{totaleLiquidita.toFixed(2)}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">Fatture da pagare:</span>
            <span className="font-medium text-red-600">-€{totaleDaPagare.toFixed(2)}</span>
          </div>
          <div className="flex justify-between py-3 bg-gray-50 rounded-lg px-4">
            <span className="font-bold text-gray-900">Liquidità prevista dopo pagamenti:</span>
            <span className={`font-bold text-lg ${
              (totaleLiquidita - totaleDaPagare) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              €{(totaleLiquidita - totaleDaPagare).toFixed(2)}
            </span>
          </div>
        </div>

        {(totaleLiquidita - totaleDaPagare) < 0 && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">
              <strong>Attenzione:</strong> La liquidità prevista è negativa. 
              Sarà necessario integrare liquidità prima di pagare tutte le fatture.
            </p>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Fatture Non Pagate ({fattureNonPagate.length})
        </h2>
        {fattureNonPagate.length === 0 ? (
          <p className="text-center text-gray-500 py-8">Nessuna fattura da pagare</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Numero</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Fornitore</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Data</th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Importo</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {fattureNonPagate.map((f) => (
                  <tr key={f.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">{f.numero_fattura}</td>
                    <td className="px-4 py-3 text-sm">{f.ragione_sociale_fornitore}</td>
                    <td className="px-4 py-3 text-sm">{new Date(f.data_fattura).toLocaleDateString()}</td>
                    <td className="px-4 py-3 text-sm text-right font-medium">€{f.totale?.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
