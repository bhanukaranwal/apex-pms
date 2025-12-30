import { useState } from 'react'
import { useQuery } from 'react-query'
import { aiAPI, portfolioAPI } from '../lib/api'
import { Brain, TrendingUp, Activity, Lightbulb } from 'lucide-react'

const AIInsights = () => {
  const [selectedPortfolio, setSelectedPortfolio] = useState<number | null>(null)
  const { data: portfolios } = useQuery('portfolios', () => portfolioAPI.list())

  const { data: recommendations } = useQuery(
    ['recommendations', selectedPortfolio],
    () => aiAPI.recommendations(selectedPortfolio!),
    { enabled: !!selectedPortfolio }
  )

  const { data: regime } = useQuery('regime', () => aiAPI.regimeDetection({ lookback_days: 252 }))

  const { data: alphaSignals } = useQuery('alpha-signals', () =>
    aiAPI.alphaSignals({ tickers: 'AAPL,MSFT,GOOGL,AMZN,NVDA', horizon: 30 })
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">AI Insights</h1>
          <p className="text-gray-400 mt-1">ML-powered analytics and recommendations</p>
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

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-purple-600 p-2 rounded-lg">
              <Brain size={20} className="text-white" />
            </div>
            <div className="stat-label">Market Regime</div>
          </div>
          <div className="stat-value capitalize">{regime?.data?.current_regime?.replace('_', ' ') || 'Loading...'}</div>
          <div className="text-sm text-gray-400 mt-1">
            {(regime?.data?.regime_probability * 100)?.toFixed(0)}% confidence
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-blue-600 p-2 rounded-lg">
              <TrendingUp size={20} className="text-white" />
            </div>
            <div className="stat-label">Alpha Signals</div>
          </div>
          <div className="stat-value">{Object.keys(alphaSignals?.data || {}).length}</div>
          <div className="text-sm text-gray-400 mt-1">Active predictions</div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-green-600 p-2 rounded-lg">
              <Lightbulb size={20} className="text-white" />
            </div>
            <div className="stat-label">Recommendations</div>
          </div>
          <div className="stat-value">{recommendations?.data?.recommendations?.length || 0}</div>
          <div className="text-sm text-gray-400 mt-1">For your portfolio</div>
        </div>
      </div>

      {selectedPortfolio && (
        <>
          <div className="card">
            <h2 className="text-xl font-semibold text-white mb-4">AI Recommendations</h2>
            <div className="space-y-3">
              {recommendations?.data?.recommendations?.map((rec: any, idx: number) => (
                <div key={idx} className="bg-dark-800 p-4 rounded-lg flex items-start gap-4">
                  <div className={`p-2 rounded-lg ${
                    rec.action === 'buy' || rec.action === 'increase' ? 'bg-primary-600' :
                    rec.action === 'sell' || rec.action === 'reduce' ? 'bg-red-600' :
                    'bg-gray-600'
                  }`}>
                    <Activity size={20} className="text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-white capitalize">{rec.action} {rec.ticker}</h3>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        rec.priority === 'high' ? 'bg-red-900 text-red-300' :
                        rec.priority === 'medium' ? 'bg-yellow-900 text-yellow-300' :
                        'bg-blue-900 text-blue-300'
                      }`}>
                        {rec.priority}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400">{rec.reason}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {recommendations?.data?.risk_alerts?.length > 0 && (
            <div className="card bg-yellow-900 bg-opacity-20 border-yellow-800">
              <h2 className="text-xl font-semibold text-yellow-400 mb-4">Risk Alerts</h2>
              <ul className="space-y-2">
                {recommendations?.data?.risk_alerts?.map((alert: string, idx: number) => (
                  <li key={idx} className="text-gray-300 flex items-start gap-2">
                    <Activity size={16} className="text-yellow-400 mt-0.5 flex-shrink-0" />
                    <span>{alert}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Alpha Prediction Signals</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-dark-800">
              <tr>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Ticker</th>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Signal</th>
                <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Confidence</th>
                <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Predicted Return</th>
                <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Horizon</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(alphaSignals?.data || {}).map(([ticker, signal]: [string, any]) => (
                <tr key={ticker} className="border-b border-dark-800 hover:bg-dark-800">
                  <td className="py-3 px-2 font-medium text-white">{ticker}</td>
                  <td className="py-3 px-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      signal.direction === 'bullish' ? 'bg-primary-900 text-primary-300' :
                      signal.direction === 'bearish' ? 'bg-red-900 text-red-300' :
                      'bg-gray-800 text-gray-400'
                    }`}>
                      {signal.direction}
                    </span>
                  </td>
                  <td className="py-3 px-2 text-right text-gray-300">{(signal.confidence * 100).toFixed(0)}%</td>
                  <td className={`py-3 px-2 text-right font-medium ${
                    signal.predicted_return >= 0 ? 'text-primary-500' : 'text-red-500'
                  }`}>
                    {(signal.predicted_return * 100).toFixed(2)}%
                  </td>
                  <td className="py-3 px-2 text-right text-gray-400">{signal.horizon_days}d</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default AIInsights
