// Dashboard HR principale
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Users, FileText, DollarSign, Calendar, 
  AlertTriangle, TrendingUp, Clock, CheckCircle 
} from 'lucide-react';

const HRDashboard = () => {
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadStatistics();
  }, []);
  
  const loadStatistics = async () => {
    try {
      const response = await fetch('/api/hr/statistics', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setStatistics(data);
    } catch (error) {
      console.error('Errore caricamento statistiche:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Caricamento...</div>;
  
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Dashboard HR</h1>
      
      {/* Cards Statistiche */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatCard
          title="Dipendenti Attivi"
          value={statistics?.dipendenti_attivi || 0}
          icon={<Users className="w-8 h-8 text-blue-500" />}
          trend="+2 questo mese"
        />
        
        <StatCard
          title="Buste Paga da Pagare"
          value={statistics?.buste_paga_da_pagare || 0}
          icon={<FileText className="w-8 h-8 text-orange-500" />}
          alert={statistics?.buste_paga_da_pagare > 0}
        />
        
        <StatCard
          title="Importo da Pagare"
          value={`€${(statistics?.importo_da_pagare || 0).toLocaleString()}`}
          icon={<DollarSign className="w-8 h-8 text-green-500" />}
        />
        
        <StatCard
          title="Richieste Ferie"
          value={statistics?.richieste_ferie_pendenti || 0}
          icon={<Calendar className="w-8 h-8 text-purple-500" />}
          alert={statistics?.richieste_ferie_pendenti > 5}
        />
      </div>
      
      {/* Alert Azioni Richieste */}
      {statistics?.buste_paga_da_pagare > 0 && (
        <Alert className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Ci sono {statistics.buste_paga_da_pagare} buste paga da pagare per un totale di €
            {statistics.importo_da_pagare.toLocaleString()}
          </AlertDescription>
        </Alert>
      )}
      
      {/* Sezioni Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Azioni Rapide</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full" variant="outline" onClick={() => window.location.href = '/hr/employees/new'}>
              <Users className="w-4 h-4 mr-2" />
              Nuovo Dipendente
            </Button>
            
            <Button className="w-full" variant="outline" onClick={() => window.location.href = '/hr/payslips/import'}>
              <FileText className="w-4 h-4 mr-2" />
              Import Buste Paga
            </Button>
            
            <Button className="w-full" variant="outline" onClick={() => runEmailBot()}>
              <Clock className="w-4 h-4 mr-2" />
              Esegui Email Bot
            </Button>
            
            <Button className="w-full" variant="outline" onClick={() => window.location.href = '/hr/contracts/new'}>
              <FileText className="w-4 h-4 mr-2" />
              Genera Contratto
            </Button>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Ultime Attività</CardTitle>
          </CardHeader>
          <CardContent>
            <RecentActivities />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, trend, alert }) => (
  <Card className={alert ? 'border-orange-500' : ''}>
    <CardContent className="pt-6">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold mt-2">{value}</p>
          {trend && (
            <p className="text-sm text-gray-500 mt-1">{trend}</p>
          )}
        </div>
        {icon}
      </div>
    </CardContent>
  </Card>
);

const RecentActivities = () => {
  return (
    <div className="space-y-3">
      <ActivityItem
        icon={<CheckCircle className="w-4 h-4 text-green-500" />}
        text="Busta paga Marzo 2024 inviata"
        time="2 ore fa"
      />
      <ActivityItem
        icon={<Users className="w-4 h-4 text-blue-500" />}
        text="Nuovo dipendente: Mario Rossi"
        time="1 giorno fa"
      />
      <ActivityItem
        icon={<FileText className="w-4 h-4 text-purple-500" />}
        text="Contratto firmato: Luigi Verdi"
        time="2 giorni fa"
      />
    </div>
  );
};

const ActivityItem = ({ icon, text, time }) => (
  <div className="flex items-center space-x-3 text-sm">
    {icon}
    <div className="flex-1">
      <p>{text}</p>
      <p className="text-gray-500 text-xs">{time}</p>
    </div>
  </div>
);

const runEmailBot = async () => {
  try {
    const response = await fetch('/api/hr/email-bot/run', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    const data = await response.json();
    alert(`Email Bot: ${data.imported} importate, ${data.skipped} skippate`);
  } catch (error) {
    alert('Errore esecuzione email bot');
  }
};

export default HRDashboard;
