import { ref, reactive } from 'vue'

class WebSocketService {
  constructor() {
    this.socket = null
    this.isConnected = ref(false)
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.listeners = new Map()
    this.messageQueue = []
  }

  connect(apiKey) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      try {
        const wsUrl = import.meta.env.VITE_WS_URL || `ws://${window.location.hostname}:8000`
        const url = `${wsUrl}/ws/dashboard?api_key=${apiKey}`
        
        this.socket = new WebSocket(url)

        this.socket.onopen = () => {
          console.log('🟢 WebSocket connected successfully to:', url)
          this.isConnected.value = true
          this.reconnectAttempts = 0
          
          // Send queued messages
          while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift()
            this.socket.send(JSON.stringify(message))
          }
          
          // Send ping to keep connection alive
          this.startHeartbeat()
          
          resolve()
        }

        this.socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            console.log('📩 WebSocket message received:', data)
            console.log('📩 Message type:', data.type, 'for task:', data.task_id)
            this.handleMessage(data)
          } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error)
          }
        }

        this.socket.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          this.isConnected.value = false
          this.stopHeartbeat()
          
          // Attempt to reconnect if not a normal closure
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnect(apiKey)
          }
        }

        this.socket.onerror = (error) => {
          console.error('❌ WebSocket connection error:', error)
          console.log('🔍 Attempted URL:', url)
          reject(error)
        }

      } catch (error) {
        reject(error)
      }
    })
  }

  reconnect(apiKey) {
    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`)
    
    setTimeout(() => {
      this.connect(apiKey).catch(() => {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          console.error('Max reconnection attempts reached')
          this.emit('connection_failed')
        }
      })
    }, delay)
  }

  disconnect() {
    this.stopHeartbeat()
    if (this.socket) {
      this.socket.close(1000, 'Client disconnect')
      this.socket = null
    }
    this.isConnected.value = false
  }

  send(message) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message))
    } else {
      // Queue message for when connection is established
      this.messageQueue.push(message)
    }
  }

  sendUserInput(taskId, machineId, input) {
    const message = {
      type: 'user_input',
      task_id: taskId,
      machine_id: machineId,
      input: input
    }
    this.send(message)
  }

  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' })
      }
    }, 30000) // 30 seconds
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  handleMessage(data) {
    const { type } = data
    
    // Handle system messages
    if (type === 'pong') {
      return // Heartbeat response
    }
    
    // Emit to listeners
    this.emit(type, data)
    this.emit('message', data)
  }

  // Event listener management
  on(event, callback) {
    console.log(`🔧 Registering WebSocket listener for event: "${event}"`)
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
    console.log(`✅ WebSocket listener registered. Total listeners for "${event}": ${this.listeners.get(event).length}`)
    console.log(`📊 Total event types registered: ${this.listeners.size}`)
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  emit(event, data) {
    const listenerCount = this.listeners.has(event) ? this.listeners.get(event).length : 0
    console.log(`📡 Emitting WebSocket event "${event}" to ${listenerCount} listeners`)
    console.log('📋 All registered listeners:', Array.from(this.listeners.keys()))
    console.log('📦 Event data:', data)
    
    if (listenerCount === 0 && event !== 'pong') {
      console.warn(`⚠️ No listeners registered for event "${event}"`)
      console.log('📋 Available event listeners:', Array.from(this.listeners.keys()))
      
      // Additional debugging for empty listeners
      if (this.listeners.size === 0) {
        console.error('🔴 NO EVENT LISTENERS REGISTERED AT ALL! Component may not be mounted properly.')
      } else {
        console.log(`ℹ️ Total listeners registered: ${this.listeners.size}`)
      }
    }
    
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach((callback, index) => {
        try {
          console.log(`📤 Calling listener ${index + 1}/${listenerCount} for event "${event}"`)
          callback(data)
          console.log(`✅ Listener ${index + 1} executed successfully`)
        } catch (error) {
          console.error(`❌ Error in WebSocket event listener ${index + 1} for event "${event}":`, error)
        }
      })
    }
  }
}

// Create singleton instance
export const websocketService = new WebSocketService()

// Composable for Vue components
export function useWebSocket() {
  return {
    isConnected: websocketService.isConnected,
    connect: (apiKey) => websocketService.connect(apiKey),
    disconnect: () => websocketService.disconnect(),
    send: (message) => websocketService.send(message),
    sendUserInput: (taskId, machineId, input) => websocketService.sendUserInput(taskId, machineId, input),
    on: (event, callback) => websocketService.on(event, callback),
    off: (event, callback) => websocketService.off(event, callback)
  }
}

export default websocketService