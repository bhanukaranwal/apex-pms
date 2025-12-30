import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Portfolios from './pages/Portfolios'
import PortfolioDetail from './pages/PortfolioDetail'
import Risk from './pages/Risk'
import Analytics from './pages/Analytics'
import Orders from './pages/Orders'
import Compliance from './pages/Compliance'
import Reports from './pages/Reports'
import AIInsights from './pages/AIInsights'
import Settings from './pages/Settings'

function App() {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/portfolios" element={<Portfolios />} />
        <Route path="/portfolios/:id" element={<PortfolioDetail />} />
        <Route path="/risk" element={<Risk />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/orders" element={<Orders />} />
        <Route path="/compliance" element={<Compliance />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/ai-insights" element={<AIInsights />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}

export default App
