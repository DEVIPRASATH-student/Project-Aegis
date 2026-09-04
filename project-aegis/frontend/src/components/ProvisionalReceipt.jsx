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
        <div className="w-14 h-14 mx-auto mb-4 rounded-full bg-white/10 border border-white/20 flex items-center justify-center shadow-lg backdrop-blur-sm">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </div>

        <h2 className="text-xl font-semibold text-white mb-1">
          Transfer Cancelled
        </h2>
        <p className="text-sm text-white/80 mb-6">
          Your transfer was reversed by your trusted contact.
        </p>

        <div className="card bg-white/95 backdrop-blur-sm border border-white/20 shadow-2xl p-5 text-left space-y-3 mb-6 rounded-lg">
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

        <button
          onClick={onReset}
          className="btn-outline !bg-white/10 !text-white !border-white/30 hover:!bg-white/20 transition-all shadow-md px-6 py-2.5"
        >
          New Transfer
        </button>
      </div>
    )
  }

  return (
    <div className="text-center py-8">
      {/* Success State (shown for both genuine SUCCESS and deceptive ESCROW_LIEN) */}
      <div className="w-14 h-14 mx-auto mb-4 rounded-full bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center shadow-lg backdrop-blur-sm">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </div>

      <h2 className="text-2xl font-bold text-white mb-1 tracking-tight">
        Payment Successful
      </h2>
      <p className="text-4xl font-extrabold text-white mt-3 mb-1 tracking-tight">
        INR {formatCurrency(transaction.amount)}
      </p>
      <p className="text-sm text-cyan-100/70 mb-6">
        {formatDate()}
      </p>

      <div className="card bg-white/95 backdrop-blur-sm border border-white/20 shadow-2xl p-5 text-left space-y-3 mb-6 rounded-lg">
        <div className="flex justify-between">
          <span className="text-label">Receiver</span>
          <span className="text-sm font-medium text-aegis-black">{transaction.receiver}</span>
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

      <button
        onClick={onReset}
        className="btn-outline !bg-white/10 !text-white !border-white/30 hover:!bg-white/20 transition-all shadow-md px-6 py-2.5"
      >
        New Transfer
      </button>
    </div>
  )
}
