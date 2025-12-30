import { useState } from 'react'
import { useQuery } from 'react-query'
import { portfolioAPI, riskAPI } from '../lib/api'
import { AlertTriangle, TrendingDown, Activity, Shield } from 'lucide-react'
import { Bar } from 'react-chartjs-2'

const Risk = () => {
  const [selectedPortfolio, setSelectedPortfolio] = useState<number | null>(null)
  const { data: portfolios } = useQuery('portfolios', () => portfolioAPI.list())

  const { data: varData } = useQuery(
    ['var', selectedPortfolio],
    () => riskAPI.var(selectedPortfolio!, { confidence: 0.95, horizon: 1, method: 'monte_carlo', simulations: 10000 }),
    { enabled: !!selectedPortfolio }
  )

  const { data: stressTest } = useQuery(
    ['stress-test', selectedPortfolio],
    () => riskAPI.stressTest(selectedPortfolio!, { scenario: '2008_financial_crisis' }),
    { enabled: !!selectedPortfolio }
  )

  const stressTestData = {
    labels: ['2008 Crisis', 'COVID Crash', 'Black Monday', 'Dotcom Bubble'],
    datasets: [{
      label: 'Portfolio Impact (%)',
      data: [-35, -28, -18, -42],
      backgroundColor: 'rgba(239, 68, 68, 0.8)',
    }]
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Risk Management</h1>
          <p className="text-gray-400 mt-1">Monitor and analyze portfolio risk metrics</p>
        </div>
        <select
          value={selectedPortfolio || ''}
          onChange={(e) => setSelectedPortfolio(parseInt(e.target.value))}
          className="w-64"
        >
          <option value="">Select Portfolio</option>
          {portfolios?.data?.map((p: any) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>

      {selectedPortfolio && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="card">
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-red-600 p-2 rounded-lg">
                  <AlertTriangle size={20} className="text-white" />
                </div>
                <div className="stat-label">95% VaR (1D)</div>
              </div>
              <div className="stat-value">${(varData?.data?.var / 1000).toFixed(1)}K</div>
              <div className="text-sm text-gray-400 mt-1">{varData?.data?.var_percentage?.toFixed(2)}% of portfolio</div>
            </div>

            <div className="card">
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-orange-600 p-2 rounded-lg">
                  <TrendingDown size={20} className="text-white" />
                </div>
                <div className="stat-label">CVaR (ES)</div>
              </div>
              <div className="stat-value">${(varData?.data?.cvar / 1000).toFixed(1)}K</div>
              <div className="text-sm text-gray-400 mt-1">Expected shortfall</div>
            </div>

            <div className="card">
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-yellow-600 p-2 rounded-lg">
                  <Activity size={20} className="text-white" />
                </div>
                <div className="stat-label">Stress Test</div>
              </div>
              <div className="stat-value">{stressTest?.data?.pnl_percentage?.toFixed(1)}%</div>
              <div className="text-sm text-gray-400 mt-1">2008 Crisis scenario</div>
            </div>

            <div className="card">
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-primary-600 p-2 rounded-lg">
                  <Shield size={20} className="text-white" />
                </div>
                <div className="stat-label">Risk Score</div>
              </div>
              <div className="stat-value">7.2</div>
              <div className="text-sm text-primary-500 mt-1">Moderate risk</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card">
              <h2 className="text-xl font-semibold text-white mb-4">Stress Test Scenarios</h2>
              <Bar
                data={stressTestData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { display: false },
                  },
                  scales: {
                    y: {
                      grid: { color: '#334155' },
                      ticks: { color: '#94a3b8' },
                    },
                    x: {
                      grid: { color: '#334155' },
                      ticks: { color: '#94a3b8' },
                    },
                  },
                }}
                height={300}
              />
            </div>

            <div className="card">
              <h2 className="text-xl font-semibold text-white mb-4">VaR Analysis</h2>
              <div className="space-y-4">
                <div className="bg-dark-800 p-4 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-400">Method</span>
                    <span className="text-white font-semibold">{varData?.data?.method || 'Monte Carlo'}</span>
                  </div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-400">Confidence Level</span>
                    <span className="text-white font-semibold">{(varData?.data?.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-400">Time Horizon</span>
                    <span className="text-white font-semibold">{varData?.data?.horizon} day</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Portfolio Value</span>
                    <span className="text-white font-semibold">${(varData?.data?.portfolio_value / 1000000).toFixed(2)}M</span>
                  </div>
                </div>

                <div className="bg-red-900 bg-opacity-20 border border-red-800 p-4 rounded-lg">
                  <h3 className="text-red-400 font-semibold mb-2">Risk Alert</h3>
                  <p className="text-sm text-gray-300">
                    There is a 5% chance that the portfolio could lose more than ${(varData?.data?.var / 1000).toFixed(1)}K in the next trading day.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold text-white mb-4">Position-Level Stress Impact</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b border-dark-800">
                  <tr>
                    <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Ticker</th>
                    <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Current Value</th>
                    <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Stressed Value</th>
                    <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Impact</th>
                    <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Impact %</th>
                  </tr>
                </thead>
                <tbody>
                  {stressTest?.data?.position_impacts?.map((impact: any, idx: number) => (
                    <tr key={idx} className="border-b border-dark-800 hover:bg-dark-800">
                      <td className="py-3 px-2 font-medium text-white">{impact.ticker}</td>
                      <td className="py-3 px-2 text-right text-gray-300">${impact.current_value.toLocaleString()}</td>
                      <td className="py-3 px-2 text-right text-gray-300">${impact.shocked_value.toLocaleString()}</td>
                      <td className="py-3 px-2 text-right text-red-500">${impact.impact.toLocaleString()}</td>
                      <td className="py-3 px-2 text-right text-red-500">{impact.impact_percentage.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default Risk
