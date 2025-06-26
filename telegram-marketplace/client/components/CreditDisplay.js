import { useState, useEffect } from 'react'
import axios from 'axios'

export default function CreditDisplay({ credits }) {
  const [showPurchaseModal, setShowPurchaseModal] = useState(false)
  const [packages, setPackages] = useState({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchPackages()
  }, [])

  const fetchPackages = async () => {
    try {
      const response = await axios.get('http://localhost:8000/credits/packages')
      setPackages(response.data)
    } catch (error) {
      console.error('Error fetching packages:', error)
    }
  }

  const purchaseCredits = async (packageName) => {
    setLoading(true)
    try {
      const response = await axios.post('http://localhost:8000/credits/purchase', {
        package: packageName
      })
      
      if (response.data.status === 'success') {
        alert('Credits purchased successfully!')
        setShowPurchaseModal(false)
        // Refresh credits in parent component
        window.location.reload()
      }
    } catch (error) {
      console.error('Purchase error:', error)
      alert('Purchase failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getCreditColor = (creditAmount) => {
    if (creditAmount >= 1000) return 'text-success-600'
    if (creditAmount >= 500) return 'text-warning-600'
    return 'text-danger-600'
  }

  return (
    <>
      <div className="flex items-center space-x-2">
        <div className="text-sm text-gray-600">Credits:</div>
        <div className={`text-lg font-bold ${getCreditColor(credits)}`}>
          {credits.toLocaleString()}
        </div>
        <button 
          onClick={() => setShowPurchaseModal(true)}
          className="text-primary-600 hover:text-primary-800 text-sm"
        >
          Buy More
        </button>
      </div>

      {/* Purchase Modal */}
      {showPurchaseModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Purchase Credits</h2>
              <button 
                onClick={() => setShowPurchaseModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              {Object.entries(packages).map(([packageName, packageInfo]) => (
                <div 
                  key={packageName}
                  className="border rounded-lg p-4 hover:border-primary-300 transition-colors"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold capitalize">{packageName}</h3>
                      <div className="text-2xl font-bold text-primary-600">
                        {packageInfo.credits.toLocaleString()} Credits
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold">${packageInfo.price}</div>
                      <div className="text-sm text-gray-500">
                        ${(packageInfo.price / packageInfo.credits * 1000).toFixed(2)}/1000 credits
                      </div>
                    </div>
                  </div>
                  
                  {packageName === 'premium' && (
                    <div className="bg-primary-50 text-primary-700 text-sm px-2 py-1 rounded mb-2">
                      Most Popular
                    </div>
                  )}
                  
                  <button
                    onClick={() => purchaseCredits(packageName)}
                    disabled={loading}
                    className="btn-primary w-full"
                  >
                    {loading ? 'Processing...' : `Purchase ${packageName}`}
                  </button>
                </div>
              ))}
            </div>

            <div className="mt-6 text-center text-sm text-gray-500">
              <p>💳 Secure payment processing</p>
              <p>⚡ Credits added instantly</p>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
