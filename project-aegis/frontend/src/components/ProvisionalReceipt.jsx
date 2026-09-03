import { useEffect, useState } from 'react'
import { useTransactionPoller } from '../hooks/useTelemetry'

/**
 * Project Aegis -- Provisional Receipt Component
 *
 * Shows the victim a "Payment Successful" screen regardless of
 * the actual backend status (asymmetric deception).
 *
 * Polls the backend for status changes. If the co-signer reverses
 * the transaction, the UI quietly transitions to "Transfer Cancelled".
 */
export default function ProvisionalReceipt({ transaction, onReset }) {
  const { status: polledStatus } = useTransactionPoller(
    transaction?.transaction_id,
    2500
  )

  const [displayState, setDisplayState] = useState('success')

  useEffect(() => {
    if (polledStatus === 'REVERSED') {
      // Small delay before showing reversal (feels more natural)
      const timer = setTimeout(() => {
        setDisplayState('reversed')
      }, 800)
      return () => clearTimeout(timer)
    }
  }, [polledStatus])

  const formatCurrency = (val) => {
    return parseFloat(val).toLocaleString('en-IN')
  }

  const formatDate = () => {
    return new Date().toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (displayState === 'reversed') {
    return (
      <div className="text-center py-8">
        {/* Reversed State */}
        <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-aegis-offwhite border border-aegis-border flex items-center justify-center">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#666666" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </div>

        <h2 className="text-lg font-semibold text-aegis-black mb-1">
          Transfer Cancelled
        </h2>
        <p className="text-sm text-aegis-gray mb-6">
          Your transfer was reversed by your trusted contact.
        </p>

        <div className="card p-4 text-left space-y-3 mb-6">
          <div className="flex justify-between">
            <span className="text-label">Amount</span>
            <span className="text-sm font-medium text-aegis-black">
              INR {formatCurrency(transaction.amount)}
            </span>
          </div>
          <div className="divider" />
          <div className="flex justify-between">
            <span className="text-label">Receiver</span>
            <span className="text-sm text-aegis-black">{transaction.receiver}</span>
          </div>
          <div className="divider" />
          <div className="flex justify-between">
            <span className="text-label">Status</span>
            <span className="badge badge-neutral">Cancelled</span>
          </div>
          <div className="divider" />
          <div className="flex justify-between">
            <span className="text-label">Reference</span>
            <span className="text-sm text-mono text-aegis-gray">
              {transaction.transaction_id}
            </span>
          </div>
        </div>

        <button onClick={onReset} className="btn-outline">
          New Transfer
        </button>
      </div>
    )
  }

  return (
    <div className="text-center py-8">
      {/* Success State (shown for both genuine SUCCESS and deceptive ESCROW_LIEN) */}
      <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-green-50 flex items-center justify-center">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#1B7A3D" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </div>

      <h2 className="text-lg font-semibold text-aegis-black mb-1">
        Payment Successful
      </h2>
      <p className="text-3xl font-bold text-aegis-black mt-3 mb-1">
        INR {formatCurrency(transaction.amount)}
      </p>
      <p className="text-sm text-aegis-gray mb-6">
        {formatDate()}
      </p>

      <div className="card p-4 text-left space-y-3 mb-6">
        <div className="flex justify-between">
          <span className="text-label">Receiver</span>
          <span className="text-sm text-aegis-black">{transaction.receiver}</span>
        </div>
        <div className="divider" />
        <div className="flex justify-between">
          <span className="text-label">Status</span>
          <span className="badge badge-success">Completed</span>
        </div>
        <div className="divider" />
        <div className="flex justify-between">
          <span className="text-label">Transaction ID</span>
          <span className="text-sm text-mono text-aegis-gray">
            {transaction.transaction_id}
          </span>
        </div>
        <div className="divider" />
        <div className="flex justify-between">
          <span className="text-label">Reference</span>
          <span className="text-xs text-aegis-midgray">
            Transaction reference generated
          </span>
        </div>
      </div>

      <button onClick={onReset} className="btn-outline">
        New Transfer
      </button>
    </div>
  )
}
