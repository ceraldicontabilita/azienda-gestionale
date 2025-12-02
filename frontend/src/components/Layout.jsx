import React, { useState } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, FileText, Users, Wallet, UsersRound, 
  ClipboardCheck, Building2, FileCheck, GitBranch, Receipt,
  Calculator, Package, Settings, Menu, X, Upload 
} from 'lucide-react'

const menuItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/archive', icon: FileText, label: 'Fatture' },
  { path: '/suppliers', icon: Users, label: 'Fornitori' },
  { path: '/prima-nota-cassa', icon: Wallet, label: 'Prima Nota Cassa' },
  { path: '/gestione-dipendenti', icon: UsersRound, label: 'Dipendenti' },
  { path: '/haccp', icon: ClipboardCheck, label: 'HACCP' },
  { path: '/gestione-bonifici', icon: Building2, label: 'Bonifici' },
  { path: '/gestione-assegni', icon: FileCheck, label: 'Assegni' },
  { path: '/riconciliazione-bancaria', icon: GitBranch, label: 'Riconciliazione' },
  { path: '/gestione-erario', icon: Receipt, label: 'Gestione Erario' },
  { path: '/iva', icon: Calculator, label: 'IVA' },
  { path: '/warehouse', icon: Package, label: 'Magazzino' },
  { path: '/bulk-import', icon: Upload, label: 'Import Massivo' },
  { path: '/impostazioni', icon: Settings, label: 'Impostazioni' },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-white border-r border-gray-200 transition-all duration-300`}>
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          {sidebarOpen && (
            <h1 className="text-xl font-bold text-blue-600">Azienda Cloud</h1>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <nav className="p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon size={20} />
                {sidebarOpen && <span className="text-sm font-medium">{item.label}</span>}
              </Link>
            )
          })}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
