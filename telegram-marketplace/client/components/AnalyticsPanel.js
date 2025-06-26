import { useState, useEffect } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, BarElement } from 'chart.js'
import { Line, Bar } from 'react-chartjs-2'
import axios from 'axios'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, BarElement)

export default function AnalyticsPanel() {
  const [groupScore, setGroupScore] = useState(null)
  const [scoreForm, setScoreForm] = useState({ groupId: '' })
  const [loading, setLoading] = useState(false)
  const [analyticsData, setAnalyticsData] = useState(null)

  useEffect(() => {
    // Load demo analytics data
    setAnalyticsData({
      memberGrowth: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Members Scraped',
          data: [1200, 1900, 3000, 5000, 7200, 9500],
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4
        }]
      },
      groupDistribution: {
        labels: ['Crypto', 'Trading', 'Tech', 'Gaming', 'Business', 'Other'],
        datasets: [{
          label: 'Groups by Category',
          data: [45, 30, 25, 20, 15, 10],
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(139, 92, 246, 0.8)',
            'rgba(107, 114, 128, 0.8)'
          ]
        }]
      }
    })
  }, [])

  const handleScoreGroup = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await axios.post('http://localhost:8000/analytics/score-group', {
        group_id: scoreForm.groupId
      })
      
      setGroupScore(response.data)
    } catch (error) {
      console.error('Scoring error:', error)
      setGroupScore({
        error: error.response?.data?.detail || 'Failed to score group'
      })
    } finally {
      setLoading(false)
    }
  }

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Total Members</h3>
          <div className="text-2xl font-bold">127,543</div>
          <div className="text-success-600 text-sm">↑ +15.3%</div>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Active Groups</h3>
          <div className="text-2xl font-bold">284</div>
          <div className="text-success-600 text-sm">↑ +8.2%</div>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Avg Group Score</h3>
          <div className="text-2xl font-bold">73.2</div>
          <div className="text-warning-600 text-sm">↓ -2.1%</div>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Success Rate</h3>
          <div className="text-2xl font-bold">89.4%</div>
          <div className="text-success-600 text-sm">↑ +3.7%</div>
        </div>
      </div>

      {/* Group Scoring Tool */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Group Quality Scorer</h2>
        <form onSubmit={handleScoreGroup} className="mb-6">
          <div className="flex space-x-4">
            <input
              type="text"
              value={scoreForm.groupId}
              onChange={(e) => setScoreForm({groupId: e.target.value})}
              placeholder="Enter group ID or username"
              className="input-field flex-1"
              required
            />
            <button
              type="submit"
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Analyzing...' : 'Score Group'}
            </button>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Analyze group engagement, growth, and quality metrics (costs 10 credits)
          </p>
        </form>

        {groupScore && !groupScore.error && (
          <div className="space-y-4">
            <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-primary-900">
                  Group Score: {groupScore.final_score}/100
                </h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  groupScore.final_score >= 80 ? 'bg-success-100 text-success-800' :
                  groupScore.final_score >= 60 ? 'bg-warning-100 text-warning-800' :
                  'bg-danger-100 text-danger-800'
                }`}>
                  {groupScore.final_score >= 80 ? 'Excellent' :
                   groupScore.final_score >= 60 ? 'Good' : 'Poor'}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(groupScore.metrics || {}).map(([metric, score]) => (
                <div key={metric} className="bg-gray-50 rounded-lg p-3">
                  <div className="text-sm font-medium text-gray-700 capitalize">
                    {metric.replace('_', ' ')}
                  </div>
                  <div className="text-xl font-bold">
                    {(score * 100).toFixed(1)}%
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div 
                      className={`h-2 rounded-full ${
                        score >= 0.8 ? 'bg-success-500' :
                        score >= 0.6 ? 'bg-warning-500' : 'bg-danger-500'
                      }`}
                      style={{ width: `${score * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {groupScore?.error && (
          <div className="bg-danger-50 border border-danger-200 rounded-lg p-4">
            <div className="text-danger-700">{groupScore.error}</div>
          </div>
        )}
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Member Growth Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Member Growth Trend</h3>
          {analyticsData?.memberGrowth && (
            <Line data={analyticsData.memberGrowth} options={chartOptions} />
          )}
        </div>

        {/* Group Distribution Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Groups by Category</h3>
          {analyticsData?.groupDistribution && (
            <Bar data={analyticsData.groupDistribution} options={chartOptions} />
          )}
        </div>
      </div>

      {/* Top Performing Groups */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Top Performing Groups</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Group Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Members
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Growth
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {[
                { name: 'Crypto Trading Pro', members: 45230, score: 94.2, growth: 12.3 },
                { name: 'Tech Innovators', members: 38490, score: 91.7, growth: 8.9 },
                { name: 'Business Network', members: 29847, score: 88.4, growth: 15.2 },
                { name: 'Gaming Community', members: 23456, score: 85.1, growth: 6.7 },
                { name: 'Investment Tips', members: 19283, score: 82.9, growth: 9.4 }
              ].map((group, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {group.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {group.members.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      group.score >= 90 ? 'bg-success-100 text-success-800' :
                      group.score >= 80 ? 'bg-warning-100 text-warning-800' :
                      'bg-danger-100 text-danger-800'
                    }`}>
                      {group.score}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <span className="text-success-600">↑ {group.growth}%</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex space-x-2">
                      <button className="text-primary-600 hover:text-primary-900">
                        Analyze
                      </button>
                      <button className="text-success-600 hover:text-success-900">
                        Scrape
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Analytics Reports */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Recent Reports</h3>
        <div className="space-y-3">
          {[
            { title: 'Weekly Growth Report', date: '2 hours ago', status: 'completed' },
            { title: 'Competitor Analysis', date: '5 hours ago', status: 'completed' },
            { title: 'Member Quality Assessment', date: '1 day ago', status: 'completed' },
            { title: 'Market Trend Analysis', date: '2 days ago', status: 'processing' }
          ].map((report, index) => (
            <div key={index} className="flex justify-between items-center py-3 border-b border-gray-100 last:border-b-0">
              <div>
                <div className="font-medium text-gray-900">{report.title}</div>
                <div className="text-sm text-gray-500">{report.date}</div>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`px-2 py-1 rounded-full text-xs ${
                  report.status === 'completed' ? 'bg-success-100 text-success-800' :
                  'bg-warning-100 text-warning-800'
                }`}>
                  {report.status}
                </span>
                <button className="text-primary-600 hover:text-primary-900 text-sm">
                  View
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
