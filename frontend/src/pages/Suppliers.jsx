import React, { useState, useEffect } from 'react';
import { Building2, Phone, Mail, MapPin, Plus, Edit, Trash2, TrendingUp, FileText, AlertCircle } from 'lucide-react';

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState(null);
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState(null);
  const [supplierStats, setSupplierStats] = useState(null);
  const [supplierInvoices, setSupplierInvoices] = useState([]);
  const [activeTab, setActiveTab] = useState('stats');
  const [formData, setFormData] = useState({
    partita_iva: '',
    ragione_sociale: '',
    email: '',
    telefono: '',
    indirizzo: '',
    citta: '',
    cap: '',
    metodo_pagamento: 'banca'
  });

  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const fetchSuppliers = async () => {
    try {
      const response = await fetch(`http://localhost:8001/suppliers/?id_utente=${user.id}`);
      const data = await response.json();
      setSuppliers(data.data || []);
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
      const url = editingSupplier
        ? `http://localhost:8001/suppliers/${editingSupplier.partita_iva}?id_utente=${user.id}`
        : 'http://localhost:8001/suppliers/';

      const response = await fetch(url, {
        method: editingSupplier ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formDataToSend
      });

      if (response.ok) {
        setShowModal(false);
        setEditingSupplier(null);
        setFormData({
          partita_iva: '',
          ragione_sociale: '',
          email: '',
          telefono: '',
          indirizzo: '',
          citta: '',
          cap: '',
          metodo_pagamento: 'banca'
        });
        fetchSuppliers();
      }
    } catch (error) {
      console.error('Errore:', error);
    }
  };

  const handleDelete = async (piva) => {
    if (!confirm('Sicuro di voler eliminare questo fornitore?')) return;

    try {
      const response = await fetch(
        `http://localhost:8001/suppliers/${piva}?id_utente=${user.id}&force=true`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        fetchSuppliers();
      }
    } catch (error) {
      console.error('Errore:', error);
    }
  };

  const openStatsModal = async (supplier) => {
    setSelectedSupplier(supplier);
    setShowStatsModal(true);
    setActiveTab('stats');
    
    try {
      const [statsRes, invoicesRes] = await Promise.all([
        fetch(`http://localhost:8001/suppliers/${supplier.partita_iva}/stats?id_utente=${user.id}`),
        fetch(`http://localhost:8001/suppliers/${supplier.partita_iva}/fatture?id_utente=${user.id}`)
      ]);
      
      const statsData = await statsRes.json();
      const invoicesData = await invoicesRes.json();
      
      setSupplierStats(statsData.data);
      setSupplierInvoices(invoicesData.data || []);
    } catch (error) {
      console.error('Errore:', error);
    }
  };

  const openEditModal = (supplier) => {
    setEditingSupplier(supplier);
    setFormData({
      partita_iva: supplier.partita_iva,
      ragione_sociale: supplier.ragione_sociale,
      email: supplier.email || '',
      telefono: supplier.telefono || '',
      indirizzo: supplier.indirizzo || '',
      citta: supplier.citta || '',
      cap: supplier.cap || '',
      metodo_pagamento: supplier.metodo_pagamento || 'banca'
    });
    setShowModal(true);
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="text-gray-500">Caricamento...</div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Fornitori</h1>
          <p className="text-gray-600 mt-1">{suppliers.length} fornitori attivi</p>
        </div>
        <button
          onClick={() => {
            setEditingSupplier(null);
            setShowModal(true);
          }}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          Nuovo Fornitore
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {suppliers.map((supplier) => (
          <div key={supplier.partita_iva} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{supplier.ragione_sociale}</h3>
                  <p className="text-sm text-gray-500">P.IVA: {supplier.partita_iva}</p>
                </div>
              </div>
            </div>

            <div className="space-y-2 text-sm">
              {supplier.email && (
                <div className="flex items-center gap-2 text-gray-600">
                  <Mail className="w-4 h-4" />
                  {supplier.email}
                </div>
              )}
              {supplier.telefono && (
                <div className="flex items-center gap-2 text-gray-600">
                  <Phone className="w-4 h-4" />
                  {supplier.telefono}
                </div>
              )}
              {supplier.citta && (
                <div className="flex items-center gap-2 text-gray-600">
                  <MapPin className="w-4 h-4" />
                  {supplier.citta}
                </div>
              )}
            </div>

            <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                {supplier.metodo_pagamento || 'N/D'}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => openStatsModal(supplier)}
                  className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                  title="Statistiche"
                >
                  <TrendingUp className="w-4 h-4" />
                </button>
                <button
                  onClick={() => openEditModal(supplier)}
                  className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(supplier.partita_iva)}
                  className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {showStatsModal && selectedSupplier && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">{selectedSupplier.ragione_sociale}</h2>
              <button
                onClick={() => setShowStatsModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <div className="flex gap-2 mb-6 border-b border-gray-200">
              <button
                onClick={() => setActiveTab('stats')}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === 'stats'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Statistiche
              </button>
              <button
                onClick={() => setActiveTab('invoices')}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === 'invoices'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Fatture ({supplierInvoices.length})
              </button>
            </div>

            {activeTab === 'stats' && supplierStats && (
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Fatture Totali</p>
                  <p className="text-3xl font-bold text-blue-600">{supplierStats.totale_fatture || 0}</p>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Importo Totale</p>
                  <p className="text-3xl font-bold text-green-600">
                    €{(supplierStats.importo_totale || 0).toFixed(2)}
                  </p>
                </div>
                <div className="bg-yellow-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Fatture Pagate</p>
                  <p className="text-3xl font-bold text-yellow-600">{supplierStats.fatture_pagate || 0}</p>
                </div>
                <div className="bg-red-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Fatture Da Pagare</p>
                  <p className="text-3xl font-bold text-red-600">{supplierStats.fatture_da_pagare || 0}</p>
                </div>
                {supplierStats.ultima_fattura_data && (
                  <div className="col-span-2 bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">Ultima Fattura</p>
                    <p className="text-lg font-medium text-gray-900">
                      {new Date(supplierStats.ultima_fattura_data).toLocaleDateString()}
                    </p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'invoices' && (
              <div className="space-y-2">
                {supplierInvoices.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">Nessuna fattura trovata</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Numero</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Data</th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Importo</th>
                          <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Stato</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {supplierInvoices.map((invoice) => (
                          <tr key={invoice.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3 text-sm">{invoice.numero_fattura}</td>
                            <td className="px-4 py-3 text-sm">
                              {new Date(invoice.data_fattura).toLocaleDateString()}
                            </td>
                            <td className="px-4 py-3 text-sm text-right font-medium">
                              €{invoice.totale?.toFixed(2)}
                            </td>
                            <td className="px-4 py-3 text-center">
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                invoice.pagata 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {invoice.pagata ? 'Pagata' : 'Da Pagare'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingSupplier ? 'Modifica Fornitore' : 'Nuovo Fornitore'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Partita IVA *
                  </label>
                  <input
                    type="text"
                    required
                    maxLength={11}
                    value={formData.partita_iva}
                    onChange={(e) => setFormData({...formData, partita_iva: e.target.value})}
                    disabled={!!editingSupplier}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Ragione Sociale *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.ragione_sociale}
                    onChange={(e) => setFormData({...formData, ragione_sociale: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Indirizzo</label>
                <input
                  type="text"
                  value={formData.indirizzo}
                  onChange={(e) => setFormData({...formData, indirizzo: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">CAP</label>
                  <input
                    type="text"
                    maxLength={5}
                    value={formData.cap}
                    onChange={(e) => setFormData({...formData, cap: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Città</label>
                  <input
                    type="text"
                    value={formData.citta}
                    onChange={(e) => setFormData({...formData, citta: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Metodo Pagamento</label>
                <select
                  value={formData.metodo_pagamento}
                  onChange={(e) => setFormData({...formData, metodo_pagamento: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="banca">Bonifico Bancario</option>
                  <option value="cassa">Contanti</option>
                  <option value="assegno">Assegno</option>
                  <option value="rid">RID</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingSupplier(null);
                  }}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Annulla
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  {editingSupplier ? 'Aggiorna' : 'Crea'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
