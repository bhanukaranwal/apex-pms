import { useState } from 'react'
import { useQuery } from 'react-query'
import { portfolioAPI, analyticsAPI } from '../lib/api'
import { BarChart3, PieChart, TrendingUp } from 'lucide-react'

const Analytics = () => {
  const [selectedPortfolio, setSelectedPortfolio] = useState<number | null>(null)
  const { data: portfolios } = useQuery('portfolios', () => portfolioAPI.list())

  const { data: returns } = useQuery(
    ['returns', selectedPortfolio],
    () => analyticsAPI.returns(selectedPortfolio!, {
      start_date: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end_date: new Date().toISOString().split('T')[0],
      frequency: 'monthly'
    }),
    { enabled: !!selectedPortfolio }
  )

  const { data: attribution } = useQuery(
    ['attribution', selectedPortfolio],
    () => analyticsAPI.attribution(selectedPortfolio!, {
      start_date: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end_date: new Date().toISOString().split('T')[0],
      method: 'brinson_fachler'
    }),
    { enabled: !!selectedPortfolio }
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Analytics</h1>
          <p className="text-gray-400 mt-1">Performance analysis and attribution</p>
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card">
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-primary-600 p-2 rounded-lg">
                  <TrendingUp size={20} className="text-white" />
                </div>
                <div className="stat-label">Total Return</div>
              </div>
              <div className="stat-value">{(returns?.data?.cumulative_return * 100)?.toFixed(2)}%</div>
              <div className="text-sm text-gray-400 mt-1">Since inception</div>
            </div>

            <div className="card">
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-blue-600 p-2 rounded-lg">
                  <BarChart3 size={20} className="text-white" />
                </div>
                <div className="stat-label">Annualized Return</div>
              </div>
              <div className="stat-value">{(returns?.data?.annualized_return * 100)?.toFixed(2)}%</div>
              <div className="text-sm text-gray-400 mt-1">CAGR</div>
            </div>

            <div className="card">
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-green-600 p-2 rounded-lg">
                  <PieChart size={20} className="text-white" />
                </div>
                <div className="stat-label">Active Return</div>
              </div>
              <div className="stat-value">{(attribution?.data?.active_return * 100)?.toFixed(2)}%</div>
              <div className="text-sm text-gray-400 mt-1">vs Benchmark</div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold text-white mb-4">Brinson-Fachler Attribution</h2>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-dark-800 p-4 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">Allocation Effect</p>
                <p className="text-2xl font-bold text-primary-500">{(attribution?.data?.allocation_effect * 100)?.toFixed(2)}%</p>
              </div>
              <div className="bg-dark-800 p-4 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">Selection Effect</p>
                <p className="text-2xl font-bold text-blue-500">{(attribution?.data?.selection_effect * 100)?.toFixed(2)}%</p>
              </div>
              <div className="bg-dark-800 p-4 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">Interaction Effect</p>
                <p className="text-2xl font-bold text-green-500">{(attribution?.data?.interaction_effect * 100)?.toFixed(2)}%</p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b border-dark-800">
                  <tr>
                    <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Sector</th>
                    <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Portfolio Weight</th>
                    <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Benchmark Weight</th>
                    <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Allocation</th>
                    <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Selection</th>
                    <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Total Effect</th>
                  </tr>
                </thead>
                <tbody>
                  {attribution?.data?.sector_attribution?.map((sector: any, idx: number) => (
                    <tr key={idx} className="border-b border-dark-800 hover:bg-dark-800">
                      <td className="py-3 px-2 font-medium text-white">{sector.sector}</td>
                      <td className="py-3 px-2 text-right text-gray-300">{(sector.portfolio_weight * 100).toFixed(1)}%</td>
                      <td className="py-3 px-2 text-right text-gray-300">{(sector.benchmark_weight * 100).toFixed(1)}%</td>
                      <td className={`py-3 px-2 text-right ${sector.allocation_effect >= 0 ? 'text-primary-500' : 'text-red-500'}`}>
                        {(sector.allocation_effect * 100).toFixed(2)}%
                      </td>
                      <td className={`py-3 px-2 text-right ${sector.selection_effect >= 0 ? 'text-primary-500' : 'text-red-500'}`}>
                        {(sector.selection_effect * 100).toFixed(2)}%
                      </td>
                      <td className={`py-3 px-2 text-right font-semibold ${sector.total_effect >= 0 ? 'text-primary-500' : 'text-red-500'}`}>
                        {(sector.total_effect * 100).toFixed(2)}%
                      </td>
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

export default Analytics
