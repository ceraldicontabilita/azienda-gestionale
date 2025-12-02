import React, { useState, useEffect } from 'react'
import { TrendingUp, Users, AlertTriangle, DollarSign } from 'lucide-react'
import axios from 'axios'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [quickActions, setQuickActions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [statsRes, actionsRes] = await Promise.all([
        axios.get('/api/dashboard/stats', { params: { id_utente: 1 } }),
        axios.get('/api/dashboard/quick-actions', { params: { id_utente: 1 } })
      ])

      setStats(statsRes.data.data)
      setQuickActions(actionsRes.data.data)
    } catch (error) {
      console.error('Errore caricamento dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Caricamento...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Panoramica generale dell'attività</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Fatture Mese */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Fatture Mese</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">
                €{stats?.fatture_mese?.totale?.toLocaleString('it-IT', { minimumFractionDigits: 2 }) || '0.00'}
              </p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <TrendingUp className="text-blue-600" size={24} />
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-4">{stats?.fatture_mese?.mese}</p>
        </div>

        {/* Fornitori */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Fornitori Attivi</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">
                {stats?.fornitori?.totale || 0}
              </p>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <Users className="text-green-600" size={24} />
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-4">Totale</p>
        </div>

        {/* Fatture da Pagare */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Da Pagare</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">
                €{stats?.fatture_da_pagare?.importo?.toLocaleString('it-IT', { minimumFractionDigits: 2 }) || '0.00'}
              </p>
            </div>
            <div className="p-3 bg-orange-50 rounded-lg">
              <AlertTriangle className="text-orange-600" size={24} />
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-4">
            {stats?.fatture_da_pagare?.numero || 0} fatture
          </p>
        </div>

        {/* Saldo Cassa */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Saldo Cassa</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">
                €{stats?.saldo_cassa?.toLocaleString('it-IT', { minimumFractionDigits: 2 }) || '0.00'}
              </p>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <DollarSign className="text-purple-600" size={24} />
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-4">Attuale</p>
        </div>
      </div>

      {/* Quick Actions */}
      {quickActions && quickActions.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Azioni Rapide</h2>
          <div className="space-y-3">
            {quickActions.map((action, index) => (
              <div
                key={index}
                className={`flex items-start gap-4 p-4 rounded-lg border ${
                  action.priorita === 'alta'
                    ? 'border-red-200 bg-red-50'
                    : action.priorita === 'media'
                    ? 'border-yellow-200 bg-yellow-50'
                    : 'border-blue-200 bg-blue-50'
                }`}
              >
                <AlertTriangle
                  className={
                    action.priorita === 'alta'
                      ? 'text-red-600'
                      : action.priorita === 'media'
                      ? 'text-yellow-600'
                      : 'text-blue-600'
                  }
                  size={20}
                />
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{action.titolo}</h3>
                  <p className="text-sm text-gray-600 mt-1">{action.descrizione}</p>
                </div>
                <button
                  onClick={() => (window.location.href = action.azione)}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                >
                  Visualizza
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Chart Area - Da implementare con Recharts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Andamento Fatture</h2>
          <div className="h-64 flex items-center justify-center text-gray-400">
            Grafico in sviluppo
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Categorie Spese</h2>
          <div className="h-64 flex items-center justify-center text-gray-400">
            Grafico in sviluppo
          </div>
        </div>
      </div>
    </div>
  )
}
