import axios from 'axios'
import io from 'socket.io-client'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Axios instance with default config
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// WebSocket connection
export const socket = io(API_BASE_URL.replace('http', 'ws'), {
  transports: ['websocket'],
  autoConnect: false,
})

// API methods
export const authAPI = {
  login: (phone, code, password) => 
    api.post('/auth/login', { phone, code, password }),
  
  checkStatus: (phone) => 
    api.get(`/auth/status?phone=${phone}`),
}

export const accountsAPI = {
  getStats: () => api.get('/accounts/stats'),
  getBest: () => api.get('/accounts/best'),
  add: (phone, sessionPath, proxy) => 
    api.post('/accounts/add', { phone, session_path: sessionPath, proxy }),
}

export const scrapingAPI = {
  scrapeMembers: (source, limit, filters) =>
    api.post('/scrape/members', { source, limit, filters }),
  
  searchGroups: (query, limit) =>
    api.post('/search/groups', { query, limit }),
}

export const monitoringAPI = {
  getAccountStatus: (phone) => 
    api.get(`/monitoring/status/${phone}`),
  
  getAllStatuses: () => 
    api.get('/monitoring/accounts'),
}

export const analyticsAPI = {
  scoreGroup: (groupId) =>
    api.post('/analytics/score-group', { group_id: groupId }),
}

export const creditsAPI = {
  getBalance: () => api.get('/credits/balance'),
  getPackages: () => api.get('/credits/packages'),
  purchase: (packageName) => api.post('/credits/purchase', { package: packageName }),
}

export const marketplaceAPI = {
  createTransaction: (buyer, seller, amount, description) =>
    api.post('/marketplace/create-transaction', { buyer, seller, amount, description }),
  
  confirmTransaction: (txId, role) =>
    api.post('/marketplace/confirm-transaction', { tx_id: txId, role }),
}

export const bulkAPI = {
  scheduleAddMembers: (group, users, accountsPerHour, timezone) =>
    api.post('/bulk/schedule-add-members', { 
      group, users, accounts_per_hour: accountsPerHour, timezone 
    }),
  
  getTaskStatus: (taskId) =>
    api.get(`/bulk/task-status/${taskId}`),
}

export const gdprAPI = {
  makeRequest: (userId, requestType) =>
    api.post('/gdpr/request', { user_id: userId, request_type: requestType }),
}

export const securityAPI = {
  cleanupSession: (sessionPath) =>
    api.post('/security/cleanup-session', { session_path: sessionPath }),
  
  randomizeFingerprint: () =>
    api.post('/security/randomize-fingerprint'),
}

// Interceptors for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle authentication errors
      console.error('Authentication failed')
    } else if (error.response?.status === 402) {
      // Handle insufficient credits
      console.error('Insufficient credits')
    }
    return Promise.reject(error)
  }
)

export default api
