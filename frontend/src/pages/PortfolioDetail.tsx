import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from 'react-query'
import { portfolioAPI, positionAPI, riskAPI, analyticsAPI } from '../lib/api'
import { ArrowLeft, Plus, TrendingUp, AlertTriangle, DollarSign, Percent } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Line, Doughnut } from 'react-chartjs-2'

const PortfolioDetail = () => {
  const { id } = useParams()
  const portfolioId = parseInt(id || '0')

  const { data: portfolio } = useQuery(['portfolio', portfolioId], () => portfolioAPI.get(portfolioId))
  const { data: positions } = useQuery(['positions', portfolioId], () => positionAPI.list(portfolioId))
  const { data: riskMetrics } = useQuery(['risk-metrics', portfolioId], () => 
    riskAPI.metrics(portfolioId, { lookback_days: 252 })
  )

  const positionsData = positions?.data || []
  const totalValue = positionsData.reduce((sum: number, p: any) => sum + (parseFloat(p.market_value) || 0), 0)

  const allocationData = {
    labels: positionsData.slice(0, 10).map((p: any) => p.ticker),
    datasets: [{
      data: positionsData.slice(0, 10).map((p: any) => parseFloat(p.market_value) || 0),
      backgroundColor: [
        '#3b82f6', '#22c55e', '#eab308', '#ef4444', '#8b5cf6',
        '#ec4899', '#f97316', '#06b6d4', '#84cc16', '#f59e0b'
      ],
    }]
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/portfolios" className="p-2 hover:bg-dark-800 rounded-lg">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-white">{portfolio?.data?.name}</h1>
            <p className="text-gray-400 mt-1">{portfolio?.data?.description || 'No description'}</p>
          </div>
        </div>
        <button className="btn-primary">
          <Plus size={18} className="mr-2" />
          Add Position
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-blue-600 p-2 rounded-lg">
              <DollarSign size={20} className="text-white" />
            </div>
            <div className="stat-label">Total Value</div>
          </div>
          <div className="stat-value">${(totalValue / 1000000).toFixed(2)}M</div>
          <div className="stat-change-positive mt-1">+12.5% YTD</div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-primary-600 p-2 rounded-lg">
              <TrendingUp size={20} className="text-white" />
            </div>
            <div className="stat-label">Sharpe Ratio</div>
          </div>
          <div className="stat-value">{riskMetrics?.data?.sharpe_ratio?.toFixed(2) || '0.00'}</div>
          <div className="stat-change-positive mt-1">+0.15</div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-yellow-600 p-2 rounded-lg">
              <AlertTriangle size={20} className="text-white" />
            </div>
            <div className="stat-label">Volatility</div>
          </div>
          <div className="stat-value">{(riskMetrics?.data?.volatility * 100)?.toFixed(1) || '0.0'}%</div>
          <div className="stat-change-negative mt-1">-1.2%</div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-red-600 p-2 rounded-lg">
              <Percent size={20} className="text-white" />
            </div>
            <div className="stat-label">Max Drawdown</div>
          </div>
          <div className="stat-value">{(riskMetrics?.data?.max_drawdown * 100)?.toFixed(1) || '0.0'}%</div>
          <div className="stat-change-positive mt-1">+1.1%</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card">
          <h2 className="text-xl font-semibold text-white mb-4">Holdings</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-dark-800">
                <tr>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Ticker</th>
                  <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Shares</th>
                  <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Price</th>
                  <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Value</th>
                  <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Weight</th>
                  <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">P&L</th>
                </tr>
              </thead>
              <tbody>
                {positionsData.map((position: any) => {
                  const weight = (parseFloat(position.market_value) / totalValue) * 100
                  const pnl = parseFloat(position.unrealized_pnl) || 0
                  return (
                    <tr key={position.id} className="border-b border-dark-800 hover:bg-dark-800 transition-colors">
                      <td className="py-3 px-2 font-medium text-white">{position.ticker}</td>
                      <td className="py-3 px-2 text-right text-gray-300">{parseFloat(position.shares).toFixed(2)}</td>
                      <td className="py-3 px-2 text-right text-gray-300">${parseFloat(position.current_price).toFixed(2)}</td>
                      <td className="py-3 px-2 text-right text-gray-300">${parseFloat(position.market_value).toLocaleString()}</td>
                      <td className="py-3 px-2 text-right text-gray-300">{weight.toFixed(1)}%</td>
                      <td className={`py-3 px-2 text-right font-medium ${pnl >= 0 ? 'text-primary-500' : 'text-red-500'}`}>
                        ${pnl.toLocaleString()}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Asset Allocation</h2>
          <div className="h-64 flex items-center justify-center">
            <Doughnut 
              data={allocationData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom',
                    labels: {
                      color: '#cbd5e1',
                      padding: 10,
                      font: { size: 11 }
                    }
                  }
                }
              }}
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Risk Metrics</h2>
          <div className="space-y-4">
            {[
              { label: 'Beta', value: riskMetrics?.data?.beta?.toFixed(2) || '0.00' },
              { label: 'Alpha', value: `${(riskMetrics?.data?.alpha * 100)?.toFixed(2) || '0.00'}%` },
              { label: 'Sortino Ratio', value: riskMetrics?.data?.sortino_ratio?.toFixed(2) || '0.00' },
              { label: 'Information Ratio', value: riskMetrics?.data?.information_ratio?.toFixed(2) || '0.00' },
              { label: 'Tracking Error', value: `${(riskMetrics?.data?.tracking_error * 100)?.toFixed(2) || '0.00'}%` },
            ].map((metric) => (
              <div key={metric.label} className="flex justify-between items-center">
                <span className="text-gray-400">{metric.label}</span>
                <span className="text-white font-semibold">{metric.value}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Portfolio Info</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Strategy</span>
              <span className="text-white font-semibold">{portfolio?.data?.strategy || 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Benchmark</span>
              <span className="text-white font-semibold">{portfolio?.data?.benchmark || 'SPY'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Inception Date</span>
              <span className="text-white font-semibold">
                {new Date(portfolio?.data?.inception_date).toLocaleDateString()}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Currency</span>
              <span className="text-white font-semibold">{portfolio?.data?.base_currency}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Number of Positions</span>
              <span className="text-white font-semibold">{positionsData.length}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PortfolioDetail
