import { useState } from 'react'
import axios from 'axios'

export default function ScrapingPanel() {
  const [scrapeForm, setScrapeForm] = useState({
    source: '',
    limit: 500,
    filters: {
      premium_only: false,
      has_username: false,
      online_only: false
    }
  })
  const [searchForm, setSearchForm] = useState({
    query: '',
    limit: 50
  })
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [activeTab, setActiveTab] = useState('scrape')

  const handleScrape = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await axios.post('http://localhost:8000/scrape/members', {
        source: scrapeForm.source,
        limit: scrapeForm.limit
      })
      
      setResults({
        type: 'scrape',
        data: response.data
      })
    } catch (error) {
      console.error('Scraping error:', error)
      setResults({
        type: 'error',
        message: error.response?.data?.detail || 'Scraping failed'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await axios.post('http://localhost:8000/search/groups', {
        query: searchForm.query,
        limit: searchForm.limit
      })
      
      setResults({
        type: 'search',
        data: response.data
      })
    } catch (error) {
      console.error('Search error:', error)
      setResults({
        type: 'error',
        message: error.response?.data?.detail || 'Search failed'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="card">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('scrape')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'scrape'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Member Scraping
            </button>
            <button
              onClick={() => setActiveTab('search')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'search'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Group Search
            </button>
          </nav>
        </div>

        <div className="pt-6">
          {/* Member Scraping Tab */}
          {activeTab === 'scrape' && (
            <form onSubmit={handleScrape} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Source Group/Channel
                </label>
                <input
                  type="text"
                  value={scrapeForm.source}
                  onChange={(e) => setScrapeForm({...scrapeForm, source: e.target.value})}
                  placeholder="@groupname or https://t.me/groupname"
                  className="input-field"
                  required
                />
                <p className="text-sm text-gray-500 mt-1">
                  Enter group username or Telegram link
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Member Limit
                </label>
                <input
                  type="number"
                  value={scrapeForm.limit}
                  onChange={(e) => setScrapeForm({...scrapeForm, limit: parseInt(e.target.value)})}
                  min="1"
                  max="10000"
                  className="input-field"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Maximum number of members to scrape (costs 5 credits)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Filters
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={scrapeForm.filters.premium_only}
                      onChange={(e) => setScrapeForm({
                        ...scrapeForm,
                        filters: {...scrapeForm.filters, premium_only: e.target.checked}
                      })}
                      className="mr-2"
                    />
                    Premium users only
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={scrapeForm.filters.has_username}
                      onChange={(e) => setScrapeForm({
                        ...scrapeForm,
                        filters: {...scrapeForm.filters, has_username: e.target.checked}
                      })}
                      className="mr-2"
                    />
                    Users with usernames only
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={scrapeForm.filters.online_only}
                      onChange={(e) => setScrapeForm({
                        ...scrapeForm,
                        filters: {...scrapeForm.filters, online_only: e.target.checked}
                      })}
                      className="mr-2"
                    />
                    Recently active users only
                  </label>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full"
              >
                {loading ? 'Scraping...' : 'Start Scraping'}
              </button>
            </form>
          )}

          {/* Group Search Tab */}
          {activeTab === 'search' && (
            <form onSubmit={handleSearch} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search Query
                </label>
                <input
                  type="text"
                  value={searchForm.query}
                  onChange={(e) => setSearchForm({...searchForm, query: e.target.value})}
                  placeholder="cryptocurrency, trading, etc."
                  className="input-field"
                  required
                />
                <p className="text-sm text-gray-500 mt-1">
                  Search for public groups and channels (costs 2 credits)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Result Limit
                </label>
                <input
                  type="number"
                  value={searchForm.limit}
                  onChange={(e) => setSearchForm({...searchForm, limit: parseInt(e.target.value)})}
                  min="1"
                  max="100"
                  className="input-field"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full"
              >
                {loading ? 'Searching...' : 'Search Groups'}
              </button>
            </form>
          )}
        </div>
      </div>

      {/* Results Display */}
      {results && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Results</h3>
          
          {results.type === 'error' && (
            <div className="bg-danger-50 border border-danger-200 rounded-lg p-4">
              <div className="flex">
                <div className="text-danger-500">❌</div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-danger-800">
                    Error
                  </h3>
                  <div className="mt-2 text-sm text-danger-700">
                    {results.message}
                  </div>
                </div>
              </div>
            </div>
          )}

          {results.type === 'scrape' && (
            <div>
              <div className="mb-4">
                <span className="text-success-600 font-medium">
                  ✅ Successfully scraped {results.data.members_scraped} members from {results.data.source}
                </span>
              </div>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Username
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {results.data.members?.slice(0, 20).map((member) => (
                      <tr key={member.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {member.id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {member.username || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {[member.first_name, member.last_name].filter(Boolean).join(' ') || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            member.is_premium ? 'bg-primary-100 text-primary-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {member.is_premium ? 'Premium' : 'Regular'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {results.data.members?.length > 20 && (
                <div className="mt-4 text-center">
                  <button className="btn-secondary">
                    Show All {results.data.members_scraped} Members
                  </button>
                </div>
              )}
            </div>
          )}

          {results.type === 'search' && (
            <div>
              <div className="mb-4">
                <span className="text-success-600 font-medium">
                  ✅ Found {results.data.results?.length || 0} groups for "{results.data.query}"
                </span>
              </div>
              
              <div className="grid gap-4">
                {results.data.results?.map((group) => (
                  <div key={group.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium text-gray-900">{group.title}</h4>
                        <p className="text-gray-600">@{group.username}</p>
                        <p className="text-sm text-gray-500 mt-1">
                          {group.participants_count?.toLocaleString()} members • {group.type}
                        </p>
                        {group.verified && (
                          <span className="inline-block mt-1 px-2 py-1 text-xs bg-primary-100 text-primary-800 rounded-full">
                            ✓ Verified
                          </span>
                        )}
                      </div>
                      <div className="flex space-x-2">
                        <button className="btn-secondary text-sm">
                          View Info
                        </button>
                        <button className="btn-primary text-sm">
                          Scrape Members
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
