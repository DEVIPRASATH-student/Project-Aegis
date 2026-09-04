import { Routes, Route, Navigate } from 'react-router-dom'
import VictimDashboard from './pages/VictimDashboard'
import CoSignerAlerts from './pages/CoSignerAlerts'
import DemoGradient from '@/components/ui/demo'

/**
 * Project Aegis -- Application Router
 *
 * Routes:
 *   /transfer   -- Victim-facing transfer interface
 *   /dashboard  -- Trusted co-signer dashboard
 *   /demo       -- Dark gradient background demo
 *   /           -- Redirects to /transfer
 */
export default function App() {
  return (
    <Routes>
      <Route path="/transfer" element={<VictimDashboard />} />
      <Route path="/dashboard" element={<CoSignerAlerts />} />
      <Route path="/demo" element={<DemoGradient />} />
      <Route path="/" element={<Navigate to="/transfer" replace />} />
    </Routes>
  )
}
