import { useState, useEffect } from 'react'
import io from 'socket.io-client'

export default function Layout({ children }) {
  const [isConnected, setIsConnected] = useState(false)
  const [socket, setSocket] = useState(null)

  useEffect(() => {
    // Initialize WebSocket connection for real-time updates
    const socketInstance = io('ws://localhost:8000', {
      transports: ['websocket']
    })

    socketInstance.on('connect', () => {
      setIsConnected(true)
    })

    socketInstance.on('disconnect', () => {
      setIsConnected(false)
    })

    setSocket(socketInstance)

    return () => socketInstance.close()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Connection Status */}
      <div className={`fixed top-0 right-0 m-4 px-3 py-1 rounded-full text-sm font-medium z-50 ${
        isConnected 
          ? 'bg-success-100 text-success-800' 
          : 'bg-danger-100 text-danger-800'
      }`}>
        {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
      </div>

      {children}
    </div>
  )
}
