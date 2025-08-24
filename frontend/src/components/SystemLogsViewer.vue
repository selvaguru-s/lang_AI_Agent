<template>
  <div class="system-logs-viewer">
    <!-- Header Controls -->
    <div class="logs-header">
      <div class="header-title">
        <div class="logs-icon">📟</div>
        <h3>System Logs</h3>
        <div class="connection-status" :class="getConnectionStatusClass()">
          <div class="status-dot"></div>
          <span>{{ getConnectionStatusText() }}</span>
        </div>
      </div>
      
      <div class="logs-controls">
        <div class="filter-tabs">
          <button 
            v-for="source in logSources" 
            :key="source.id"
            @click="activeLogSource = source.id"
            :class="['filter-tab', { active: activeLogSource === source.id }]"
          >
            <span class="source-icon">{{ source.icon }}</span>
            <span>{{ source.label }}</span>
            <span v-if="getLogCount(source.id) > 0" class="log-count">{{ getLogCount(source.id) }}</span>
          </button>
        </div>
        
        <div class="control-buttons">
          <button @click="clearLogs" class="control-btn clear-btn" title="Clear all logs">
            <span>🗑️</span>
          </button>
          <button @click="toggleAutoScroll" class="control-btn" :class="{ active: autoScroll }" title="Toggle auto-scroll">
            <span>{{ autoScroll ? '📌' : '📍' }}</span>
          </button>
          <button @click="exportLogs" class="control-btn" title="Export logs">
            <span>💾</span>
          </button>
          <button @click="toggleFullscreen" class="control-btn" title="Toggle fullscreen">
            <span>{{ isFullscreen ? '🔳' : '⛶' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Log Display Area -->
    <div 
      class="logs-container" 
      :class="{ fullscreen: isFullscreen }"
      ref="logsContainer"
    >
      <div class="terminal-window" ref="terminalWindow">
        <div class="terminal-header">
          <div class="terminal-title">
            <span class="source-badge" :class="activeLogSource">
              {{ getActiveSourceLabel() }}
            </span>
            <span class="log-time-range">
              {{ getTimeRange() }}
            </span>
          </div>
          <div class="terminal-stats">
            <span>{{ getFilteredLogs().length }} entries</span>
            <span v-if="isLive" class="live-indicator">🔴 LIVE</span>
          </div>
        </div>
        
        <div class="terminal-content" ref="terminalContent">
          <!-- Loading state -->
          <div v-if="isLoading" class="loading-logs">
            <div class="loading-spinner"></div>
            <span>Loading system logs...</span>
          </div>
          
          <!-- Empty state -->
          <div v-else-if="getFilteredLogs().length === 0" class="empty-logs">
            <div class="empty-icon">📝</div>
            <p>No {{ getActiveSourceLabel().toLowerCase() }} logs available</p>
            <small>Logs will appear here as system events occur</small>
          </div>
          
          <!-- Log entries -->
          <div v-else class="log-entries">
            <div 
              v-for="(log, index) in getFilteredLogs()" 
              :key="`${log.source}-${log.timestamp}-${index}`"
              class="log-entry"
              :class="getLogEntryClass(log)"
            >
              <div class="log-timestamp">
                {{ formatLogTime(log.timestamp) }}
              </div>
              <div class="log-source-tag" :class="log.source">
                {{ log.source.toUpperCase() }}
              </div>
              <div class="log-level" :class="log.level">
                {{ getLogLevelIcon(log.level) }}
              </div>
              <div class="log-message">
                <div class="message-content">
                  {{ log.message }}
                </div>
                <div v-if="log.details" class="message-details">
                  <pre>{{ typeof log.details === 'object' ? JSON.stringify(log.details, null, 2) : log.details }}</pre>
                </div>
                <div v-if="log.context" class="message-context">
                  <div class="context-item" v-for="(value, key) in log.context" :key="key">
                    <span class="context-key">{{ key }}:</span>
                    <span class="context-value">{{ value }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Log Details Modal -->
    <div v-if="selectedLog" class="log-modal-overlay" @click="closeLogDetails">
      <div class="log-modal" @click.stop>
        <div class="log-modal-header">
          <h4>Log Entry Details</h4>
          <button @click="closeLogDetails" class="close-btn">×</button>
        </div>
        <div class="log-modal-content">
          <div class="detail-section">
            <label>Timestamp:</label>
            <span>{{ formatFullLogTime(selectedLog.timestamp) }}</span>
          </div>
          <div class="detail-section">
            <label>Source:</label>
            <span class="source-badge" :class="selectedLog.source">{{ selectedLog.source }}</span>
          </div>
          <div class="detail-section">
            <label>Level:</label>
            <span class="log-level" :class="selectedLog.level">{{ selectedLog.level }}</span>
          </div>
          <div class="detail-section">
            <label>Message:</label>
            <div class="message-detail">{{ selectedLog.message }}</div>
          </div>
          <div v-if="selectedLog.details" class="detail-section">
            <label>Details:</label>
            <pre class="details-json">{{ typeof selectedLog.details === 'object' ? JSON.stringify(selectedLog.details, null, 2) : selectedLog.details }}</pre>
          </div>
          <div v-if="selectedLog.context" class="detail-section">
            <label>Context:</label>
            <div class="context-grid">
              <div v-for="(value, key) in selectedLog.context" :key="key" class="context-pair">
                <strong>{{ key }}:</strong>
                <span>{{ value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useWebSocket } from '@/services/websocket'

export default {
  name: 'SystemLogsViewer',
  props: {
    taskId: {
      type: String,
      required: true
    }
  },
  emits: ['log-event'],
  setup(props, { emit }) {
    // WebSocket connection
    const { isConnected, on, off } = useWebSocket()
    
    // Data references
    const logs = ref([])
    const activeLogSource = ref('all')
    const autoScroll = ref(true)
    const isFullscreen = ref(false)
    const isLoading = ref(false)
    const isLive = ref(false)
    const selectedLog = ref(null)
    
    // DOM references
    const logsContainer = ref(null)
    const terminalContent = ref(null)
    const terminalWindow = ref(null)
    
    // Log sources configuration
    const logSources = [
      { id: 'all', label: 'All Logs', icon: '📋' },
      { id: 'server', label: 'Server', icon: '🖥️' },
      { id: 'client', label: 'Client', icon: '💻' },
      { id: 'llm', label: 'AI Monitor', icon: '🤖' },
      { id: 'websocket', label: 'WebSocket', icon: '🔗' },
      { id: 'system', label: 'System', icon: '⚙️' }
    ]
    
    // Computed properties
    const getFilteredLogs = () => {
      if (activeLogSource.value === 'all') {
        return logs.value
      }
      return logs.value.filter(log => log.source === activeLogSource.value)
    }
    
    const getLogCount = (source) => {
      if (source === 'all') return logs.value.length
      return logs.value.filter(log => log.source === source).length
    }
    
    const getActiveSourceLabel = () => {
      const source = logSources.find(s => s.id === activeLogSource.value)
      return source ? source.label : 'Unknown'
    }
    
    const getTimeRange = () => {
      const filtered = getFilteredLogs()
      if (filtered.length === 0) return 'No logs'
      
      const first = filtered[0]
      const last = filtered[filtered.length - 1]
      
      if (filtered.length === 1) {
        return formatLogTime(first.timestamp)
      }
      
      return `${formatLogTime(first.timestamp)} - ${formatLogTime(last.timestamp)}`
    }
    
    // Connection status
    const getConnectionStatusClass = () => {
      if (isLive.value) return 'status-live'
      if (isConnected.value) return 'status-connected'
      return 'status-disconnected'
    }
    
    const getConnectionStatusText = () => {
      if (isLive.value) return 'Live monitoring'
      if (isConnected.value) return 'Connected'
      return 'Disconnected'
    }
    
    // Log entry styling
    const getLogEntryClass = (log) => {
      return [
        `log-level-${log.level}`,
        `log-source-${log.source}`,
        log.isNew ? 'log-new' : ''
      ].filter(Boolean).join(' ')
    }
    
    const getLogLevelIcon = (level) => {
      const icons = {
        debug: '🔍',
        info: 'ℹ️',
        warning: '⚠️',
        error: '❌',
        critical: '🚨',
        success: '✅'
      }
      return icons[level] || 'ℹ️'
    }
    
    // Time formatting
    const formatLogTime = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit',
        fractionalSecondDigits: 3
      })
    }
    
    const formatFullLogTime = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleString('en-US', { 
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        fractionalSecondDigits: 3,
        hour12: false
      })
    }
    
    // Log management
    const addLog = (logEntry) => {
      // Add timestamp if not present
      if (!logEntry.timestamp) {
        logEntry.timestamp = Date.now()
      }
      
      // Mark as new for animation
      logEntry.isNew = true
      
      logs.value.push(logEntry)
      
      // Remove new flag after animation
      setTimeout(() => {
        logEntry.isNew = false
      }, 1000)
      
      // Limit log history (keep last 1000 entries)
      if (logs.value.length > 1000) {
        logs.value = logs.value.slice(-1000)
      }
      
      // Auto scroll if enabled
      if (autoScroll.value) {
        nextTick(() => {
          scrollToBottom()
        })
      }
      
      // Emit log event for parent components
      emit('log-event', logEntry)
    }
    
    const clearLogs = () => {
      logs.value = []
    }
    
    const toggleAutoScroll = () => {
      autoScroll.value = !autoScroll.value
      if (autoScroll.value) {
        scrollToBottom()
      }
    }
    
    const scrollToBottom = () => {
      if (terminalContent.value) {
        terminalContent.value.scrollTop = terminalContent.value.scrollHeight
      }
    }
    
    const toggleFullscreen = () => {
      isFullscreen.value = !isFullscreen.value
      
      if (isFullscreen.value) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    }
    
    const closeLogDetails = () => {
      selectedLog.value = null
    }
    
    const showLogDetails = (log) => {
      selectedLog.value = log
    }
    
    const exportLogs = () => {
      const filtered = getFilteredLogs()
      const logData = filtered.map(log => ({
        timestamp: formatFullLogTime(log.timestamp),
        source: log.source,
        level: log.level,
        message: log.message,
        details: log.details,
        context: log.context
      }))
      
      const blob = new Blob([JSON.stringify(logData, null, 2)], { 
        type: 'application/json' 
      })
      
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `system-logs-${props.taskId}-${new Date().toISOString().split('T')[0]}.json`
      link.click()
      
      URL.revokeObjectURL(url)
    }
    
    // WebSocket event handlers
    const handleServerLog = (message) => {
      addLog({
        source: 'server',
        level: message.level || 'info',
        message: message.message || message.data,
        details: message.details,
        context: {
          taskId: props.taskId,
          endpoint: message.endpoint,
          method: message.method
        },
        timestamp: message.timestamp || Date.now()
      })
    }
    
    const handleClientLog = (message) => {
      addLog({
        source: 'client',
        level: message.level || 'info',
        message: message.message || message.data,
        details: message.details,
        context: {
          taskId: props.taskId,
          machineId: message.machine_id,
          command: message.command
        },
        timestamp: message.timestamp || Date.now()
      })
    }
    
    // Generic message handler that routes to appropriate log handlers
    const handleWebSocketMessage = (message) => {
      console.log('SystemLogsViewer received WebSocket message:', message)
      console.log('Current task ID:', props.taskId)
      console.log('Message task ID:', message.task_id)
      console.log('Message type:', message.type)
      
      // Only process messages for our task
      if (message.task_id && message.task_id !== props.taskId && props.taskId !== 'system') {
        console.log('Message filtered out - task ID mismatch')
        return
      }
      
      console.log('Processing message for SystemLogsViewer')
      
      // Route message based on type
      switch (message.type) {
        case 'server_log':
          handleServerLog(message)
          break
        case 'client_log':
          handleClientLog(message)
          break
        case 'llm_analysis':
          handleLLMAnalysis(message)
          break
        case 'alternative_execution':
          handleAlternativeExecution(message)
          break
        case 'command_killed':
          handleCommandKilled(message)
          break
        case 'websocket_event':
          handleWebSocketEvent(message)
          break
        case 'task_chain_progress':
          handleTaskChainProgress(message)
          break
        case 'live_output':
          // Convert live output to client log
          addLog({
            source: 'client',
            level: 'debug',
            message: `Command output: ${(message.data || '').substring(0, 100)}...`,
            details: {
              stream: message.stream,
              fullOutput: message.data,
              subtaskId: message.subtask_id
            },
            context: {
              taskId: props.taskId,
              type: 'command_output'
            },
            timestamp: Date.now()
          })
          break
        case 'task_update':
          // Convert task update to server log
          addLog({
            source: 'server',
            level: 'info',
            message: `Task status: ${message.status || 'updated'}`,
            details: message,
            context: {
              taskId: props.taskId,
              type: 'status_change'
            },
            timestamp: Date.now()
          })
          break
        case 'interactive_prompt':
          // Convert to client log
          addLog({
            source: 'client',
            level: 'info',
            message: 'Interactive input required',
            details: {
              prompt: message.data
            },
            context: {
              taskId: props.taskId,
              type: 'user_input_request'
            },
            timestamp: Date.now()
          })
          break
        default:
          console.log('Unhandled message type in SystemLogsViewer:', message.type)
          // Generic log for unhandled message types
          addLog({
            source: 'system',
            level: 'debug',
            message: `WebSocket event: ${message.type || 'unknown'}`,
            details: message,
            context: {
              taskId: props.taskId,
              type: 'websocket_message'
            },
            timestamp: Date.now()
          })
      }
      
      console.log('Message processing completed')
    }
    
    const handleLLMAnalysis = (message) => {
      addLog({
        source: 'llm',
        level: 'info',
        message: `LLM Analysis: ${message.analysis?.reasoning || 'Command analyzed'}`,
        details: {
          status: message.analysis?.status,
          confidence: message.analysis?.confidence,
          shouldKill: message.analysis?.should_kill,
          suggestedAlternative: message.analysis?.suggested_alternative
        },
        context: {
          taskId: props.taskId,
          analysisType: 'command_monitoring'
        },
        timestamp: message.timestamp || Date.now()
      })
    }
    
    const handleAlternativeExecution = (message) => {
      addLog({
        source: 'client',
        level: 'warning',
        message: `Alternative command executed: ${message.alternative_command}`,
        details: {
          originalCommand: message.original_command,
          reason: message.reason,
          attemptNumber: message.attempt_number
        },
        context: {
          taskId: props.taskId,
          type: 'alternative_execution'
        },
        timestamp: message.timestamp || Date.now()
      })
    }
    
    const handleCommandKilled = (message) => {
      addLog({
        source: 'system',
        level: 'warning',
        message: `Command terminated: ${message.reason}`,
        details: {
          suggestedAlternative: message.suggested_alternative,
          executionTime: message.execution_time
        },
        context: {
          taskId: props.taskId,
          type: 'command_termination'
        },
        timestamp: message.timestamp || Date.now()
      })
    }
    
    const handleWebSocketEvent = (message) => {
      // Log WebSocket connection events
      addLog({
        source: 'websocket',
        level: 'info',
        message: `WebSocket: ${message.type}`,
        details: message,
        context: {
          taskId: props.taskId,
          connectionStatus: isConnected.value ? 'connected' : 'disconnected'
        },
        timestamp: Date.now()
      })
    }
    
    const handleTaskChainProgress = (message) => {
      addLog({
        source: 'server',
        level: 'info',
        message: `Task chain progress: ${message.completed_subtasks}/${message.total_subtasks} completed`,
        details: {
          currentResult: message.current_result,
          chainStatus: message.status
        },
        context: {
          taskId: props.taskId,
          type: 'chain_progress'
        },
        timestamp: message.timestamp || Date.now()
      })
    }
    
    // Initialize logs with current task start
    const initializeLogs = () => {
      console.log('Initializing SystemLogsViewer for task:', props.taskId)
      
      addLog({
        source: 'system',
        level: 'info',
        message: `Started monitoring task ${props.taskId}`,
        context: {
          taskId: props.taskId,
          type: 'monitoring_start'
        },
        timestamp: Date.now()
      })
      
      // Add a test log to verify the system is working
      setTimeout(() => {
        addLog({
          source: 'system',
          level: 'success',
          message: 'System logs viewer initialized successfully',
          details: {
            component: 'SystemLogsViewer',
            version: '1.0.0',
            features: ['real-time updates', 'filtering', 'export', 'fullscreen']
          },
          context: {
            taskId: props.taskId,
            type: 'initialization_complete'
          },
          timestamp: Date.now()
        })
      }, 1000)
      
      // Set live status
      isLive.value = true
    }
    
    // Lifecycle
    onMounted(() => {
      initializeLogs()
      
      console.log('SystemLogsViewer mounted for task:', props.taskId)
      console.log('Current WebSocket connection status:', isConnected.value)
      
      // Use nextTick to ensure component is fully mounted before registering listeners
      nextTick(() => {
        console.log('Registering WebSocket event handlers for SystemLogsViewer...')
        
        // Register the generic message handler for ALL WebSocket messages
        on('message', handleWebSocketMessage)
        
        // Also register specific handlers as backup
        on('server_log', handleServerLog)
        on('llm_analysis', handleLLMAnalysis)
        on('alternative_execution', handleAlternativeExecution)
        on('command_killed', handleCommandKilled)
        on('websocket_event', handleWebSocketEvent)
        on('task_chain_progress', handleTaskChainProgress)
        
        console.log('SystemLogsViewer registered WebSocket event handlers successfully')
        
        // Add a test log to verify the component is working
        addLog({
          source: 'system',
          level: 'info',
          message: `SystemLogsViewer initialized for task: ${props.taskId}`,
          details: {
            componentStatus: 'ready',
            websocketConnected: isConnected.value
          },
          context: {
            taskId: props.taskId,
            timestamp: new Date().toISOString()
          },
          timestamp: Date.now()
        })
      })
    })
    
    onUnmounted(() => {
      isLive.value = false
      
      console.log('SystemLogsViewer unmounting, cleaning up event listeners')
      
      // Clean up event listeners
      off('message', handleWebSocketMessage)
      off('server_log', handleServerLog)
      off('llm_analysis', handleLLMAnalysis)
      off('alternative_execution', handleAlternativeExecution)
      off('command_killed', handleCommandKilled)
      off('websocket_event', handleWebSocketEvent)
      off('task_chain_progress', handleTaskChainProgress)
      
      // Reset fullscreen
      if (isFullscreen.value) {
        document.body.style.overflow = ''
      }
    })
    
    return {
      // Data
      logs,
      activeLogSource,
      autoScroll,
      isFullscreen,
      isLoading,
      isLive,
      selectedLog,
      logSources,
      
      // DOM refs
      logsContainer,
      terminalContent,
      terminalWindow,
      
      // Computed
      getFilteredLogs,
      getLogCount,
      getActiveSourceLabel,
      getTimeRange,
      getConnectionStatusClass,
      getConnectionStatusText,
      getLogEntryClass,
      getLogLevelIcon,
      
      // Methods
      formatLogTime,
      formatFullLogTime,
      clearLogs,
      toggleAutoScroll,
      toggleFullscreen,
      exportLogs,
      showLogDetails,
      closeLogDetails
    }
  }
}
</script>

<style scoped>
.system-logs-viewer {
  background: #0d1117;
  border-radius: 12px;
  border: 1px solid #30363d;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  overflow: hidden;
  backdrop-filter: blur(20px);
  transition: all 0.3s ease;
}

.system-logs-viewer:hover {
  border-color: #00d562;
  box-shadow: 0 8px 32px rgba(0, 213, 98, 0.1);
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #21262d;
  background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-title h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #f0f6fc;
  background: linear-gradient(135deg, #00d562, #00a049);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logs-icon {
  font-size: 1.6rem;
  filter: drop-shadow(0 0 8px rgba(0, 213, 98, 0.3));
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
}

.status-live {
  background: linear-gradient(135deg, #00d562, #00a049);
  color: #0d1117;
  box-shadow: 0 4px 15px rgba(0, 213, 98, 0.3);
}

.status-connected {
  background: linear-gradient(135deg, #21262d, #30363d);
  color: #7d8590;
  border: 1px solid #30363d;
}

.status-disconnected {
  background: linear-gradient(135deg, #da3633, #b91c1c);
  color: white;
  box-shadow: 0 4px 15px rgba(218, 54, 51, 0.3);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { 
    opacity: 1; 
    transform: scale(1);
  }
  50% { 
    opacity: 0.6; 
    transform: scale(1.1);
  }
}

.logs-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.filter-tabs {
  display: flex;
  gap: 0;
  background: #21262d;
  border-radius: 12px;
  padding: 0.3rem;
  overflow-x: auto;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #7d8590;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  position: relative;
}

.filter-tab:hover {
  color: #f0f6fc;
  background: rgba(0, 213, 98, 0.05);
}

.filter-tab.active {
  color: #00d562;
  background: rgba(0, 213, 98, 0.1);
  box-shadow: inset 0 0 20px rgba(0, 213, 98, 0.1);
}

.log-count {
  background: #30363d;
  color: #7d8590;
  padding: 0.3rem 0.7rem;
  border-radius: 16px;
  font-size: 0.7rem;
  font-weight: 700;
  min-width: 24px;
  text-align: center;
  transition: all 0.3s ease;
}

.filter-tab.active .log-count {
  background: #00d562;
  color: #0d1117;
  box-shadow: 0 2px 8px rgba(0, 213, 98, 0.4);
}

.control-buttons {
  display: flex;
  gap: 0.5rem;
}

.control-btn {
  padding: 0.6rem 1rem;
  background: #21262d;
  border: 1px solid #30363d;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.8rem;
  color: #7d8590;
  font-weight: 500;
  transition: all 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn:hover {
  background: #30363d;
  color: #f0f6fc;
  border-color: #00d562;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 213, 98, 0.2);
}

.control-btn.active {
  background: #00d562;
  color: #0d1117;
  border-color: #00d562;
}

.clear-btn {
  background: rgba(218, 54, 51, 0.1);
  color: #f85149;
  border-color: rgba(218, 54, 51, 0.3);
}

.clear-btn:hover {
  background: rgba(218, 54, 51, 0.2);
  color: #ff6b6b;
  border-color: #da3633;
}

.logs-container {
  height: 500px;
  position: relative;
}

.logs-container.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  height: 100vh;
  z-index: 9999;
  border-radius: 0;
}

.terminal-window {
  height: 100%;
  background: #0d1117;
  display: flex;
  flex-direction: column;
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #161b22, #21262d);
  color: #f0f6fc;
  font-size: 0.85rem;
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  border-bottom: 1px solid #30363d;
}

.terminal-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.source-badge {
  padding: 0.4rem 0.8rem;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  white-space: nowrap;
  text-align: center;
  min-width: 80px;
}

.source-badge.all { 
  background: rgba(125, 133, 144, 0.2); 
  color: #7d8590; 
  border: 1px solid rgba(125, 133, 144, 0.3);
}
.source-badge.server { 
  background: rgba(33, 136, 255, 0.2); 
  color: #58a6ff; 
  border: 1px solid rgba(33, 136, 255, 0.3);
}
.source-badge.client { 
  background: rgba(255, 138, 36, 0.2); 
  color: #ff8a24; 
  border: 1px solid rgba(255, 138, 36, 0.3);
}
.source-badge.llm { 
  background: rgba(159, 122, 234, 0.2); 
  color: #a78bfa; 
  border: 1px solid rgba(159, 122, 234, 0.3);
}
.source-badge.websocket { 
  background: rgba(56, 178, 172, 0.2); 
  color: #22d3ee; 
  border: 1px solid rgba(56, 178, 172, 0.3);
}
.source-badge.system { 
  background: rgba(0, 213, 98, 0.2); 
  color: #00d562; 
  border: 1px solid rgba(0, 213, 98, 0.3);
}

.terminal-stats {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.8rem;
}

.live-indicator {
  color: #00d562;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
  from { text-shadow: 0 0 5px #00d562, 0 0 10px #00d562; }
  to { text-shadow: 0 0 10px #00d562, 0 0 20px #00d562, 0 0 30px #00d562; }
}

.terminal-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  background: linear-gradient(145deg, #0d1117 0%, #161b22 100%);
}

.terminal-content::-webkit-scrollbar {
  width: 8px;
}

.terminal-content::-webkit-scrollbar-track {
  background: #161b22;
}

.terminal-content::-webkit-scrollbar-thumb {
  background: #30363d;
  border-radius: 4px;
}

.terminal-content::-webkit-scrollbar-thumb:hover {
  background: #00d562;
}

.loading-logs, .empty-logs {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #7d8590;
  text-align: center;
  padding: 3rem;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #30363d;
  border-top: 3px solid #00d562;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.3;
  filter: grayscale(100%);
}

.empty-logs h4 {
  color: #f0f6fc;
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
}

.empty-logs p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
}

.log-entries {
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
}

.log-entry {
  display: grid;
  grid-template-columns: auto auto auto 1fr auto;
  gap: 1rem;
  padding: 0.75rem 1rem;
  margin: 0.25rem 0;
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  cursor: pointer;
  align-items: center;
  position: relative;
}

.log-entry:hover {
  background: rgba(0, 213, 98, 0.05);
  border-color: rgba(0, 213, 98, 0.2);
  transform: translateX(4px);
  box-shadow: 0 2px 12px rgba(0, 213, 98, 0.1);
}

.log-entry.log-new {
  animation: slideInGlow 0.5s ease-out;
}

@keyframes slideInGlow {
  from {
    opacity: 0;
    transform: translateX(-20px);
    box-shadow: 0 0 20px rgba(0, 213, 98, 0.6);
  }
  to {
    opacity: 1;
    transform: translateX(0);
    box-shadow: 0 0 5px rgba(0, 213, 98, 0.2);
  }
}

.log-timestamp {
  font-size: 0.75rem;
  color: #7d8590;
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
  white-space: nowrap;
  background: #21262d;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  border: 1px solid #30363d;
}

.log-level {
  font-size: 1.2rem;
  min-width: 24px;
  text-align: center;
}

.log-source-tag {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 0.4rem 0.8rem;
  border-radius: 12px;
  white-space: nowrap;
  text-align: center;
  min-width: 80px;
}

.log-source-tag.server { 
  background: rgba(33, 136, 255, 0.2); 
  color: #58a6ff; 
  border: 1px solid rgba(33, 136, 255, 0.3);
}
.log-source-tag.client { 
  background: rgba(255, 138, 36, 0.2); 
  color: #ff8a24; 
  border: 1px solid rgba(255, 138, 36, 0.3);
}
.log-source-tag.llm { 
  background: rgba(159, 122, 234, 0.2); 
  color: #a78bfa; 
  border: 1px solid rgba(159, 122, 234, 0.3);
}
.log-source-tag.websocket { 
  background: rgba(56, 178, 172, 0.2); 
  color: #22d3ee; 
  border: 1px solid rgba(56, 178, 172, 0.3);
}
.log-source-tag.system { 
  background: rgba(0, 213, 98, 0.2); 
  color: #00d562; 
  border: 1px solid rgba(0, 213, 98, 0.3);
}

.log-message {
  flex: 1;
  font-size: 0.9rem;
  line-height: 1.4;
  word-wrap: break-word;
  font-weight: 500;
  color: #f0f6fc;
  min-width: 0;
}

.message-content {
  word-wrap: break-word;
  margin-bottom: 0.25rem;
}

.task-id-badge {
  font-size: 0.7rem;
  background: #30363d;
  color: #7d8590;
  padding: 0.3rem 0.6rem;
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  border: 1px solid #21262d;
  white-space: nowrap;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Log level colors */
.log-level-debug { opacity: 0.7; }
.log-level-debug .log-message { color: #7d8590; }
.log-level-info .log-message { color: #f0f6fc; }
.log-level-warning .log-message { color: #d29922; font-weight: 600; }
.log-level-error .log-message { color: #f85149; font-weight: 600; }
.log-level-critical .log-message { 
  color: #ff6b6b; 
  font-weight: 700;
  text-shadow: 0 0 5px rgba(255, 107, 107, 0.5);
}
.log-level-success .log-message { color: #00d562; font-weight: 600; }

.message-details {
  margin-top: 0.5rem;
}

.message-details pre {
  background: rgba(0, 0, 0, 0.2);
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  color: #a0aec0;
  overflow-x: auto;
  margin: 0;
}

.message-context {
  margin-top: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.context-item {
  background: rgba(255, 255, 255, 0.05);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
}

.context-key {
  color: #a0aec0;
}

.context-value {
  color: #e2e8f0;
  margin-left: 0.25rem;
}

/* Log modal */
.log-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 2rem;
}

.log-modal {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 16px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
}

.log-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #21262d;
  background: linear-gradient(135deg, #161b22, #0d1117);
}

.log-modal-header h4 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #f0f6fc;
}

.close-btn {
  background: #21262d;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 0.6rem;
  cursor: pointer;
  color: #7d8590;
  font-size: 1.2rem;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #30363d;
  color: #f0f6fc;
  border-color: #00d562;
}

.log-modal-content {
  padding: 1.5rem;
  background: #0d1117;
}

.detail-section {
  margin-bottom: 1.5rem;
}

.detail-section label {
  font-weight: 600;
  color: #00d562;
  display: block;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.9rem;
}

.message-detail {
  font-family: 'JetBrains Mono', monospace;
  background: #161b22;
  border: 1px solid #21262d;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  line-height: 1.6;
  color: #f0f6fc;
}

.details-json {
  background: #0d1117;
  color: #f0f6fc;
  border: 1px solid #30363d;
  padding: 1.5rem;
  border-radius: 12px;
  font-size: 0.85rem;
  line-height: 1.6;
  overflow-x: auto;
  margin: 0;
  font-family: 'JetBrains Mono', monospace;
}

.context-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.context-pair {
  background: #161b22;
  border: 1px solid #21262d;
  padding: 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.context-pair:hover {
  border-color: #00d562;
  background: rgba(0, 213, 98, 0.05);
}

.context-pair strong {
  color: #00d562;
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.8rem;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .log-entry {
    grid-template-columns: auto auto 1fr;
    gap: 0.75rem;
  }
  
  .log-source-tag {
    grid-row: 2;
    grid-column: 1 / -1;
    justify-self: start;
  }
  
  .task-id-badge {
    display: none;
  }
}

@media (max-width: 768px) {
  .logs-header {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .filter-tabs {
    overflow-x: auto;
    width: 100%;
  }
  
  .filter-tab {
    padding: 0.75rem 1rem;
    font-size: 0.8rem;
  }
  
  .logs-container {
    height: 400px;
  }
  
  .log-entry {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    padding: 1rem;
  }
  
  .log-timestamp,
  .log-level,
  .log-source-tag,
  .log-message {
    justify-self: start;
  }
  
  .log-modal-content {
    padding: 1rem;
  }
  
  .context-grid {
    grid-template-columns: 1fr;
  }
}

/* Fullscreen styles */
.logs-container.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9998;
  border-radius: 0;
  height: 100vh;
  border: none;
}

.logs-container.fullscreen .terminal-content {
  height: calc(100vh - 200px);
}

/* Smooth transitions */
* {
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}</style>
