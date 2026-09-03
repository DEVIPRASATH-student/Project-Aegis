import { useState } from 'react'
import { resolveEscrow } from '../api/client'

/**
 * Project Aegis -- Escrow Alert Card Component
 *
 * Displays a protected transaction alert on the co-signer dashboard.
 * Shows risk score, risk factors, and action buttons (Reverse/Approve).
 * Professional security-operations styling with red alert border.
 */
export default function EscrowCard({ transaction, onResolved }) {
  const [resolving, setResolving] = useState(false)
  const [action, setAction] = useState(null)
  const [error, setError] = useState(null)

  const handleResolve = async (decision) => {
    setResolving(true)
    setAction(decision)
    setError(null)
    try {
      await resolveEscrow({
        transactionId: transaction.transaction_id,
        decision,
        resolvedBy: 'co-signer',
      })
      if (onResolved) onResolved(transaction.transaction_id, decision)
    } catch (err) {
      setError(err.message)
      setResolving(false)
      setAction(null)
    }
  }

  const formatCurrency = (val) => {
    return parseFloat(val).toLocaleString('en-IN')
  }

  const timeSince = (dateStr) => {
    if (!dateStr) return ''
    const created = new Date(dateStr)
    const now = new Date()
    const seconds = Math.floor((now - created) / 1000)
    if (seconds < 60) return `${seconds}s ago`
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    return `${hours}h ago`
  }

  const riskFactors = (() => {
    try {
      return JSON.parse(transaction.risk_factors || '[]')
    } catch {
      return []
    }
  })()

  const riskScore = transaction.risk_score || 0
  const riskLevel = transaction.risk_level || 'HIGH'

  return (
    <div className="alert-critical">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-risk-high pulse-dot" />
          <span className="text-xs font-semibold uppercase tracking-wider text-risk-high">
            Emergency -- Suspected APP Fraud
          </span>
        </div>
        <span className="text-2xs text-aegis-gray font-mono">
          {timeSince(transaction.created_at)}
        </span>
      </div>

      {/* Amount */}
      <p className="text-2xl font-bold text-aegis-black mb-1">
        INR {formatCurrency(transaction.amount)}
      </p>
      <p className="text-sm text-aegis-gray mb-4">
        has been temporarily protected.
      </p>

      {/* Details Grid */}
      <div className="grid grid-cols-2 gap-x-6 gap-y-3 mb-4">
        <div>
          <p className="text-label mb-0.5">Victim</p>
          <p className="text-sm font-medium text-aegis-black">
            {transaction.sender === 'A' ? 'Dad' : transaction.sender}
          </p>
        </div>
        <div>
          <p className="text-label mb-0.5">Receiver</p>
          <p className="text-sm font-medium text-aegis-black">
            {transaction.receiver === 'B' ? 'XXXX 4821' : transaction.receiver}
          </p>
        </div>
        <div>
          <p className="text-label mb-0.5">Risk Score</p>
          <p className="text-sm font-bold text-risk-high">
            {Math.round(riskScore)} / 100
          </p>
        </div>
        <div>
          <p className="text-label mb-0.5">Status</p>
          <span className="badge badge-warning">Escrow Lien</span>
        </div>
      </div>

      {/* Risk Factors */}
      {riskFactors.length > 0 && (
        <div className="mb-4">
          <p className="text-label mb-2">Risk Factors</p>
          <ul className="space-y-1.5">
            {riskFactors.map((factor, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-aegis-charcoal">
                <span className="text-risk-high mt-0.5 text-xs">--</span>
                {factor}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* CPST Token */}
      {transaction.cpst_token && (
        <div className="mb-4 p-2.5 bg-white rounded border border-aegis-border">
          <p className="text-2xs text-aegis-midgray uppercase tracking-wider mb-0.5">
            Provisional Settlement Token
          </p>
          <p className="text-sm text-mono font-medium text-aegis-black">
            {transaction.cpst_token}
          </p>
        </div>
      )}

      {/* Error */}
      {error && (
        <p className="text-sm text-risk-high mb-3">{error}</p>
      )}

      {/* Actions */}
      <div className="flex gap-3 mt-4">
        <button
          className="btn-danger flex-1 py-2.5"
          onClick={() => handleResolve('REVERSED')}
          disabled={resolving}
        >
          {resolving && action === 'REVERSED' ? 'Reversing...' : 'Reverse Transaction'}
        </button>
        <button
          className="btn-outline flex-1 py-2.5"
          onClick={() => handleResolve('SUCCESS')}
          disabled={resolving}
        >
          {resolving && action === 'SUCCESS' ? 'Approving...' : 'Approve Transaction'}
        </button>
      </div>
    </div>
  )
}
