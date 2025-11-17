import { useState, useEffect, useRef } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Clock, X } from 'lucide-react';
import { invoicesAPI } from '../services/api';

const StatusBadge = ({ status }) => {
  const styles = {
    completed: 'bg-green-100 text-green-800',
    pending_approval: 'bg-orange-100 text-orange-800',
    pending_clarification: 'bg-red-100 text-red-800',
    processing: 'bg-blue-100 text-blue-800',
  };

  const labels = {
    completed: 'Completed',
    pending_approval: 'Pending Approval',
    pending_clarification: 'Needs Clarification',
    processing: 'Processing',
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
      {labels[status] || status}
    </span>
  );
};

const InvoiceCard = ({ invoice, onClick }) => (
  <div
    onClick={() => onClick(invoice)}
    className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
  >
    <div className="flex items-start justify-between mb-3">
      <div className="flex items-center">
        <div className="p-2 bg-primary-50 rounded-lg mr-3">
          <FileText className="w-5 h-5 text-primary-600" />
        </div>
        <div>
          <h4 className="font-semibold text-gray-900">{invoice.invoice_number}</h4>
          <p className="text-sm text-gray-600">Supplier ID: {invoice.supplier_id}</p>
        </div>
      </div>
      <StatusBadge status={invoice.processing_status} />
    </div>

    <div className="grid grid-cols-3 gap-4 mb-3">
      <div>
        <p className="text-xs text-gray-500">Amount</p>
        <p className="font-semibold text-gray-900">
          ${invoice.total_amount.toFixed(2)}
        </p>
      </div>
      <div>
        <p className="text-xs text-gray-500">Confidence</p>
        <p className="font-semibold text-gray-900">
          {(invoice.confidence_score * 100).toFixed(0)}%
        </p>
      </div>
      <div>
        <p className="text-xs text-gray-500">Status</p>
        <p className="font-semibold text-gray-900">
          {invoice.is_touchless ? (
            <span className="text-green-600">Touchless</span>
          ) : (
            <span className="text-orange-600">Manual</span>
          )}
        </p>
      </div>
    </div>

    {invoice.po_number && (
      <div className="flex items-center text-sm text-gray-600">
        <CheckCircle className="w-4 h-4 mr-1 text-green-600" />
        PO: {invoice.po_number}
      </div>
    )}
  </div>
);

export default function Inbox() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      setLoading(true);
      const response = await invoicesAPI.list();
      setInvoices(response.data);
    } catch (error) {
      console.error('Failed to load invoices:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setUploading(true);
      await invoicesAPI.upload(file);
      await loadInvoices();
      alert('Invoice uploaded and processed successfully!');
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload invoice');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const pendingInvoices = invoices.filter(
    (inv) => inv.processing_status === 'pending_clarification' || inv.processing_status === 'pending_approval'
  );

  const processedInvoices = invoices.filter(
    (inv) => inv.processing_status === 'completed'
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Inbox</h1>
          <p className="text-gray-600 mt-1">
            Upload and manage incoming invoices
          </p>
        </div>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
        >
          <Upload className="w-5 h-5 mr-2" />
          {uploading ? 'Uploading...' : 'Upload Invoice'}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.xml,.png,.jpg,.jpeg"
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Invoices</p>
              <p className="text-2xl font-bold text-gray-900">{invoices.length}</p>
            </div>
            <FileText className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pending Action</p>
              <p className="text-2xl font-bold text-gray-900">{pendingInvoices.length}</p>
            </div>
            <AlertCircle className="w-8 h-8 text-orange-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Processed</p>
              <p className="text-2xl font-bold text-gray-900">{processedInvoices.length}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </div>
      </div>

      {/* Pending Invoices */}
      {pendingInvoices.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Pending Action ({pendingInvoices.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {pendingInvoices.map((invoice) => (
              <InvoiceCard
                key={invoice.id}
                invoice={invoice}
                onClick={setSelectedInvoice}
              />
            ))}
          </div>
        </div>
      )}

      {/* All Invoices */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          All Invoices ({invoices.length})
        </h2>
        {loading ? (
          <div className="text-center py-12 text-gray-500">
            Loading invoices...
          </div>
        ) : invoices.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No invoices yet</p>
            <p className="text-sm text-gray-400">Upload your first invoice to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {invoices.map((invoice) => (
              <InvoiceCard
                key={invoice.id}
                invoice={invoice}
                onClick={setSelectedInvoice}
              />
            ))}
          </div>
        )}
      </div>

      {/* Invoice Detail Modal */}
      {selectedInvoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-900">
                  Invoice Details
                </h3>
                <button
                  onClick={() => setSelectedInvoice(null)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Invoice Number</p>
                    <p className="font-semibold">{selectedInvoice.invoice_number}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Status</p>
                    <StatusBadge status={selectedInvoice.processing_status} />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total Amount</p>
                    <p className="font-semibold">${selectedInvoice.total_amount.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Tax Amount</p>
                    <p className="font-semibold">${selectedInvoice.tax_amount.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Confidence Score</p>
                    <p className="font-semibold">
                      {(selectedInvoice.confidence_score * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Processing Type</p>
                    <p className="font-semibold">
                      {selectedInvoice.is_touchless ? 'Touchless' : 'Manual Review'}
                    </p>
                  </div>
                </div>

                {selectedInvoice.validation_errors && selectedInvoice.validation_errors.length > 0 && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="font-semibold text-red-800 mb-2">Validation Errors:</p>
                    <ul className="list-disc list-inside text-sm text-red-700">
                      {selectedInvoice.validation_errors.map((error, idx) => (
                        <li key={idx}>{error}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="flex gap-3 pt-4">
                  <button className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                    Approve
                  </button>
                  <button className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                    Reject
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
