import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Project Aegis -- Transaction Status Polling Hook
 *
 * Polls a transaction's status at regular intervals.
 * Used by the victim UI to detect when a co-signer reverses a transaction.
 *
 * @param {string|null} transactionId - The transaction ID to poll
 * @param {number} interval - Polling interval in milliseconds (default: 2500)
 * @returns {{ status, data, error, stopPolling }}
 */
export function useTransactionPoller(transactionId, interval = 2500) {
  const [status, setStatus] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const timerRef = useRef(null);
  const activeRef = useRef(false);

  const stopPolling = useCallback(() => {
    activeRef.current = false;
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!transactionId) return;

    activeRef.current = true;

    const poll = async () => {
      if (!activeRef.current) return;
      try {
        const response = await fetch(`/api/v1/transfer/${transactionId}`);
        if (!response.ok) return;
        const result = await response.json();
        setData(result);
        setStatus(result.status);

        // Stop polling if transaction is in a terminal state
        if (result.status === 'REVERSED' || result.status === 'SUCCESS') {
          // Keep polling a bit after terminal state for reliability
        }
      } catch (err) {
        setError(err.message);
      }
    };

    // Initial fetch
    poll();

    // Start interval
    timerRef.current = setInterval(poll, interval);

    return () => {
      stopPolling();
    };
  }, [transactionId, interval, stopPolling]);

  return { status, data, error, stopPolling };
}

/**
 * Escrow polling hook for the co-signer dashboard.
 *
 * Polls the escrow endpoint for a user's protected transactions.
 *
 * @param {string} userId - The user ID to monitor
 * @param {number} interval - Polling interval in milliseconds (default: 2500)
 * @returns {{ transactions, totalProtected, activeAlerts, error, loading }}
 */
export function useEscrowPoller(userId, interval = 2500) {
  const [transactions, setTransactions] = useState([]);
  const [totalProtected, setTotalProtected] = useState(0);
  const [activeAlerts, setActiveAlerts] = useState(0);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const timerRef = useRef(null);

  useEffect(() => {
    if (!userId) return;

    const poll = async () => {
      try {
        const response = await fetch(`/api/v1/escrow/${userId}`);
        if (!response.ok) {
          throw new Error(`Server responded with ${response.status}`);
        }
        const result = await response.json();
        setTransactions(result.transactions || []);
        setTotalProtected(result.total_protected_amount || 0);
        setActiveAlerts(result.active_alerts || 0);
        setError(null);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    // Initial fetch
    poll();

    // Start interval
    timerRef.current = setInterval(poll, interval);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [userId, interval]);

  return { transactions, totalProtected, activeAlerts, error, loading };
}
