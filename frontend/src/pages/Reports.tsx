import { useState } from 'react'
import { useMutation } from 'react-query'
import { reportAPI, portfolioAPI } from '../lib/api'
import { FileText, Download, Calendar } from 'lucide-react'
import { useQuery } from 'react-query'
import toast from 'react-hot-toast'

const Reports = () => {
  const [selectedPortfolio, setSelectedPortfolio] = useState<number | null>(null)
  const [reportType, setReportType] = useState('performance')
  const [startDate, setStartDate] = useState(new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0])
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0])
  const [format, setFormat] = useState('pdf')

  const { data: portfolios } = useQuery('portfolios', () => portfolioAPI.list())

  const generateMutation = useMutation(
    async (data: any) => {
      if (reportType === 'performance') {
        return reportAPI.performance(data.portfolioId, data)
      } else if (reportType === 'holdings') {
        return reportAPI.holdings(data.portfolioId, data)
      } else if (reportType === 'risk') {
        return reportAPI.risk(data.portfolioId, data)
      } else {
        return reportAPI.tax(data.portfolioId, new Date().getFullYear())
      }
    },
    {
      onSuccess: () => {
        toast.success('Report generated successfully')
      },
      onError: () => {
        toast.error('Failed to generate report')
      },
    }
  )

  const handleGenerate = () => {
    if (!selectedPortfolio) {
      toast.error('Please select a portfolio')
      return
    }

    generateMutation.mutate({
      portfolioId: selectedPortfolio,
      start_date: startDate,
      end_date: endDate,
      format,
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Reports</h1>
          <p className="text-gray-400 mt-1">Generate and download portfolio reports</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card">
          <h2 className="text-xl font-semibold text-white mb-6">Generate Report</h2>
          
          <div className="space-y-4">
            <div className="input-group">
              <label className="label">Portfolio</label>
              <select
                value={selectedPortfolio || ''}
                onChange={(e) => setSelectedPortfolio(parseInt(e.target.value))}
                className="w-full"
              >
                <option value="">Select portfolio</option>
                {portfolios?.data?.map((p: any) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            <div className="input-group">
              <label className="label">Report Type</label>
              <select
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                className="w-full"
              >
                <option value="performance">Performance Report</option>
                <option value="holdings">Holdings Report</option>
                <option value="risk">Risk Report</option>
                <option value="tax">Tax Report</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="input-group">
                <label className="label">Start Date</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full"
                />
              </div>

              <div className="input-group">
                <label className="label">End Date</label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full"
                />
              </div>
            </div>

            <div className="input-group">
              <label className="label">Format</label>
              <select
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                className="w-full"
              >
                <option value="pdf">PDF</option>
                <option value="excel">Excel</option>
              </select>
            </div>

            <button
              onClick={handleGenerate}
              disabled={generateMutation.isLoading}
              className="btn-primary w-full"
            >
              {generateMutation.isLoading ? 'Generating...' : 'Generate Report'}
            </button>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-6">Quick Reports</h2>
          <div className="space-y-3">
            {[
              { name: 'Monthly Performance', type: 'performance', icon: FileText },
              { name: 'Current Holdings', type: 'holdings', icon: FileText },
              { name: 'Risk Analysis', type: 'risk', icon: FileText },
              { name: 'Tax Summary', type: 'tax', icon: FileText },
            ].map((report) => {
              const Icon = report.icon
              return (
                <button
                  key={report.name}
                  className="w-full bg-dark-800 hover:bg-dark-700 p-4 rounded-lg flex items-center gap-3 transition-colors"
                >
                  <Icon size={20} className="text-primary-500" />
                  <span className="text-white font-medium">{report.name}</span>
                  <Download size={16} className="ml-auto text-gray-400" />
                </button>
              )
            })}
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Recent Reports</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-dark-800">
              <tr>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Report Name</th>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Portfolio</th>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Type</th>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Generated</th>
                <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {[
                { id: 1, name: 'Q4 Performance Report', portfolio: 'Growth Equity Fund', type: 'Performance', date: '2025-12-30' },
                { id: 2, name: 'Holdings Summary', portfolio: 'Balanced Portfolio', type: 'Holdings', date: '2025-12-29' },
                { id: 3, name: 'Risk Analysis', portfolio: 'Tech Growth', type: 'Risk', date: '2025-12-28' },
              ].map((report) => (
                <tr key={report.id} className="border-b border-dark-800 hover:bg-dark-800">
                  <td className="py-3 px-2 font-medium text-white">{report.name}</td>
                  <td className="py-3 px-2 text-gray-300">{report.portfolio}</td>
                  <td className="py-3 px-2 text-gray-300">{report.type}</td>
                  <td className="py-3 px-2 text-gray-400 text-sm">
                    {new Date(report.date).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-2 text-right">
                    <button className="px-3 py-1 bg-primary-600 hover:bg-primary-700 text-white text-sm rounded flex items-center gap-1 ml-auto">
                      <Download size={14} />
                      Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Reports
