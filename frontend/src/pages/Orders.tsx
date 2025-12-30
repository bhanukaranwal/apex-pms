import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { orderAPI, portfolioAPI } from '../lib/api'
import { Plus, TrendingUp, Clock, CheckCircle, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'

const Orders = () => {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [statusFilter, setStatusFilter] = useState('')
  const queryClient = useQueryClient()

  const { data: orders, isLoading } = useQuery('orders', () => orderAPI.list())

  const executeMutation = useMutation(
    (orderId: number) => orderAPI.execute(orderId),
    {
      onSuccess: () => {
        toast.success('Order executed successfully')
        queryClient.invalidateQueries('orders')
      },
      onError: () => {
        toast.error('Failed to execute order')
      },
    }
  )

  const cancelMutation = useMutation(
    (orderId: number) => orderAPI.cancel(orderId),
    {
      onSuccess: () => {
        toast.success('Order cancelled')
        queryClient.invalidateQueries('orders')
      },
      onError: () => {
        toast.error('Failed to cancel order')
      },
    }
  )

  const filteredOrders = orders?.data?.filter((o: any) => 
    !statusFilter || o.status === statusFilter
  ) || []

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'filled': return 'bg-green-900 text-green-300'
      case 'pending': return 'bg-yellow-900 text-yellow-300'
      case 'submitted': return 'bg-blue-900 text-blue-300'
      case 'cancelled': return 'bg-gray-800 text-gray-400'
      case 'rejected': return 'bg-red-900 text-red-300'
      default: return 'bg-gray-800 text-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'filled': return <CheckCircle size={16} />
      case 'pending': return <Clock size={16} />
      case 'cancelled': return <XCircle size={16} />
      case 'rejected': return <XCircle size={16} />
      default: return <Clock size={16} />
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Orders</h1>
          <p className="text-gray-400 mt-1">Manage and execute trading orders</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="btn-primary">
          <Plus size={18} className="mr-2" />
          Create Order
        </button>
      </div>

      <div className="card">
        <div className="flex gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="flex-1"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="submitted">Submitted</option>
            <option value="filled">Filled</option>
            <option value="partially_filled">Partially Filled</option>
            <option value="cancelled">Cancelled</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-dark-800">
              <tr>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">ID</th>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Ticker</th>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Type</th>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Side</th>
                <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Quantity</th>
                <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Price</th>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Status</th>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Created</th>
                <th className="text-right py-3 px-2 text-sm font-medium text-gray-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredOrders.map((order: any) => (
                <tr key={order.id} className="border-b border-dark-800 hover:bg-dark-800">
                  <td className="py-3 px-2 text-gray-400">#{order.id}</td>
                  <td className="py-3 px-2 font-medium text-white">{order.ticker}</td>
                  <td className="py-3 px-2 text-gray-300">{order.order_type}</td>
                  <td className="py-3 px-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      order.side === 'buy' ? 'bg-primary-900 text-primary-300' : 'bg-red-900 text-red-300'
                    }`}>
                      {order.side.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 px-2 text-right text-gray-300">{parseFloat(order.quantity).toFixed(2)}</td>
                  <td className="py-3 px-2 text-right text-gray-300">
                    ${order.price ? parseFloat(order.price).toFixed(2) : 'Market'}
                  </td>
                  <td className="py-3 px-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1 w-fit ${getStatusColor(order.status)}`}>
                      {getStatusIcon(order.status)}
                      {order.status}
                    </span>
                  </td>
                  <td className="py-3 px-2 text-gray-400 text-sm">
                    {new Date(order.created_at).toLocaleString()}
                  </td>
                  <td className="py-3 px-2 text-right">
                    <div className="flex gap-2 justify-end">
                      {order.status === 'pending' && (
                        <button
                          onClick={() => executeMutation.mutate(order.id)}
                          className="px-3 py-1 bg-primary-600 hover:bg-primary-700 text-white text-sm rounded"
                        >
                          Execute
                        </button>
                      )}
                      {(order.status === 'pending' || order.status === 'submitted') && (
                        <button
                          onClick={() => cancelMutation.mutate(order.id)}
                          className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showCreateModal && <CreateOrderModal onClose={() => setShowCreateModal(false)} />}
    </div>
  )
}

const CreateOrderModal = ({ onClose }: { onClose: () => void }) => {
  const [formData, setFormData] = useState({
    portfolio_id: '',
    ticker: '',
    order_type: 'market',
    side: 'buy',
    quantity: '',
    price: '',
    broker: 'alpaca',
  })

  const { data: portfolios } = useQuery('portfolios', () => portfolioAPI.list())
  const queryClient = useQueryClient()

  const createMutation = useMutation(
    (data: any) => orderAPI.create(data),
    {
      onSuccess: () => {
        toast.success('Order created successfully')
        queryClient.invalidateQueries('orders')
        onClose()
      },
      onError: () => {
        toast.error('Failed to create order')
      },
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      ...formData,
      portfolio_id: parseInt(formData.portfolio_id),
      quantity: parseFloat(formData.quantity),
      price: formData.price ? parseFloat(formData.price) : null,
    })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-dark-900 rounded-xl p-6 max-w-md w-full mx-4 border border-dark-800">
        <h2 className="text-2xl font-bold text-white mb-6">Create New Order</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="input-group">
            <label className="label">Portfolio *</label>
            <select
              value={formData.portfolio_id}
              onChange={(e) => setFormData({ ...formData, portfolio_id: e.target.value })}
              required
              className="w-full"
            >
              <option value="">Select portfolio</option>
              {portfolios?.data?.map((p: any) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="input-group">
              <label className="label">Ticker *</label>
              <input
                type="text"
                value={formData.ticker}
                onChange={(e) => setFormData({ ...formData, ticker: e.target.value.toUpperCase() })}
                required
                placeholder="AAPL"
                className="w-full"
              />
            </div>

            <div className="input-group">
              <label className="label">Side *</label>
              <select
                value={formData.side}
                onChange={(e) => setFormData({ ...formData, side: e.target.value })}
                className="w-full"
              >
                <option value="buy">Buy</option>
                <option value="sell">Sell</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="input-group">
              <label className="label">Order Type *</label>
              <select
                value={formData.order_type}
                onChange={(e) => setFormData({ ...formData, order_type: e.target.value })}
                className="w-full"
              >
                <option value="market">Market</option>
                <option value="limit">Limit</option>
                <option value="stop">Stop</option>
                <option value="stop_limit">Stop Limit</option>
              </select>
            </div>

            <div className="input-group">
              <label className="label">Quantity *</label>
              <input
                type="number"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                required
                step="0.01"
                placeholder="100"
                className="w-full"
              />
            </div>
          </div>

          {(formData.order_type === 'limit' || formData.order_type === 'stop_limit') && (
            <div className="input-group">
              <label className="label">Limit Price</label>
              <input
                type="number"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                step="0.01"
                placeholder="150.00"
                className="w-full"
              />
            </div>
          )}

          <div className="input-group">
            <label className="label">Broker</label>
            <select
              value={formData.broker}
              onChange={(e) => setFormData({ ...formData, broker: e.target.value })}
              className="w-full"
            >
              <option value="alpaca">Alpaca</option>
              <option value="interactive_brokers">Interactive Brokers</option>
            </select>
          </div>

          <div className="flex gap-3 pt-4">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" disabled={createMutation.isLoading} className="btn-primary flex-1">
              {createMutation.isLoading ? 'Creating...' : 'Create Order'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Orders
