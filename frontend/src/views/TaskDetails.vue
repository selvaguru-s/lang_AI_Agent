<template>
  <div class="task-details">
    <div v-if="task" class="task-container">
      <div class="task-header">
        <div class="task-title-section">
          <h1>{{ task.original_prompt }}</h1>
          <div class="connection-status">
            <span class="status-dot" :class="getConnectionStatus()"></span>
            <span class="connection-text">{{ getConnectionText() }}</span>
          </div>
        </div>
        <div class="status" :class="task.status">{{ task.status }}</div>
      </div>

      <div class="task-info">
        <div class="info-grid">
          <div><strong>Task ID:</strong> {{ task.task_id }}</div>
          <div><strong>Machine ID:</strong> {{ task.machine_id }}</div>
          <div><strong>Created:</strong> {{ formatDate(task.created_at) }}</div>
          <div><strong>Progress:</strong> {{ task.current_subtask_index + 1 }}/{{ task.subtasks.length }}</div>
        </div>
      </div>

      <div class="subtasks">
        <h2>Verification Methods</h2>
        <div v-if="isVerificationTask()" class="verification-summary">
          <div class="verification-overview">
            <h3>🔍 {{ task.original_prompt }}</h3>
            <div class="verification-result" :class="getOverallVerificationStatus()">
              {{ getOverallVerificationText() }}
            </div>
          </div>
        </div>
        
        <div v-for="(subtask, index) in task.subtasks" :key="index" class="subtask-card" :class="{ 'verification-method': isVerificationTask() }">
          <div class="subtask-header">
            <div class="method-info">
              <h3 v-if="isVerificationTask()">Method {{ index + 1 }}: {{ getVerificationMethodType(subtask.description) }}</h3>
              <h3 v-else>{{ subtask.description }}</h3>
              <p class="method-description">{{ subtask.description }}</p>
            </div>
            <div class="subtask-status" :class="getSubtaskStatus(index)">
              {{ getSubtaskStatusText(index) }}
            </div>
          </div>
          <div class="subtask-command">
            <strong>Command:</strong>
            <code>{{ subtask.command }}</code>
          </div>
          <div class="expected-output">
            <strong>Expected Output:</strong>
            <p>{{ subtask.expected_output }}</p>
          </div>
          <div v-if="subtask.attempts && subtask.attempts.length" class="attempts">
            <h4>Execution Attempts</h4>
            <div v-for="(attempt, attemptIndex) in subtask.attempts" :key="attemptIndex" class="attempt">
              <div class="attempt-header">
                <span>Attempt {{ attempt.attempt_number }}</span>
                <span class="exit-code" :class="{ success: attempt.exit_code === 0 }">
                  Exit Code: {{ attempt.exit_code }}
                </span>
              </div>
              <div class="attempt-output">
                <pre>{{ attempt.output }}</pre>
              </div>
            </div>
          </div>
          
          <!-- Live output for currently running subtask -->
          <div v-if="isCurrentSubtask(index) && liveOutputs[subtask.id]" class="live-output">
            <h4>🔴 Live Output</h4>
            <div class="live-terminal">
              <pre ref="liveTerminal">{{ liveOutputs[subtask.id] }}</pre>
            </div>
            
            <!-- Interactive input when waiting for user input -->
            <div v-if="waitingForInput[subtask.id]" class="interactive-input">
              <div class="input-prompt">
                <span class="prompt-icon">⌨️</span>
                <span>Command is waiting for user input:</span>
              </div>
              <div class="input-section">
                <input 
                  v-model="userInput"
                  type="text" 
                  placeholder="Type your input and press Enter..."
                  class="user-input-field"
                  @keypress.enter="sendUserInput(subtask.id)"
                  ref="userInputField"
                />
                <button @click="sendUserInput(subtask.id)" class="send-input-btn">Send</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="task.ai_summary" class="ai-summary">
        <h3>🤖 AI Summary</h3>
        <p>{{ task.ai_summary }}</p>
      </div>

      <div v-if="task.error_message" class="error-message">
        <h3>Error</h3>
        <p>{{ task.error_message }}</p>
      </div>
    </div>

    <div v-else class="loading">
      Loading task details...
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWebSocket } from '@/services/websocket'
import api from '@/services/api'

export default {
  name: 'TaskDetails',
  setup() {
    const task = ref(null)
    const route = useRoute()
    const authStore = useAuthStore()
    const { isConnected, on, off, sendUserInput: wsendUserInput } = useWebSocket()
    const liveOutputs = ref({})
    const liveTerminal = ref(null)
    const refreshInterval = ref(null)
    const lastRefresh = ref(Date.now())
    const waitingForInput = ref({})
    const userInput = ref('')
    const userInputField = ref(null)
    const clientLogs = ref([])
    const maxLogs = 100 // Keep last 100 log entries

    const loadTask = async () => {
      try {
        console.log('🔄 TaskDetails loading task data for ID:', route.params.id)
        const response = await api.get(`/tasks/${route.params.id}`)
        console.log('📊 TaskDetails loaded task data:', response.data)
        task.value = response.data
        lastRefresh.value = Date.now()
        console.log('✅ TaskDetails task data updated')
      } catch (error) {
        console.error('❌ Failed to load task:', error)
      }
    }

    const startAutoRefresh = () => {
      // Clear any existing interval
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
      }
      
      refreshInterval.value = setInterval(async () => {
        // Only auto-refresh if task is still running
        if (task.value && (task.value.status === 'running' || task.value.status === 'pending')) {
          console.log('🔄 Auto-refreshing task data...')
          await loadTask()
        } else if (task.value && (task.value.status === 'completed' || task.value.status === 'failed')) {
          // Stop auto-refresh when task is done
          console.log('⏹️ Task completed - stopping auto-refresh')
          stopAutoRefresh()
        }
      }, 2000) // Refresh every 2 seconds
      
      console.log('⏰ Auto-refresh started (every 2 seconds)')
    }

    const stopAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
        console.log('⏹️ Auto-refresh stopped')
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString()
    }

    const getSubtaskStatus = (index) => {
      const subtask = task.value.subtasks[index]
      
      // Check if subtask has actual status field
      if (subtask.status === 'completed') return 'completed'
      
      // Fallback to index-based logic
      if (task.value.status === 'completed') {
        return 'completed' // All subtasks completed
      }
      if (index < task.value.current_subtask_index) return 'completed'
      if (index === task.value.current_subtask_index) return 'current'
      return 'pending'
    }

    const getSubtaskStatusText = (index) => {
      const subtask = task.value.subtasks[index]
      
      // Check if subtask has actual status field
      if (subtask.status === 'completed') return 'Completed'
      
      // Fallback to index-based logic
      if (task.value.status === 'completed') {
        return 'Completed' // All subtasks completed
      }
      if (index < task.value.current_subtask_index) return 'Completed'
      if (index === task.value.current_subtask_index) return 'Current'
      return 'Pending'
    }

    const isCurrentSubtask = (index) => {
      return task.value && index === task.value.current_subtask_index && task.value.status === 'running'
    }

    const getConnectionStatus = () => {
      if (refreshInterval.value) return 'refreshing'
      if (isConnected.value) return 'online'
      return 'offline'
    }

    const getConnectionText = () => {
      if (refreshInterval.value) {
        const secondsSince = Math.floor((Date.now() - lastRefresh.value) / 1000)
        return `Auto-refreshing (${secondsSince}s ago)`
      }
      if (isConnected.value) return 'Live updates active'
      return 'Offline'
    }

    const isVerificationTask = () => {
      if (!task.value) return false
      const prompt = task.value.original_prompt.toLowerCase()
      return prompt.includes('installed') || 
             prompt.includes('available') || 
             prompt.includes('check if') || 
             prompt.includes('verify') ||
             prompt.includes('is ') ||
             task.value.subtasks.length >= 3
    }

    const getVerificationMethodType = (description) => {
      const desc = description.toLowerCase()
      if (desc.includes('path') || desc.includes('command -v') || desc.includes('which')) {
        return 'PATH Check'
      } else if (desc.includes('package') || desc.includes('dpkg') || desc.includes('rpm')) {
        return 'Package Manager'
      } else if (desc.includes('version') || desc.includes('help') || desc.includes('execution')) {
        return 'Functionality Test'
      } else if (desc.includes('systemctl') || desc.includes('service')) {
        return 'Service Status'
      } else if (desc.includes('process') || desc.includes('ps aux')) {
        return 'Process Check'
      } else if (desc.includes('port') || desc.includes('socket') || desc.includes('netstat')) {
        return 'Network Check'
      } else {
        return 'Alternative Check'
      }
    }

    const getOverallVerificationStatus = () => {
      if (!task.value || task.value.status === 'running') return 'checking'
      
      const completedSubtasks = task.value.subtasks.filter(subtask => 
        subtask.attempts && subtask.attempts.length > 0
      )
      
      const successfulChecks = completedSubtasks.filter(subtask => {
        const lastAttempt = subtask.attempts[subtask.attempts.length - 1]
        return lastAttempt.exit_code === 0 && 
               !lastAttempt.output.toLowerCase().includes('not found') &&
               !lastAttempt.output.toLowerCase().includes('not installed') &&
               !lastAttempt.output.toLowerCase().includes('failed')
      })
      
      if (successfulChecks.length > 0) return 'verified'
      if (completedSubtasks.length === task.value.subtasks.length) return 'not-found'
      return 'checking'
    }

    const getOverallVerificationText = () => {
      const status = getOverallVerificationStatus()
      if (status === 'verified') return '✅ Verified Available'
      if (status === 'not-found') return '❌ Not Found'
      return '🔄 Checking...'
    }

    const handleLiveOutput = (message) => {
      if (message.task_id === route.params.id) {
        const subtaskId = message.subtask_id
        
        if (!liveOutputs.value[subtaskId]) {
          liveOutputs.value[subtaskId] = ''
        }
        
        liveOutputs.value[subtaskId] += message.data
        
        // Auto-scroll to bottom of live terminal
        nextTick(() => {
          if (liveTerminal.value) {
            liveTerminal.value.scrollTop = liveTerminal.value.scrollHeight
          }
        })
      }
    }

    const handleInteractivePrompt = (message) => {
      console.log('🔔 Interactive prompt received:', message)
      if (message.task_id === route.params.id) {
        const subtaskId = message.subtask_id || getCurrentSubtaskId()
        
        // Add the prompt to live output
        if (!liveOutputs.value[subtaskId]) {
          liveOutputs.value[subtaskId] = ''
        }
        liveOutputs.value[subtaskId] += `\n${message.data}`
        
        // Mark as waiting for input
        waitingForInput.value[subtaskId] = true
        
        // Focus input field
        nextTick(() => {
          if (userInputField.value) {
            userInputField.value.focus()
          }
        })
      }
    }

    const handleWaitingForInput = (message) => {
      console.log('⏳ Waiting for input:', message)
      if (message.task_id === route.params.id) {
        const subtaskId = getCurrentSubtaskId()
        waitingForInput.value[subtaskId] = true
        
        // Focus input field
        nextTick(() => {
          if (userInputField.value) {
            userInputField.value.focus()
          }
        })
      }
    }

    const getCurrentSubtaskId = () => {
      if (!task.value || !task.value.subtasks) return null
      const currentSubtask = task.value.subtasks[task.value.current_subtask_index]
      return currentSubtask ? currentSubtask.id : null
    }

    const sendUserInput = (subtaskId) => {
      if (!userInput.value.trim()) return
      
      console.log('📤 Sending user input:', userInput.value)
      
      // Add input to terminal output (echo)
      if (liveOutputs.value[subtaskId]) {
        liveOutputs.value[subtaskId] += `\n${userInput.value}\n`
      }
      
      // Send to server via WebSocket
      wsendUserInput(task.value.task_id, task.value.machine_id, userInput.value.trim())
      
      // Clear input and waiting state
      userInput.value = ''
      waitingForInput.value[subtaskId] = false
    }

    const handleTaskUpdate = (message) => {
      console.log('🔄 TaskDetails received task_update:', message)
      console.log('📋 Current route task ID:', route.params.id)
      console.log('📋 Message task ID:', message.task_id)
      
      if (message.task_id === route.params.id) {
        console.log('✅ Task IDs match - refreshing task data')
        
        // Force reactive update by setting to null first, then reloading
        task.value = null
        setTimeout(async () => {
          await loadTask()
        }, 100)
      } else {
        console.log('❌ Task IDs do not match - ignoring update')
      }
    }

    onMounted(async () => {
      // Load initial task data
      await loadTask()
      
      // Start auto-refresh for running tasks
      if (task.value && (task.value.status === 'running' || task.value.status === 'pending')) {
        startAutoRefresh()
      }
      
      // Set up WebSocket event listeners (still keep for live output)
      console.log('📝 TaskDetails registering WebSocket event listeners')
      on('live_output', handleLiveOutput)
      on('task_update', handleTaskUpdate)
      on('interactive_prompt', handleInteractivePrompt)
      on('waiting_for_input', handleWaitingForInput)
      on('client_log', handleClientLog)
      console.log('✅ TaskDetails WebSocket event listeners registered')
    })

    onUnmounted(() => {
      // Clean up auto-refresh
      stopAutoRefresh()
      
      // Clean up WebSocket event listeners
      off('live_output', handleLiveOutput)
      off('task_update', handleTaskUpdate)
      off('interactive_prompt', handleInteractivePrompt)
      off('waiting_for_input', handleWaitingForInput)
    })

    return {
      task,
      formatDate,
      getSubtaskStatus,
      getSubtaskStatusText,
      isCurrentSubtask,
      liveOutputs,
      liveTerminal,
      isConnected,
      getConnectionStatus,
      getConnectionText,
      isVerificationTask,
      getVerificationMethodType,
      getOverallVerificationStatus,
      getOverallVerificationText,
      waitingForInput,
      userInput,
      userInputField,
      sendUserInput
    }
  }
}
</script>

<style scoped>
.task-details {
  padding: 2rem;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.task-title-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online {
  background: #28a745;
}

.status-dot.offline {
  background: #dc3545;
}

.status-dot.refreshing {
  background: #007bff;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.connection-text {
  font-size: 0.8rem;
  color: #6c757d;
}

.status {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  color: white;
  font-weight: bold;
}

.status.pending { background: #ffc107; }
.status.running { background: #007bff; }
.status.completed { background: #28a745; }
.status.failed { background: #dc3545; }

.task-info {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.subtasks {
  margin-top: 2rem;
}

.verification-summary {
  background: #f8f9fa;
  border: 2px dashed #dee2e6;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.verification-overview h3 {
  margin: 0 0 1rem 0;
  color: #495057;
}

.verification-result {
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-weight: bold;
  text-align: center;
}

.verification-result.verified {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.verification-result.not-found {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.verification-result.checking {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

.verification-method {
  border-left: 4px solid #007bff;
}

.method-info h3 {
  margin: 0 0 0.5rem 0;
  color: #007bff;
  font-size: 1rem;
}

.method-description {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
  font-style: italic;
}

.subtask-card {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

.subtask-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.subtask-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  color: white;
  font-size: 0.8rem;
}

.subtask-status.completed { background: #28a745; }
.subtask-status.current { background: #007bff; }
.subtask-status.pending { background: #6c757d; }

.subtask-command {
  margin-bottom: 1rem;
}

.subtask-command code {
  background: #f8f9fa;
  padding: 0.5rem;
  border-radius: 4px;
  display: block;
  margin-top: 0.5rem;
}

.expected-output {
  margin-bottom: 1rem;
}

.attempts {
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
}

.attempt {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.attempt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.exit-code {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background: #dc3545;
  color: white;
  font-size: 0.8rem;
}

.exit-code.success {
  background: #28a745;
}

.attempt-output pre {
  background: #212529;
  color: white;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0;
}

.ai-summary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 2rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.ai-summary h3 {
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
}

.ai-summary p {
  margin: 0;
  line-height: 1.6;
  font-size: 1rem;
}

.live-output {
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
  margin-top: 1rem;
}

.live-output h4 {
  color: #dc3545;
  margin-bottom: 0.5rem;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.live-terminal {
  background: #000;
  border-radius: 4px;
  padding: 0;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #333;
}

.live-terminal pre {
  background: #000;
  color: #00ff00;
  padding: 1rem;
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.4;
  min-height: 100px;
}

.live-terminal::-webkit-scrollbar {
  width: 8px;
}

.live-terminal::-webkit-scrollbar-track {
  background: #333;
}

.live-terminal::-webkit-scrollbar-thumb {
  background: #666;
  border-radius: 4px;
}

.live-terminal::-webkit-scrollbar-thumb:hover {
  background: #888;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 2rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}

/* Interactive Terminal Styles */
.interactive-input {
  margin-top: 1rem;
  padding: 1rem;
  background: #f0f8ff;
  border-radius: 8px;
  border: 2px solid #4a90e2;
}

.input-prompt {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #2c5aa0;
}

.prompt-icon {
  margin-right: 0.5rem;
  font-size: 1.1em;
}

.input-section {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.user-input-field {
  flex: 1;
  padding: 0.5rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  background: #fff;
}

.user-input-field:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.send-input-btn {
  padding: 0.5rem 1rem;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.send-input-btn:hover {
  background: #2c5aa0;
}

.send-input-btn:active {
  transform: translateY(1px);
}
</style>