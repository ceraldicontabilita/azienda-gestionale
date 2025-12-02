import React from 'react'
import { Settings } from 'lucide-react'

export default function Impostazioni() {
  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  const user = JSON.parse(localStorage.getItem('user') || '{}')

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Impostazioni</h1>

      <div className="bg-white rounded-lg shadow p-6 mb-4">
        <h2 className="font-bold mb-4">Account</h2>
        <div className="space-y-2">
          <p><span className="font-medium">Email:</span> {user.email}</p>
          <p><span className="font-medium">Ragione Sociale:</span> {user.ragione_sociale}</p>
          <p><span className="font-medium">P.IVA:</span> {user.partita_iva}</p>
        </div>
      </div>

      <button onClick={handleLogout} className="btn-danger">
        Logout
      </button>
    </div>
  )
}
