import React, { useState } from 'react';
import { Upload, FileSpreadsheet, CheckCircle, AlertCircle } from 'lucide-react';

export default function BulkImport() {
  const [activeTab, setActiveTab] = useState('fornitori');
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const handleUpload = async (e, tipo) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('id_utente', user.id);

    try {
      const response = await fetch(`http://localhost:8001/bulk-import/${tipo}`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setResult({
          success: true,
          tipo: tipo,
          ...data
        });
      } else {
        setResult({
          success: false,
          error: data.detail || 'Errore durante import'
        });
      }
    } catch (error) {
      setResult({
        success: false,
        error: error.message
      });
    } finally {
      setUploading(false);
      e.target.value = null;
    }
  };

  const tabs = [
    { id: 'fornitori', label: 'Fornitori', icon: '🏢', description: 'ReportFornitori.xls' },
    { id: 'corrispettivi', label: 'Corrispettivi', icon: '💰', description: 'corrispettivi.xlsx' },
    { id: 'pos', label: 'POS', icon: '💳', description: 'pos.xlsx' },
    { id: 'versamenti', label: 'Versamenti', icon: '🏦', description: 'versamenti.xlsx' }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Import Massivo</h1>
        <p className="text-gray-600 mt-1">Carica file Excel per importare dati in blocco</p>
      </div>

      <div className="flex gap-2 border-b border-gray-200">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => {
              setActiveTab(tab.id);
              setResult(null);
            }}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === tab.id
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="max-w-2xl mx-auto text-center">
          <div className="mb-6">
            <FileSpreadsheet className="w-20 h-20 text-blue-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Import {tabs.find(t => t.id === activeTab)?.label}
            </h2>
            <p className="text-gray-600">
              Formato file: <span className="font-mono bg-gray-100 px-2 py-1 rounded">
                {tabs.find(t => t.id === activeTab)?.description}
              </span>
            </p>
          </div>

          <label className={`
            relative flex flex-col items-center justify-center
            border-2 border-dashed rounded-lg p-12 cursor-pointer
            transition-colors
            ${uploading 
              ? 'border-gray-300 bg-gray-50 cursor-not-allowed' 
              : 'border-blue-300 hover:border-blue-500 hover:bg-blue-50'
            }
          `}>
            <Upload className="w-12 h-12 text-blue-500 mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              {uploading ? 'Caricamento in corso...' : 'Clicca per selezionare il file'}
            </p>
            <p className="text-sm text-gray-500">
              oppure trascina il file qui
            </p>
            <input
              type="file"
              accept=".xlsx,.xls"
              onChange={(e) => handleUpload(e, activeTab)}
              disabled={uploading}
              className="hidden"
            />
          </label>

          {result && (
            <div className={`mt-6 p-6 rounded-lg ${
              result.success 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-red-50 border border-red-200'
            }`}>
              {result.success ? (
                <>
                  <div className="flex items-center justify-center mb-4">
                    <CheckCircle className="w-8 h-8 text-green-600 mr-2" />
                    <h3 className="text-xl font-bold text-green-900">
                      Import Completato!
                    </h3>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-sm text-green-700">Importati</p>
                      <p className="text-3xl font-bold text-green-900">{result.imported}</p>
                    </div>
                    <div>
                      <p className="text-sm text-yellow-700">Saltati</p>
                      <p className="text-3xl font-bold text-yellow-900">{result.skipped}</p>
                    </div>
                    <div>
                      <p className="text-sm text-red-700">Errori</p>
                      <p className="text-3xl font-bold text-red-900">{result.total_errors}</p>
                    </div>
                  </div>
                  {result.errors && result.errors.length > 0 && (
                    <div className="mt-4 p-4 bg-white rounded-lg">
                      <p className="text-sm font-medium text-gray-900 mb-2">
                        Primi {result.errors.length} errori:
                      </p>
                      <ul className="text-xs text-gray-600 text-left space-y-1">
                        {result.errors.map((err, idx) => (
                          <li key={idx}>• {err}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              ) : (
                <>
                  <div className="flex items-center justify-center mb-4">
                    <AlertCircle className="w-8 h-8 text-red-600 mr-2" />
                    <h3 className="text-xl font-bold text-red-900">Errore Import</h3>
                  </div>
                  <p className="text-red-700">{result.error}</p>
                </>
              )}
            </div>
          )}

          <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg text-left">
            <h4 className="font-medium text-blue-900 mb-2">📋 Istruzioni:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              {activeTab === 'fornitori' && (
                <>
                  <li>• Colonne richieste: Partita Iva, Denominazione</li>
                  <li>• Colonne opzionali: Email, Telefono, CAP, Comune, Indirizzo</li>
                  <li>• I fornitori duplicati vengono saltati automaticamente</li>
                </>
              )}
              {activeTab === 'corrispettivi' && (
                <>
                  <li>• Colonne richieste: Data e ora rilevazione, Totale</li>
                  <li>• Le righe con importo 0 vengono saltate</li>
                  <li>• Vengono registrati come movimenti cassa tipo "corrispettivi"</li>
                </>
              )}
              {activeTab === 'pos' && (
                <>
                  <li>• Colonne richieste: DATA, IMPORTO</li>
                  <li>• Gli importi vengono registrati come negativi (uscita da cassa)</li>
                  <li>• Le righe senza importo vengono saltate</li>
                </>
              )}
              {activeTab === 'versamenti' && (
                <>
                  <li>• Colonne richieste: DATA, IMPORTO</li>
                  <li>• Gli importi vengono registrati come negativi (uscita da cassa)</li>
                  <li>• Le righe senza importo vengono saltate</li>
                </>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
