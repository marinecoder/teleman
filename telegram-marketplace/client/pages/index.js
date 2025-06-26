import { useState, useEffect } from 'react'
import Head from 'next/head'
import Layout from '../components/Layout'
import AccountMonitor from '../components/AccountMonitor'
import ScrapingPanel from '../components/ScrapingPanel'
import AnalyticsPanel from '../components/AnalyticsPanel'
import CreditDisplay from '../components/CreditDisplay'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview')
  const [user, setUser] = useState(null)

  useEffect(() => {
    // Initialize user data
    setUser({
      id: 'demo_user',
      name: 'Demo User',
      credits: 1500
    })
  }, [])

  const tabs = [
    { id: 'overview', name: 'Overview', icon: '📊' },
    { id: 'accounts', name: 'Accounts', icon: '👥' },
    { id: 'scraping', name: 'Scraping', icon: '🔍' },
    { id: 'analytics', name: 'Analytics', icon: '📈' },
    { id: 'marketplace', name: 'Marketplace', icon: '🛒' },
    { id: 'settings', name: 'Settings', icon: '⚙️' }
  ]

  return (
    <>
      <Head>
        <title>Telegram Marketplace Dashboard</title>
        <meta name="description" content="Telegram marketplace management dashboard" />
      </Head>

      <Layout>
        <div className="min-h-screen bg-gray-50">
          {/* Header */}
          <header className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center py-4">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    Telegram Marketplace
                  </h1>
                  <p className="text-gray-600">
                    Welcome back, {user?.name || 'User'}
                  </p>
                </div>
                <div className="flex items-center space-x-4">
                  <CreditDisplay credits={user?.credits || 0} />
                  <button className="btn-primary">
                    Buy Credits
                  </button>
                </div>
              </div>
            </div>
          </header>

          {/* Navigation Tabs */}
          <nav className="bg-white border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex space-x-8">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === tab.id
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <span className="mr-2">{tab.icon}</span>
                    {tab.name}
                  </button>
                ))}
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Stats Cards */}
                <div className="card">
                  <h3 className="text-lg font-semibold mb-2">Active Accounts</h3>
                  <div className="text-3xl font-bold text-primary-600">24</div>
                  <p className="text-gray-600">5 new this week</p>
                </div>
                
                <div className="card">
                  <h3 className="text-lg font-semibold mb-2">Members Scraped</h3>
                  <div className="text-3xl font-bold text-success-600">15,432</div>
                  <p className="text-gray-600">+2,341 today</p>
                </div>
                
                <div className="card">
                  <h3 className="text-lg font-semibold mb-2">Active Tasks</h3>
                  <div className="text-3xl font-bold text-warning-600">8</div>
                  <p className="text-gray-600">3 scheduled</p>
                </div>

                {/* Quick Actions */}
                <div className="card lg:col-span-3">
                  <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <button className="btn-primary text-center py-4">
                      <div className="text-2xl mb-2">🔍</div>
                      Start Scraping
                    </button>
                    <button className="btn-secondary text-center py-4">
                      <div className="text-2xl mb-2">👥</div>
                      Add Members
                    </button>
                    <button className="btn-secondary text-center py-4">
                      <div className="text-2xl mb-2">📊</div>
                      View Analytics
                    </button>
                    <button className="btn-secondary text-center py-4">
                      <div className="text-2xl mb-2">⚙️</div>
                      Settings
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'accounts' && <AccountMonitor />}
            {activeTab === 'scraping' && <ScrapingPanel />}
            {activeTab === 'analytics' && <AnalyticsPanel />}
            
            {activeTab === 'marketplace' && (
              <div className="card">
                <h2 className="text-xl font-bold mb-4">Marketplace</h2>
                <p className="text-gray-600">Marketplace features coming soon...</p>
              </div>
            )}
            
            {activeTab === 'settings' && (
              <div className="card">
                <h2 className="text-xl font-bold mb-4">Settings</h2>
                <p className="text-gray-600">Settings panel coming soon...</p>
              </div>
            )}
          </main>
        </div>
      </Layout>
    </>
  )
}
