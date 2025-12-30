import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/api/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  register: (data: any) => api.post('/api/auth/register', data),
  me: () => api.get('/api/auth/me'),
}

export const portfolioAPI = {
  list: (params?: any) => api.get('/api/portfolios', { params }),
  get: (id: number) => api.get(`/api/portfolios/${id}`),
  create: (data: any) => api.post('/api/portfolios', data),
  update: (id: number, data: any) => api.put(`/api/portfolios/${id}`, data),
  delete: (id: number) => api.delete(`/api/portfolios/${id}`),
}

export const positionAPI = {
  list: (portfolioId: number) => api.get(`/api/positions/${portfolioId}/positions`),
  add: (portfolioId: number, data: any) => api.post(`/api/positions/${portfolioId}/positions`, data),
  update: (id: number, data: any) => api.put(`/api/positions/positions/${id}`, data),
  delete: (id: number) => api.delete(`/api/positions/positions/${id}`),
}

export const riskAPI = {
  var: (portfolioId: number, params: any) => api.get(`/api/risk/${portfolioId}/var`, { params }),
  stressTest: (portfolioId: number, data: any) => api.post(`/api/risk/${portfolioId}/stress-test`, data),
  greeks: (portfolioId: number) => api.get(`/api/risk/${portfolioId}/greeks`),
  correlation: (portfolioId: number, params: any) => api.get(`/api/risk/${portfolioId}/correlation`, { params }),
  metrics: (portfolioId: number, params: any) => api.get(`/api/risk/${portfolioId}/metrics`, { params }),
}

export const analyticsAPI = {
  attribution: (portfolioId: number, params: any) => api.get(`/api/analytics/${portfolioId}/attribution`, { params }),
  returns: (portfolioId: number, params: any) => api.get(`/api/analytics/${portfolioId}/returns`, { params }),
  drawdown: (portfolioId: number, params: any) => api.get(`/api/analytics/${portfolioId}/drawdown`, { params }),
  sectorExposure: (portfolioId: number) => api.get(`/api/analytics/${portfolioId}/exposure/sector`),
  factorExposure: (portfolioId: number, params: any) => api.get(`/api/analytics/${portfolioId}/exposure/factor`, { params }),
}

export const optimizationAPI = {
  optimize: (portfolioId: number, data: any) => api.post(`/api/optimization/${portfolioId}`, data),
  efficientFrontier: (portfolioId: number, params: any) => api.get(`/api/optimization/${portfolioId}/efficient-frontier`, { params }),
  rebalance: (portfolioId: number, data: any) => api.post(`/api/optimization/${portfolioId}/rebalance`, data),
}

export const orderAPI = {
  list: (params?: any) => api.get('/api/orders', { params }),
  get: (id: number) => api.get(`/api/orders/${id}`),
  create: (data: any) => api.post('/api/orders', data),
  execute: (id: number) => api.post(`/api/orders/${id}/execute`),
  cancel: (id: number) => api.put(`/api/orders/${id}/cancel`),
}

export const complianceAPI = {
  rules: () => api.get('/api/compliance/rules'),
  createRule: (data: any) => api.post('/api/compliance/rules', data),
  check: (portfolioId: number, data: any) => api.post(`/api/compliance/${portfolioId}/check`, data),
  preTradeCheck: (data: any) => api.post('/api/compliance/pre-trade-check', data),
  violations: (params?: any) => api.get('/api/compliance/violations', { params }),
  resolveViolation: (id: number, notes: string) => api.put(`/api/compliance/violations/${id}/resolve`, { notes }),
}

export const reportAPI = {
  performance: (portfolioId: number, data: any) => api.post(`/api/reports/${portfolioId}/performance`, data),
  holdings: (portfolioId: number, data: any) => api.post(`/api/reports/${portfolioId}/holdings`, data),
  risk: (portfolioId: number, data: any) => api.post(`/api/reports/${portfolioId}/risk`, data),
  tax: (portfolioId: number, taxYear: number) => api.post(`/api/reports/${portfolioId}/tax`, { tax_year: taxYear }),
  download: (portfolioId: number, reportId: string) => api.get(`/api/reports/${portfolioId}/download/${reportId}`, { responseType: 'blob' }),
}

export const aiAPI = {
  alphaSignals: (params: any) => api.get('/api/ai/alpha-signals', { params }),
  regimeDetection: (params: any) => api.get('/api/ai/regime-detection', { params }),
  sentiment: (data: any) => api.post('/api/ai/sentiment', data),
  recommendations: (portfolioId: number) => api.get(`/api/ai/${portfolioId}/recommendations`),
  retrainModels: (modelType: string) => api.post('/api/ai/models/retrain', null, { params: { model_type: modelType } }),
}
