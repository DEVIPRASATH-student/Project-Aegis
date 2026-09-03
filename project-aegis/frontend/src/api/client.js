/**
 * Project Aegis -- API Client
 *
 * Fetch wrapper for communicating with the FastAPI backend.
 * All API calls go through the Vite dev proxy (/api -> localhost:8000).
 */

const API_BASE = '/api/v1';

/**
 * Generic fetch wrapper with error handling.
 */
async function request(url, options = {}) {
  const config = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const message = errorData.detail || `Request failed (${response.status})`;
      throw new Error(message);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to reach the server. Please ensure the backend is running.');
    }
    throw error;
  }
}

/**
 * Submit a new transfer transaction.
 * POST /api/v1/transfer
 */
export async function submitTransfer({ sender, receiver, amount, screenShare, note }) {
  return request(`${API_BASE}/transfer`, {
    method: 'POST',
    body: JSON.stringify({
      sender,
      receiver,
      amount: parseFloat(amount),
      screen_share: screenShare,
      note: note || null,
    }),
  });
}

/**
 * Get the current status of a transaction.
 * Used by victim UI to detect reversals.
 * GET /api/v1/transfer/{transaction_id}
 */
export async function getTransactionStatus(transactionId) {
  return request(`${API_BASE}/transfer/${transactionId}`);
}

/**
 * Get all escrowed transactions for a user.
 * Used by co-signer dashboard polling.
 * GET /api/v1/escrow/{user_id}
 */
export async function getEscrowTransactions(userId) {
  return request(`${API_BASE}/escrow/${userId}`);
}

/**
 * Resolve an escrowed transaction (approve or reverse).
 * POST /api/v1/escrow/resolve
 */
export async function resolveEscrow({ transactionId, decision, resolvedBy }) {
  return request(`${API_BASE}/escrow/resolve`, {
    method: 'POST',
    body: JSON.stringify({
      transaction_id: transactionId,
      decision,
      resolved_by: resolvedBy || 'co-signer',
    }),
  });
}

/**
 * Get all transactions for a user (all statuses).
 * GET /api/v1/transactions/{user_id}
 */
export async function getAllTransactions(userId) {
  return request(`${API_BASE}/transactions/${userId}`);
}

/**
 * Reset all demo data.
 * POST /api/v1/demo/reset
 */
export async function resetDemo() {
  return request(`${API_BASE}/demo/reset`, {
    method: 'POST',
  });
}

/**
 * Health check.
 * GET /health
 */
export async function healthCheck() {
  return request('/health');
}
