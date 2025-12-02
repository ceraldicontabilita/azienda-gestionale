import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Archive from './pages/Archive';
import Suppliers from './pages/Suppliers';
import CashRegister from './pages/CashRegister';
import Checks from './pages/Checks';
import Employees from './pages/Employees';
import HACCP from './pages/HACCP';
import IVA from './pages/IVA';
import Warehouse from './pages/Warehouse';
import Reconciliation from './pages/Reconciliation';
import Treasury from './pages/Treasury';
import Analytics from './pages/Analytics';
import Documents from './pages/Documents';
import Settings from './pages/Settings';
import BulkImport from './pages/BulkImport';

function PrivateRoute({ children }) {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/archive" element={<Archive />} />
                  <Route path="/suppliers" element={<Suppliers />} />
                  <Route path="/cash-register" element={<CashRegister />} />
                  <Route path="/checks" element={<Checks />} />
                  <Route path="/employees" element={<Employees />} />
                  <Route path="/haccp" element={<HACCP />} />
                  <Route path="/iva" element={<IVA />} />
                  <Route path="/warehouse" element={<Warehouse />} />
                  <Route path="/reconciliation" element={<Reconciliation />} />
                  <Route path="/treasury" element={<Treasury />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/documents" element={<Documents />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/bulk-import" element={<BulkImport />} />
                </Routes>
              </Layout>
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
