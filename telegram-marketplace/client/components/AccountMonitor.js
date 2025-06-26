import { useState, useEffect } from 'react'
import axios from 'axios'

export default function AccountMonitor() {
  const [accounts, setAccounts] = useState([])
  const [stats, setStats] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAccountData()
    const interval = setInterval(fetchAccountData, 15000) // Update every 15 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchAccountData = async () => {
    try {
      const [statsResponse, accountsResponse] = await Promise.all([
        axios.get('http://localhost:8000/accounts/stats'),
        axios.get('http://localhost:8000/monitoring/accounts')
      ])
      
      setStats(statsResponse.data)
      // Mock account data for demo
      setAccounts([
        { phone: '+1234567890', status: 'LIVE', success_rate: 0.95, last_used: Date.now() - 3600000 },
        { phone: '+1234567891', status: 'LIVE', success_rate: 0.88, last_used: Date.now() - 7200000 },
        { phone: '+1234567892', status: 'BANNED', success_rate: 0.12, last_used: Date.now() - 86400000 },
        { phone: '+1234567893', status: 'LIVE', success_rate: 0.92, last_used: Date.now() - 1800000 },
        { phone: '+1234567894', status: 'ERROR', success_rate: 0.0, last_used: Date.now() - 43200000 }
      ])
      setLoading(false)
    } catch (error) {
      console.error('Error fetching account data:', error)
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const statusClasses = {
      'LIVE': 'status-live',
      'BANNED': 'status-banned',
      'ERROR': 'status-error',
      'UNAUTHORIZED': 'status-error'
    }
    return statusClasses[status] || 'status-error'
  }

  const formatLastUsed = (timestamp) => {
    const now = Date.now()
    const diff = now - timestamp
    const hours = Math.floor(diff / 3600000)
    const minutes = Math.floor((diff % 3600000) / 60000)
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ago`
    }
    return `${minutes}m ago`
  }

  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            <div className="h-4 bg-gray-200 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Account Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Total Accounts</h3>
          <div className="text-2xl font-bold">{stats.total_accounts || accounts.length}</div>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Live Accounts</h3>
          <div className="text-2xl font-bold text-success-600">
            {accounts.filter(acc => acc.status === 'LIVE').length}
          </div>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Banned Accounts</h3>
          <div className="text-2xl font-bold text-danger-600">
            {accounts.filter(acc => acc.status === 'BANNED').length}
          </div>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Avg Success Rate</h3>
          <div className="text-2xl font-bold">
            {((accounts.reduce((sum, acc) => sum + acc.success_rate, 0) / accounts.length) * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Account List */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Account Status</h2>
          <button 
            onClick={fetchAccountData}
            className="btn-secondary"
          >
            🔄 Refresh
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Phone Number
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Success Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Used
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {accounts.map((account) => (
                <tr key={account.phone} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {account.phone}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={getStatusBadge(account.status)}>
                      {account.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            account.success_rate > 0.8 ? 'bg-success-500' :
                            account.success_rate > 0.5 ? 'bg-warning-500' : 'bg-danger-500'
                          }`}
                          style={{ width: `${account.success_rate * 100}%` }}
                        ></div>
                      </div>
                      <span className="ml-2">{(account.success_rate * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatLastUsed(account.last_used)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex space-x-2">
                      <button className="text-primary-600 hover:text-primary-900">
                        View
                      </button>
                      {account.status === 'BANNED' && (
                        <button className="text-warning-600 hover:text-warning-900">
                          Recover
                        </button>
                      )}
                      <button className="text-danger-600 hover:text-danger-900">
                        Remove
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Real-time Activity Feed */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
        <div className="space-y-3">
          <div className="flex items-center space-x-3 text-sm">
            <div className="w-2 h-2 bg-success-500 rounded-full"></div>
            <span className="text-gray-600">+1234567890</span>
            <span>scraped 150 members from @example_group</span>
            <span className="text-gray-400">2 minutes ago</span>
          </div>
          <div className="flex items-center space-x-3 text-sm">
            <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
            <span className="text-gray-600">+1234567891</span>
            <span>hit rate limit, switching proxy</span>
            <span className="text-gray-400">5 minutes ago</span>
          </div>
          <div className="flex items-center space-x-3 text-sm">
            <div className="w-2 h-2 bg-success-500 rounded-full"></div>
            <span className="text-gray-600">+1234567892</span>
            <span>successfully joined @target_group</span>
            <span className="text-gray-400">8 minutes ago</span>
          </div>
        </div>
      </div>
    </div>
  )
}
