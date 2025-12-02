import React, { useState, useEffect } from 'react';
import { User, Building2, Key, Bell, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Settings() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');
  const navigate = useNavigate();

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogout = () => {
    if (confirm('Sicuro di voler uscire?')) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      navigate('/login');
    }
  };

  if (!user) return <div className="flex justify-center items-center h-64">Caricamento...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Impostazioni</h1>

      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('profile')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'profile'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Profilo
        </button>
        <button
          onClick={() => setActiveTab('company')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'company'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Azienda
        </button>
        <button
          onClick={() => setActiveTab('security')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'security'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Sicurezza
        </button>
      </div>

      {activeTab === 'profile' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6">
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-10 h-10 text-blue-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{user.email}</h2>
              <p className="text-gray-600">Amministratore</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={user.email}
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            <LogOut className="w-5 h-5" />
            Logout
          </button>
        </div>
      )}

      {activeTab === 'company' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-4">
          <div className="flex items-center gap-3 mb-4">
            <Building2 className="w-8 h-8 text-purple-600" />
            <h2 className="text-xl font-bold text-gray-900">Informazioni Azienda</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ragione Sociale</label>
              <input
                type="text"
                value={user.ragione_sociale || ''}
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Partita IVA</label>
              <input
                type="text"
                value={user.partita_iva || ''}
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'security' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-4">
          <div className="flex items-center gap-3 mb-4">
            <Key className="w-8 h-8 text-orange-600" />
            <h2 className="text-xl font-bold text-gray-900">Sicurezza</h2>
          </div>

          <div className="space-y-4">
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-800">
                <strong>✓</strong> Il tuo account è protetto con autenticazione JWT
              </p>
            </div>

            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Info:</strong> Il token di sessione scade dopo 24 ore
              </p>
            </div>

            <button className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors">
              Cambia Password
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
