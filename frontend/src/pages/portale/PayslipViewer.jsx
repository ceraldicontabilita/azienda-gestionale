// Componente visualizzazione busta paga con accettazione obbligatoria
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, Download, AlertTriangle, Clock, 
  CheckCircle, XCircle, Calendar 
} from 'lucide-react';

const PayslipViewer = ({ payslipId }) => {
  const [payslip, setPayslip] = useState(null);
  const [accepted, setAccepted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showPDF, setShowPDF] = useState(false);
  
  useEffect(() => {
    loadPayslip();
  }, [payslipId]);
  
  const loadPayslip = async () => {
    try {
      const response = await fetch(`/api/portale/buste-paga/${payslipId}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setPayslip(data);
      setAccepted(data.accettato);
    } catch (error) {
      console.error('Errore caricamento busta paga:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAccept = async () => {
    try {
      await fetch(`/api/portale/buste-paga/${payslipId}/accetta`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ accetto: true })
      });
      
      setAccepted(true);
      alert('Busta paga accettata correttamente');
      loadPayslip();
    } catch (error) {
      alert('Errore accettazione');
    }
  };
  
  const downloadPDF = async () => {
    if (!accepted) {
      alert('Devi prima accettare la busta paga');
      return;
    }
    
    window.open(`/api/portale/buste-paga/${payslipId}/download-pdf`, '_blank');
  };
  
  const downloadModuloContestazione = async () => {
    if (payslip.contestazione_scaduta) {
      alert('Termine di contestazione scaduto');
      return;
    }
    
    window.open(`/api/portale/buste-paga/${payslipId}/download-modulo-contestazione`, '_blank');
  };
  
  const openContestazione = () => {
    if (payslip.contestazione_scaduta) {
      alert('Termine di contestazione scaduto');
      return;
    }
    
    window.location.href = `/portale/buste-paga/${payslipId}/contesta`;
  };
  
  if (loading) return <div>Caricamento...</div>;
  if (!payslip) return <div>Busta paga non trovata</div>;
  
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Busta Paga {payslip.periodo}</h1>
          <p className="text-gray-600">
            Visualizzata {payslip.numero_visualizzazioni} volte
          </p>
        </div>
        
        <Badge variant={payslip.stato_pagamento === 'pagato' ? 'success' : 'warning'}>
          {payslip.stato_pagamento === 'pagato' ? 'Pagata' : 'Da Pagare'}
        </Badge>
      </div>
      
      {/* Alert Scadenza Contestazione */}
      {payslip.messaggio_scadenza && (
        <Alert className={payslip.contestazione_scaduta ? 'border-red-500' : 'border-yellow-500'} variant={payslip.contestazione_scaduta ? 'destructive' : 'warning'}>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription className="whitespace-pre-line">
            {payslip.messaggio_scadenza}
          </AlertDescription>
        </Alert>
      )}
      
      {/* Info Date */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Data Disponibilità</p>
              <p className="font-semibold">
                {new Date(payslip.data_disponibilita).toLocaleDateString('it-IT')}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Scadenza Contestazione</p>
              <p className="font-semibold">
                {new Date(payslip.data_scadenza_contestazione).toLocaleDateString('it-IT')}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Giorni Rimanenti</p>
              <p className={`font-semibold ${payslip.giorni_rimanenti_contestazione <= 30 ? 'text-orange-500' : ''} ${payslip.contestazione_scaduta ? 'text-red-500' : ''}`}>
                {payslip.contestazione_scaduta ? 'Scaduto' : `${payslip.giorni_rimanenti_contestazione} giorni`}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Dati Busta Paga */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Dettagli Busta Paga</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <DetailRow label="Retribuzione Lorda" value={`€${payslip.retribuzione_lorda.toLocaleString()}`} />
            <DetailRow label="INPS Dipendente" value={`€${payslip.inps_dipendente.toLocaleString()}`} />
            <DetailRow label="IRPEF" value={`€${payslip.irpef.toLocaleString()}`} />
            <hr />
            <DetailRow 
              label="Netto in Busta" 
              value={`€${payslip.netto_in_busta.toLocaleString()}`}
              bold 
            />
          </div>
        </CardContent>
      </Card>
      
      {/* PDF Viewer */}
      {payslip.pdf_disponibile && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Documento PDF</CardTitle>
          </CardHeader>
          <CardContent>
            {showPDF ? (
              <iframe
                src={`/api/portale/buste-paga/${payslipId}/preview-pdf`}
                className="w-full h-96 border rounded"
              />
            ) : (
              <Button onClick={() => setShowPDF(true)} variant="outline">
                <FileText className="w-4 h-4 mr-2" />
                Visualizza PDF
              </Button>
            )}
          </CardContent>
        </Card>
      )}
      
      {/* Checkbox Accettazione */}
      {!accepted && (
        <Card className="mb-6 border-blue-500">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-3">
              <Checkbox
                checked={accepted}
                onChange={(e) => setAccepted(e.target.checked)}
                className="mt-1"
              />
              <div>
                <p className="font-medium">
                  Dichiaro di aver letto la busta paga
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  Ho 180 giorni dalla data di disponibilità ({new Date(payslip.data_disponibilita).toLocaleDateString('it-IT')}) 
                  per contestare eventuali anomalie. Decorso tale termine, la busta paga si intende accettata tacitamente.
                </p>
              </div>
            </div>
            
            <Button 
              onClick={handleAccept} 
              disabled={!accepted}
              className="w-full mt-4"
            >
              <CheckCircle className="w-4 h-4 mr-2" />
              Confermo di Aver Letto
            </Button>
          </CardContent>
        </Card>
      )}
      
      {/* Pulsanti Azioni */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Button 
          onClick={downloadPDF}
          disabled={!accepted}
          variant="default"
        >
          <Download className="w-4 h-4 mr-2" />
          Scarica PDF
        </Button>
        
        <Button 
          onClick={downloadModuloContestazione}
          disabled={payslip.contestazione_scaduta}
          variant="outline"
        >
          <FileText className="w-4 h-4 mr-2" />
          Modulo Contestazione
        </Button>
        
        <Button 
          onClick={openContestazione}
          disabled={payslip.contestazione_scaduta}
          variant="outline"
        >
          <AlertTriangle className="w-4 h-4 mr-2" />
          Contesta Busta Paga
        </Button>
      </div>
      
      {/* Contestazioni Esistenti */}
      {payslip.ha_contestazioni && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Contestazioni Presentate ({payslip.numero_contestazioni})</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              Hai già presentato {payslip.numero_contestazioni} contestazione/i per questa busta paga.
            </p>
            <Button 
              variant="link" 
              onClick={() => window.location.href = `/portale/buste-paga/${payslipId}/contestazioni`}
            >
              Visualizza contestazioni →
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

const DetailRow = ({ label, value, bold }) => (
  <div className="flex justify-between">
    <span className={`text-gray-600 ${bold ? 'font-semibold' : ''}`}>{label}</span>
    <span className={bold ? 'font-bold text-lg' : ''}>{value}</span>
  </div>
);

export default PayslipViewer;
