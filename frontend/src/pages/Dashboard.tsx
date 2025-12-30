import { useQuery } from 'react-query'
import { portfolioAPI } from '../lib/api'
import { TrendingUp, TrendingDown, DollarSign, Briefcase, AlertTriangle, Target } from 'lucide-react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const Dashboard = () => {
  const { data: portfolios, isLoading } = useQuery('portfolios', () => portfolioAPI.list())

  const stats = [
    { 
      name: 'Total AUM', 
      value: '$2.45B', 
      change: '+12.5%', 
      positive: true, 
      icon: DollarSign,
      color: 'bg-blue-600'
    },
    { 
      name: 'Active Portfolios', 
      value: portfolios?.data?.length || '0', 
      change: '+3', 
      positive: true, 
      icon: Briefcase,
      color: 'bg-primary-600'
    },
    { 
      name: 'YTD Return', 
      value: '+18.3%', 
      change: '+2.1%', 
      positive: true, 
      icon: TrendingUp,
      color: 'bg-green-600'
    },
    { 
      name: 'Risk Score', 
      value: '7.2', 
      change: '-0.3', 
      positive: true, 
      icon: AlertTriangle,
      color: 'bg-yellow-600'
    },
  ]

  const chartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'Portfolio Value',
        data: [2.1, 2.15, 2.18, 2.22, 2.28, 2.32, 2.35, 2.38, 2.41, 2.43, 2.44, 2.45],
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: '#1e293b',
        titleColor: '#fff',
        bodyColor: '#cbd5e1',
        borderColor: '#334155',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        grid: {
          color: '#334155',
          drawBorder: false,
        },
        ticks: {
          color: '#94a3b8',
        },
      },
      y: {
        grid: {
          color: '#334155',
          drawBorder: false,
        },
        ticks: {
          color: '#94a3b8',
          callback: (value: any) => `$${value}B`,
        },
      },
    },
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-96">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
    </div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 mt-1">Welcome back, here's your portfolio overview</p>
        </div>
        <button className="btn-primary">
          <Target size={18} className="mr-2" />
          Run Analysis
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center justify-between mb-4">
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon size={24} className="text-white" />
                </div>
                <span className={stat.positive ? 'stat-change-positive' : 'stat-change-negative'}>
                  {stat.change}
                </span>
              </div>
              <div className="stat-label">{stat.name}</div>
              <div className="stat-value">{stat.value}</div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card">
          <h2 className="text-xl font-semibold text-white mb-4">Portfolio Performance</h2>
          <div style={{ height: '300px' }}>
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Recent Portfolios</h2>
          <div className="space-y-3">
            {portfolios?.data?.slice(0, 5).map((portfolio: any) => (
              <div key={portfolio.id} className="flex items-center justify-between p-3 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors cursor-pointer">
                <div>
                  <p className="font-medium text-gray-100">{portfolio.name}</p>
                  <p className="text-sm text-gray-400">{portfolio.strategy || 'No strategy'}</p>
                </div>
                <TrendingUp size={18} className="text-primary-500" />
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Asset Allocation</h2>
          <div className="space-y-3">
            {[
              { name: 'Equities', value: 65, color: 'bg-blue-500' },
              { name: 'Fixed Income', value: 20, color: 'bg-green-500' },
              { name: 'Alternatives', value: 10, color: 'bg-yellow-500' },
              { name: 'Cash', value: 5, color: 'bg-gray-500' },
            ].map((asset) => (
              <div key={asset.name}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-300">{asset.name}</span>
                  <span className="text-gray-400">{asset.value}%</span>
                </div>
                <div className="w-full bg-dark-800 rounded-full h-2">
                  <div className={`${asset.color} h-2 rounded-full`} style={{ width: `${asset.value}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Top Performers</h2>
          <div className="space-y-3">
            {[
              { ticker: 'NVDA', return: 245.3, value: 125000 },
              { ticker: 'MSFT', return: 42.1, value: 98000 },
              { ticker: 'AAPL', return: 38.5, value: 87000 },
              { ticker: 'GOOGL', return: 35.2, value: 76000 },
              { ticker: 'AMZN', return: 28.7, value: 65000 },
            ].map((position) => (
              <div key={position.ticker} className="flex items-center justify-between p-3 bg-dark-800 rounded-lg">
                <div>
                  <p className="font-medium text-gray-100">{position.ticker}</p>
                  <p className="text-sm text-gray-400">${position.value.toLocaleString()}</p>
                </div>
                <span className="text-primary-500 font-semibold">+{position.return}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
