import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { Link } from 'react-router-dom'
import { portfolioAPI } from '../lib/api'
import { Plus, Search, TrendingUp, Calendar, DollarSign, MoreVertical, Edit, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

const Portfolios = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: portfolios, isLoading } = useQuery('portfolios', () => portfolioAPI.list())

  const filteredPortfolios = portfolios?.data?.filter((p: any) =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Portfolios</h1>
          <p className="text-gray-400 mt-1">Manage your investment portfolios</p>
        </div>
        <button 
          onClick={() => setShowCreateModal(true)}
          className="btn-primary"
        >
          <Plus size={18} className="mr-2" />
          Create Portfolio
        </button>
      </div>

      <div className="card">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search portfolios..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPortfolios.map((portfolio: any) => (
            <Link
              key={portfolio.id}
              to={`/portfolios/${portfolio.id}`}
              className="card hover:border-primary-600 transition-all cursor-pointer group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-white group-hover:text-primary-500 transition-colors">
                    {portfolio.name}
                  </h3>
                  <p className="text-sm text-gray-400 mt-1">{portfolio.strategy || 'No strategy'}</p>
                </div>
                <button className="p-2 hover:bg-dark-800 rounded-lg">
                  <MoreVertical size={18} className="text-gray-400" />
                </button>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400 flex items-center">
                    <DollarSign size={16} className="mr-1" />
                    AUM
                  </span>
                  <span className="text-lg font-semibold text-white">
                    ${portfolio.aum ? (portfolio.aum / 1000000).toFixed(2) : '0'}M
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400 flex items-center">
                    <Calendar size={16} className="mr-1" />
                    Inception
                  </span>
                  <span className="text-sm text-gray-300">
                    {new Date(portfolio.inception_date).toLocaleDateString()}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400 flex items-center">
                    <TrendingUp size={16} className="mr-1" />
                    Benchmark
                  </span>
                  <span className="text-sm text-gray-300">{portfolio.benchmark || 'SPY'}</span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-dark-800 flex items-center justify-between">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  portfolio.is_active ? 'bg-primary-900 text-primary-300' : 'bg-gray-800 text-gray-400'
                }`}>
                  {portfolio.is_active ? 'Active' : 'Inactive'}
                </span>
                <span className="text-xs text-gray-500">ID: {portfolio.id}</span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {showCreateModal && <CreatePortfolioModal onClose={() => setShowCreateModal(false)} />}
    </div>
  )
}

const CreatePortfolioModal = ({ onClose }: { onClose: () => void }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    strategy: '',
    benchmark: 'SPY',
    inception_date: new Date().toISOString().split('T')[0],
    base_currency: 'USD',
    aum: '',
  })

  const queryClient = useQueryClient()
  const createMutation = useMutation(
    (data: any) => portfolioAPI.create(data),
    {
      onSuccess: () => {
        toast.success('Portfolio created successfully')
        queryClient.invalidateQueries('portfolios')
        onClose()
      },
      onError: () => {
        toast.error('Failed to create portfolio')
      },
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      ...formData,
      aum: formData.aum ? parseFloat(formData.aum) : null,
    })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-dark-900 rounded-xl p-6 max-w-md w-full mx-4 border border-dark-800">
        <h2 className="text-2xl font-bold text-white mb-6">Create New Portfolio</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="input-group">
            <label className="label">Portfolio Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="w-full"
            />
          </div>

          <div className="input-group">
            <label className="label">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="input-group">
              <label className="label">Strategy</label>
              <select
                value={formData.strategy}
                onChange={(e) => setFormData({ ...formData, strategy: e.target.value })}
                className="w-full"
              >
                <option value="">Select strategy</option>
                <option value="long_equity">Long Equity</option>
                <option value="balanced">Balanced</option>
                <option value="fixed_income">Fixed Income</option>
                <option value="alternative">Alternative</option>
              </select>
            </div>

            <div className="input-group">
              <label className="label">Benchmark</label>
              <input
                type="text"
                value={formData.benchmark}
                onChange={(e) => setFormData({ ...formData, benchmark: e.target.value })}
                className="w-full"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="input-group">
              <label className="label">Inception Date</label>
              <input
                type="date"
                value={formData.inception_date}
                onChange={(e) => setFormData({ ...formData, inception_date: e.target.value })}
                className="w-full"
              />
            </div>

            <div className="input-group">
              <label className="label">Currency</label>
              <select
                value={formData.base_currency}
                onChange={(e) => setFormData({ ...formData, base_currency: e.target.value })}
                className="w-full"
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
              </select>
            </div>
          </div>

          <div className="input-group">
            <label className="label">Initial AUM</label>
            <input
              type="number"
              value={formData.aum}
              onChange={(e) => setFormData({ ...formData, aum: e.target.value })}
              placeholder="1000000"
              className="w-full"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" disabled={createMutation.isLoading} className="btn-primary flex-1">
              {createMutation.isLoading ? 'Creating...' : 'Create Portfolio'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Portfolios
