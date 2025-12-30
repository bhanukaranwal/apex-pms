import { ReactNode, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Briefcase, 
  TrendingUp, 
  BarChart3, 
  ShieldCheck, 
  FileText, 
  Brain, 
  Settings, 
  LogOut,
  Menu,
  X,
  AlertTriangle
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'

interface LayoutProps {
  children: ReactNode
}

const Layout = ({ children }: LayoutProps) => {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Portfolios', href: '/portfolios', icon: Briefcase },
    { name: 'Risk', href: '/risk', icon: AlertTriangle },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Orders', href: '/orders', icon: TrendingUp },
    { name: 'Compliance', href: '/compliance', icon: ShieldCheck },
    { name: 'Reports', href: '/reports', icon: FileText },
    { name: 'AI Insights', href: '/ai-insights', icon: Brain },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-dark-950 flex">
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-dark-900 border-r border-dark-800 transition-all duration-300 ease-in-out flex flex-col`}>
        <div className="p-4 flex items-center justify-between">
          {sidebarOpen ? (
            <h1 className="text-2xl font-bold text-primary-500">Apex PMS</h1>
          ) : (
            <span className="text-2xl font-bold text-primary-500">A</span>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-dark-800 rounded-lg"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-3 py-2.5 rounded-lg transition-colors ${
                  isActive(item.href)
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-300 hover:bg-dark-800'
                }`}
              >
                <Icon size={20} className="flex-shrink-0" />
                {sidebarOpen && <span className="ml-3">{item.name}</span>}
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-dark-800">
          <div className={`flex items-center ${sidebarOpen ? '' : 'justify-center'}`}>
            <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center text-white font-semibold">
              {user?.full_name?.[0] || 'U'}
            </div>
            {sidebarOpen && (
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-gray-100">{user?.full_name}</p>
                <p className="text-xs text-gray-400">{user?.role}</p>
              </div>
            )}
          </div>
          <button
            onClick={logout}
            className={`mt-3 w-full flex items-center ${sidebarOpen ? 'px-3' : 'justify-center'} py-2 text-red-400 hover:bg-dark-800 rounded-lg transition-colors`}
          >
            <LogOut size={20} />
            {sidebarOpen && <span className="ml-3">Logout</span>}
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>
    </div>
  )
}

export default Layout
