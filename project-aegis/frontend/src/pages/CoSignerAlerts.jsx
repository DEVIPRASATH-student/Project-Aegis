import { useState, useEffect } from 'react'
import { useEscrowPoller } from '../hooks/useTelemetry'
import { getAllTransactions, resetDemo } from '../api/client'
import EscrowCard from '../components/EscrowCard'
import { GradientBackground } from '@/components/ui/dark-gradient-background'

/**
 * Project Aegis -- Co-Signer Dashboard Page
 *
 * Route: /dashboard
 *
 * This is the trusted co-signer interface styled with the dark gradient
 * background to deliver a high-tech SOC security overview.
 */

const MONITORED_USER = 'A'  // Demo: monitoring Dad's account

export default function CoSignerAlerts() {
  const {
    transactions,
    totalProtected,
    activeAlerts,
    error,
    loading
  } = useEscrowPoller(MONITORED_USER, 2500)

  const [history, setHistory] = useState([])
  const [resolvedIds, setResolvedIds] = useState(new Set())

  // Fetch transaction history periodically
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const result = await getAllTransactions(MONITORED_USER)
        setHistory(result.transactions || [])
      } catch (err) {
        // Silently fail for history
      }
    }
    fetchHistory()
    const timer = setInterval(fetchHistory, 5000)
    return () => clearInterval(timer)
  }, [])

  const handleResolved = (txId, decision) => {
    setResolvedIds(prev => new Set([...prev, txId]))
  }

  const handleDemoReset = async () => {
    try {
      await resetDemo()
      setResolvedIds(new Set())
      setHistory([])
    } catch (err) {
      // Silently fail
    }
  }

  const totalReviewed = history.filter(
    tx => tx.status === 'REVERSED' || (tx.status === 'SUCCESS' && tx.risk_score && tx.risk_score > 40)
  ).length

  const totalProtectedAllTime = history
    .filter(tx => tx.status === 'REVERSED')
    .reduce((sum, tx) => sum + tx.amount, 0)

  const visibleTransactions = transactions.filter(tx => !resolvedIds.has(tx.transaction_id))

  return (
    <GradientBackground className="min-h-screen">
      {/* Header */}
      <header className="bg-black/40 backdrop-blur-md border-b border-white/10 text-white">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-cyan-500/20 border border-cyan-400/40 rounded flex items-center justify-center">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <div>
              <h1 className="text-sm font-semibold text-white tracking-tight">
                Project Aegis
              </h1>
              <p className="text-2xs text-cyan-200/70">
                Trusted Co-Signer Dashboard
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Live indicator */}
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-status-success pulse-dot" />
              <span className="text-2xs text-white/70 font-mono">LIVE</span>
            </div>

            {/* Demo reset */}
            <button
              onClick={handleDemoReset}
              className="text-2xs text-white/40 hover:text-white font-mono transition-colors"
              title="Reset demo state"
            >
              reset
            </button>
          </div>
        </div>
      </header>

      {/* Overview Stats */}
      <div className="max-w-4xl mx-auto px-6 pt-6">
        <div className="bg-white/95 backdrop-blur-md border border-white/20 rounded-lg p-6 shadow-xl">
          <div className="grid grid-cols-3 gap-6">
            <div>
              <p className="text-label mb-1">Protected Funds</p>
              <p className="text-xl font-bold text-aegis-black">
                {totalProtected > 0 ? `INR ${totalProtected.toLocaleString('en-IN')}` : 'INR 0'}
              </p>
            </div>
            <div>
              <p className="text-label mb-1">Active Alerts</p>
              <p className="text-xl font-bold text-aegis-black flex items-center gap-2">
                {activeAlerts}
                {activeAlerts > 0 && (
                  <span className="badge badge-danger text-2xs">ACTION REQUIRED</span>
                )}
              </p>
            </div>
            <div>
              <p className="text-label mb-1">Transactions Reviewed</p>
              <p className="text-xl font-bold text-aegis-black">{totalReviewed}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-6">
        {/* Connection Error */}
        {error && (
          <div className="alert-critical mb-4">
            <p className="text-sm text-red-200">
              Unable to connect to the security layer. Retrying...
            </p>
          </div>
        )}

        {/* Active Escrow Alerts */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
              Active Alerts
            </h2>
            <span className="text-2xs text-cyan-200/60 font-mono">
              Polling every 2.5s
            </span>
          </div>

          {loading && visibleTransactions.length === 0 && (
            <div className="card bg-white/95 backdrop-blur-md border border-white/20 rounded-lg shadow-xl p-8 text-center">
              <p className="text-sm text-aegis-gray">Loading...</p>
            </div>
          )}

          {!loading && visibleTransactions.length === 0 && (
            <div className="card bg-white/95 backdrop-blur-md border border-white/20 rounded-lg shadow-xl p-8 text-center">
              <div className="w-10 h-10 mx-auto mb-3 rounded-full bg-aegis-offwhite flex items-center justify-center">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#999999" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
              </div>
              <p className="text-sm font-medium text-aegis-black mb-1">
                No active alerts
              </p>
              <p className="text-xs text-aegis-gray">
                All monitored transactions are clear. This dashboard will update automatically when a suspicious transaction is detected.
              </p>
            </div>
          )}

          <div className="space-y-4">
            {visibleTransactions.map(tx => (
              <EscrowCard
                key={tx.transaction_id}
                transaction={tx}
                onResolved={handleResolved}
              />
            ))}
          </div>
        </section>

        {/* Transaction History */}
        {history.length > 0 && (
          <section className="mt-8">
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Transaction History
            </h2>
            <div className="card bg-white/95 backdrop-blur-md border border-white/20 rounded-lg shadow-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-aegis-offwhite border-b border-aegis-border">
                    <th className="text-left text-label px-4 py-2.5 font-semibold">Transaction ID</th>
                    <th className="text-left text-label px-4 py-2.5 font-semibold">Receiver</th>
                    <th className="text-right text-label px-4 py-2.5 font-semibold">Amount</th>
                    <th className="text-center text-label px-4 py-2.5 font-semibold">Risk</th>
                    <th className="text-center text-label px-4 py-2.5 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map(tx => (
                    <tr key={tx.transaction_id} className="border-b border-aegis-border last:border-0">
                      <td className="px-4 py-2.5 text-mono text-xs text-aegis-gray">
                        {tx.transaction_id}
                      </td>
                      <td className="px-4 py-2.5 text-aegis-black">
                        {tx.receiver === 'B' ? 'XXXX 4821' : tx.receiver}
                      </td>
                      <td className="px-4 py-2.5 text-right font-medium text-aegis-black">
                        INR {parseFloat(tx.amount).toLocaleString('en-IN')}
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        {tx.risk_score ? (
                          <span className={`badge ${
                            tx.risk_level === 'HIGH' ? 'badge-danger' :
                            tx.risk_level === 'MEDIUM' ? 'badge-warning' :
                            'badge-success'
                          }`}>
                            {Math.round(tx.risk_score)}
                          </span>
                        ) : (
                          <span className="badge badge-neutral">--</span>
                        )}
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        <span className={`badge ${
                          tx.status === 'REVERSED' ? 'badge-danger' :
                          tx.status === 'ESCROW_LIEN' ? 'badge-warning' :
                          tx.status === 'SUCCESS' ? 'badge-success' :
                          'badge-neutral'
                        }`}>
                          {tx.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>
    </GradientBackground>
  )
}
