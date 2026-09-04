import { useState } from 'react'
import TransferForm from '../components/TransferForm'
import ProvisionalReceipt from '../components/ProvisionalReceipt'
import { submitTransfer, resetDemo } from '../api/client'
import { GradientBackground } from '@/components/ui/dark-gradient-background'

/**
 * Project Aegis -- Victim Dashboard Page
 *
 * Route: /transfer
 *
 * This is the victim-facing interface styled with the dark gradient
 * background while preserving the legitimate money-transfer application.
 */
export default function VictimDashboard() {
  const [transaction, setTransaction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (formData) => {
    setLoading(true)
    setError(null)
    try {
      const result = await submitTransfer(formData)
      setTransaction(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = async () => {
    setTransaction(null)
    setError(null)
  }

  const handleDemoReset = async () => {
    try {
      await resetDemo()
      setTransaction(null)
      setError(null)
    } catch (err) {
      // Silently fail for demo reset
    }
  }

  return (
    <GradientBackground className="min-h-screen">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-md border-b border-white/10 text-white">
        <div className="max-w-lg mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
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
                Secure Transfer
              </p>
            </div>
          </div>

          {/* Subtle demo reset */}
          <button
            onClick={handleDemoReset}
            className="text-2xs text-white/50 hover:text-white font-mono transition-opacity"
            title="Reset demo state"
          >
            reset
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-lg mx-auto px-4 py-8">
        {error && (
          <div className="alert-critical mb-4">
            <p className="text-sm text-red-200">{error}</p>
          </div>
        )}

        {transaction ? (
          <ProvisionalReceipt
            transaction={transaction}
            onReset={handleReset}
          />
        ) : (
          <div className="card-elevated p-6 shadow-2xl bg-white/95 backdrop-blur-sm border border-white/20">
            <h2 className="text-base font-semibold text-aegis-black mb-1">
              Send Money
            </h2>
            <p className="text-sm text-aegis-gray mb-5">
              Transfer funds to another account
            </p>
            <TransferForm onSubmit={handleSubmit} loading={loading} />
          </div>
        )}
      </main>
    </GradientBackground>
  )
}
