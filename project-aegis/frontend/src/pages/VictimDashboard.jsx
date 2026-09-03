import { useState } from 'react'
import TransferForm from '../components/TransferForm'
import ProvisionalReceipt from '../components/ProvisionalReceipt'
import { submitTransfer, resetDemo } from '../api/client'

/**
 * Project Aegis -- Victim Dashboard Page
 *
 * Route: /transfer
 *
 * This is the victim-facing interface. It looks like a simple,
 * legitimate money-transfer application. The victim should NOT
 * see any fraud warnings, risk scores, or security alerts.
 *
 * After submission, the receipt always shows "Payment Successful"
 * regardless of the actual backend status (asymmetric deception).
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
    <div className="min-h-screen bg-aegis-offwhite">
      {/* Header */}
      <header className="bg-white border-b border-aegis-border">
        <div className="max-w-lg mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-aegis-black rounded flex items-center justify-center">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <div>
              <h1 className="text-sm font-semibold text-aegis-black tracking-tight">
                Project Aegis
              </h1>
              <p className="text-2xs text-aegis-midgray">
                Secure Transfer
              </p>
            </div>
          </div>

          {/* Subtle demo reset */}
          <button
            onClick={handleDemoReset}
            className="text-2xs text-aegis-midgray hover:text-aegis-gray font-mono opacity-40 hover:opacity-100 transition-opacity"
            title="Reset demo state"
          >
            reset
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-lg mx-auto px-4 py-6">
        {error && (
          <div className="alert-info mb-4">
            <p className="text-sm text-aegis-charcoal">{error}</p>
          </div>
        )}

        {transaction ? (
          <ProvisionalReceipt
            transaction={transaction}
            onReset={handleReset}
          />
        ) : (
          <div className="card-elevated p-5">
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
    </div>
  )
}
