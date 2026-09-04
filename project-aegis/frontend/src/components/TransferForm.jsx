import { useState } from 'react'

/**
 * Project Aegis -- Transfer Form Component
 *
 * Clean money-transfer form for the victim interface.
 * Includes a subtle demo toggle for screen-share simulation.
 * Does NOT show any fraud warnings or risk indicators.
 */
export default function TransferForm({ onSubmit, loading }) {
  const [receiver, setReceiver] = useState('XXXX4821')
  const [amount, setAmount] = useState('50000')
  const [note, setNote] = useState('')
  const [screenShare, setScreenShare] = useState(false)
  const [errors, setErrors] = useState({})

  const validate = () => {
    const newErrors = {}
    if (!receiver.trim()) newErrors.receiver = 'Receiver account is required'
    if (!amount || parseFloat(amount) <= 0) newErrors.amount = 'Enter a valid amount'
    if (parseFloat(amount) > 10000000) newErrors.amount = 'Amount exceeds limit'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!validate()) return
    onSubmit({
      sender: 'A',
      receiver: receiver.trim(),
      amount: parseFloat(amount),
      screenShare,
      note: note.trim() || null,
    })
  }

  const formatCurrency = (val) => {
    const num = parseFloat(val)
    if (isNaN(num)) return ''
    return num.toLocaleString('en-IN')
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Receiver */}
      <div>
        <label className="block text-label mb-1.5" htmlFor="receiver">
          Receiver Account
        </label>
        <input
          id="receiver"
          type="text"
          className="input-field"
          placeholder="Enter receiver account number"
          value={receiver}
          onChange={(e) => setReceiver(e.target.value)}
          disabled={loading}
        />
        {errors.receiver && (
          <p className="text-xs text-risk-high mt-1">{errors.receiver}</p>
        )}
      </div>

      {/* Amount */}
      <div>
        <label className="block text-label mb-1.5" htmlFor="amount">
          Amount (INR)
        </label>
        <div className="relative flex items-center">
          <span className="absolute left-3.5 text-aegis-gray text-sm font-medium pointer-events-none select-none">
            INR
          </span>
          <input
            id="amount"
            type="number"
            className="input-field pl-14"
            style={{ paddingLeft: '3.75rem' }}
            placeholder="0"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            min="1"
            step="1"
            disabled={loading}
          />
        </div>
        {amount && parseFloat(amount) > 0 && (
          <p className="text-xs text-aegis-gray mt-1">
            INR {formatCurrency(amount)}
          </p>
        )}
        {errors.amount && (
          <p className="text-xs text-risk-high mt-1">{errors.amount}</p>
        )}
      </div>

      {/* Note */}
      <div>
        <label className="block text-label mb-1.5" htmlFor="note">
          Note <span className="font-normal text-aegis-midgray">(optional)</span>
        </label>
        <input
          id="note"
          type="text"
          className="input-field"
          placeholder="Add a note"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          maxLength={256}
          disabled={loading}
        />
      </div>

      <div className="divider" />

      {/* Screen Share Demo Toggle */}
      <div className="flex items-center justify-between py-1">
        <div>
          <p className="text-xs text-aegis-midgray font-mono">
            Simulate Active Screen-Share
          </p>
          <p className="text-2xs text-aegis-midgray mt-0.5">
            Demo control -- simulates screen-sharing detection
          </p>
        </div>
        <button
          type="button"
          className={`toggle-track ${screenShare ? 'active' : ''}`}
          onClick={() => setScreenShare(!screenShare)}
          aria-label="Toggle screen share simulation"
        >
          <div className="toggle-thumb" />
        </button>
      </div>

      <div className="divider" />

      {/* Submit */}
      <button
        type="submit"
        className="btn-primary w-full py-3 text-base"
        disabled={loading}
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Processing...
          </span>
        ) : (
          `Send INR ${formatCurrency(amount || '0')}`
        )}
      </button>
    </form>
  )
}
