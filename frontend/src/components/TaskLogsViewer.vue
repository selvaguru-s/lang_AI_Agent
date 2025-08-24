<template>
  <div class="task-logs-viewer bg-gray-900 rounded-lg border border-gray-700">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-700">
      <div class="flex items-center space-x-3">
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 rounded-full animate-pulse" 
               :class="isConnected ? 'bg-green-400' : 'bg-red-400'"></div>
          <span class="text-sm text-gray-300 font-medium">
            {{ isConnected ? 'Live Updates' : 'Disconnected' }}
          </span>
        </div>
        <span class="text-xs text-gray-500">{{ logs.length }} events</span>
      </div>
      
      <div class="flex items-center space-x-2">
        <button @click="clearLogs" 
                class="text-xs px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-gray-300 transition-colors">
          Clear
        </button>
        <button @click="toggleAutoScroll" 
                class="text-xs px-3 py-1 rounded text-gray-300 transition-colors"
                :class="autoScroll ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-700 hover:bg-gray-600'">
          Auto-scroll {{ autoScroll ? 'ON' : 'OFF' }}
        </button>
      </div>
    </div>
    
    <!-- Logs Content -->
    <div ref="logsContainer" class="h-80 overflow-y-auto bg-gray-900 font-mono text-sm">
      <!-- Empty State -->
      <div v-if="logs.length === 0" class="flex items-center justify-center h-full text-gray-500">
        <div class="text-center">
          <div class="text-2xl mb-2">📋</div>
          <p class="text-sm">Waiting for task execution logs...</p>
        </div>
      </div>
      
      <!-- Log Entries -->
      <div v-else class="p-4 space-y-2">
        <div v-for="(log, index) in logs" :key="index" 
             class="flex items-start space-x-3 p-2 rounded hover:bg-gray-800 transition-colors"
             :class="getLogRowClass(log)">
          
          <!-- Timestamp -->
          <span class="text-xs text-gray-500 font-mono shrink-0 w-20">
            {{ formatTime(log.timestamp) }}
          </span>
          
          <!-- Status Icon -->
          <span class="text-base shrink-0 w-6 text-center">
            {{ getStatusIcon(log.type, log.status) }}
          </span>
          
          <!-- Message -->
          <div class="flex-1 min-w-0">
            <div class="font-medium" :class="getMessageClass(log.type, log.status)">
              {{ getLogMessage(log) }}
            </div>
            
            <!-- Additional Details -->
            <div v-if="log.details" class="text-xs text-gray-400 mt-1">
              {{ getLogDetails(log) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useWebSocket } from '@/services/websocket'

export default {
  name: 'TaskLogsViewer',
  props: {
    taskId: {
      type: String,
      required: true
    },
    taskData: {
      type: Object,
      default: null
    }
  },
  emits: ['log-event'],
  setup(props, { emit }) {
    const logs = ref([])
    const autoScroll = ref(true)
    const logsContainer = ref(null)
    
    const { isConnected, on, off } = useWebSocket()
    
    // Add log entry
    const addLog = (logEntry) => {
      logs.value.push({
        ...logEntry,
        timestamp: logEntry.timestamp || Date.now()
      })
      
      // Limit to last 200 entries
      if (logs.value.length > 200) {
        logs.value = logs.value.slice(-200)
      }
      
      if (autoScroll.value) {
        nextTick(() => {
          scrollToBottom()
        })
      }
      
      emit('log-event', logEntry)
    }
    
    // Populate logs from task execution history
    const populateLogsFromTaskData = () => {
      if (!props.taskData) return
      
      // Clear existing logs except system monitoring message
      const systemLogs = logs.value.filter(log => log.type === 'system')
      logs.value = [...systemLogs]
      
      const task = props.taskData
      
      // Add task started log
      addLog({
        type: 'task_started',
        status: 'info',
        message: `🚀 Task execution started on ${task.machine_id}`,
        timestamp: new Date(task.created_at).toISOString(),
        details: { machine_id: task.machine_id }
      })
      
      // Add logs for each subtask execution
      if (task.subtasks) {
        task.subtasks.forEach((subtask, index) => {
          if (subtask.attempts && subtask.attempts.length > 0) {
            subtask.attempts.forEach((attempt, attemptIndex) => {
              const isSuccess = attempt.exit_code === 0
              
              // Add command execution log
              addLog({
                type: 'command_result',
                status: isSuccess ? 'success' : 'error',
                message: `Command executed: ${attempt.command}`,
                timestamp: attempt.timestamp || new Date().toISOString(),
                details: {
                  exit_code: attempt.exit_code,
                  attempt_number: attempt.attempt_number || (attemptIndex + 1),
                  output_length: attempt.output?.length || 0,
                  step: index + 1,
                  description: subtask.description
                }
              })
              
              // Add output if available
              if (attempt.output && attempt.output.trim()) {
                addLog({
                  type: 'live_output',
                  status: 'info',
                  message: `Command output: ${attempt.output.substring(0, 100)}${attempt.output.length > 100 ? '...' : ''}`,
                  timestamp: attempt.timestamp || new Date().toISOString(),
                  details: {
                    stream: 'stdout',
                    data_length: attempt.output.length,
                    full_output: attempt.output
                  }
                })
              }
            })
          }
        })
      }
      
      // Add task completion log
      if (task.status === 'completed') {
        addLog({
          type: 'task_update',
          status: 'completed',
          message: '✅ Task completed successfully',
          timestamp: task.completed_at ? new Date(task.completed_at).toISOString() : new Date().toISOString(),
          details: {
            duration: task.completed_at ? 
              Math.floor((new Date(task.completed_at) - new Date(task.created_at)) / 1000) : 0
          }
        })
      } else if (task.status === 'failed') {
        addLog({
          type: 'task_update',
          status: 'failed',
          message: '❌ Task execution failed',
          timestamp: task.completed_at ? new Date(task.completed_at).toISOString() : new Date().toISOString(),
          details: {
            error: task.error_message
          }
        })
      }
    }
    
    // WebSocket event handlers
    const handleTaskStarted = (message) => {
      if (message.task_id === props.taskId) {
        addLog({
          type: 'task_started',
          status: 'info',
          message: `Task execution started on ${message.machine_id}`,
          timestamp: new Date().toISOString(),
          details: { machine_id: message.machine_id }
        })
      }
    }
    
    const handleTaskUpdate = (message) => {
      if (message.task_id === props.taskId) {
        const isCompleted = message.status === 'completed'
        const isFailed = message.status === 'failed'
        const isRunning = message.status === 'running'
        
        let logMessage = ''
        if (isCompleted) {
          logMessage = '✅ Task completed successfully'
        } else if (isFailed) {
          logMessage = '❌ Task execution failed'
        } else if (isRunning) {
          logMessage = '⚡ Task is executing...'
        } else {
          logMessage = `Task status: ${message.status}`
        }
        
        addLog({
          type: 'task_update',
          status: message.status,
          message: logMessage,
          timestamp: new Date().toISOString(),
          details: {
            subtask_id: message.subtask_id,
            attempt: message.attempt,
            validation: message.validation
          }
        })
      }
    }
    
    const handleCommandResult = (message) => {
      if (message.task_id === props.taskId) {
        const exitCode = message.attempt?.exit_code || message.exit_code
        const command = message.attempt?.command || message.command
        const isSuccess = exitCode === 0
        
        addLog({
          type: 'command_result',
          status: isSuccess ? 'success' : 'error',
          message: `Command executed: ${command}`,
          timestamp: new Date().toISOString(),
          details: {
            exit_code: exitCode,
            attempt_number: message.attempt?.attempt_number,
            output_length: message.attempt?.output?.length || 0
          }
        })
      }
    }
    
    const handleLiveOutput = (message) => {
      if (message.task_id === props.taskId) {
        addLog({
          type: 'live_output',
          status: 'info',
          message: `Command output received (${message.stream})`,
          timestamp: new Date().toISOString(),
          details: {
            stream: message.stream,
            data_length: message.data?.length || 0,
            subtask_id: message.subtask_id
          }
        })
      }
    }
    
    const handleClientLog = (message) => {
      if (message.task_id === props.taskId || message.task_id === 'system') {
        // Parse client log levels
        const level = message.level || 'info'
        const logLevel = level.toLowerCase()
        
        let status = 'info'
        if (logLevel === 'error' || logLevel === 'critical') status = 'error'
        else if (logLevel === 'warning' || logLevel === 'warn') status = 'warning'
        else if (logLevel === 'debug') status = 'debug'
        
        addLog({
          type: 'client_log',
          status: status,
          message: message.message || message.data || 'Client log entry',
          timestamp: message.timestamp || new Date().toISOString(),
          details: {
            level: level.toUpperCase(),
            logger: message.logger || 'client',
            machine_id: message.machine_id,
            context: message.context || {},
            raw_message: message
          }
        })
      }
    }
    
    const handleServerLog = (message) => {
      if (message.task_id === props.taskId) {
        const level = message.level || 'info'
        
        let status = 'info'
        if (level === 'error' || level === 'critical') status = 'error'
        else if (level === 'warning' || level === 'warn') status = 'warning'
        
        addLog({
          type: 'server_log',
          status: status,
          message: message.message || 'Server log entry',
          timestamp: message.timestamp || new Date().toISOString(),
          details: {
            level: level.toUpperCase(),
            source: message.source || 'server',
            context: message.context || {},
            details: message.details || {}
          }
        })
      }
    }
    
    const handleInteractivePrompt = (message) => {
      if (message.task_id === props.taskId) {
        addLog({
          type: 'interactive_prompt',
          status: 'warning',
          message: '⌨️ Command requires user input',
          timestamp: new Date().toISOString(),
          details: { prompt_data: message.data }
        })
      }
    }
    
    const handleAlternativeCommandTriggered = (message) => {
      if (message.task_id === props.taskId) {
        addLog({
          type: 'alternative_execution',
          status: 'warning',
          message: `🔄 Retrying with alternative command (attempt ${message.attempt_number})`,
          timestamp: new Date().toISOString(),
          details: {
            original_command: message.original_command,
            alternative_command: message.alternative_command,
            reason: message.reason
          }
        })
      }
    }
    
    // Helper functions
    const getLogMessage = (log) => {
      if (log.type === 'client_log') {
        // Format client log messages nicely
        const logger = log.details?.logger || 'client'
        const level = log.details?.level || 'INFO'
        return `[${logger}] ${level} - ${log.message}`
      }
      
      if (log.type === 'server_log') {
        const source = log.details?.source || 'server'
        const level = log.details?.level || 'INFO'
        return `[${source}] ${level} - ${log.message}`
      }
      
      return log.message || 'Unknown event'
    }
    
    const getLogDetails = (log) => {
      if (!log.details) return ''
      
      const details = []
      
      // Standard details
      if (log.details.exit_code !== undefined) {
        details.push(`Exit code: ${log.details.exit_code}`)
      }
      if (log.details.attempt_number) {
        details.push(`Attempt: ${log.details.attempt_number}`)
      }
      if (log.details.step) {
        details.push(`Step: ${log.details.step}`)
      }
      if (log.details.description) {
        details.push(`Task: ${log.details.description}`)
      }
      if (log.details.output_length) {
        details.push(`Output: ${log.details.output_length} chars`)
      }
      if (log.details.machine_id) {
        details.push(`Machine: ${log.details.machine_id}`)
      }
      if (log.details.reason) {
        details.push(`Reason: ${log.details.reason}`)
      }
      if (log.details.duration) {
        details.push(`Duration: ${log.details.duration}s`)
      }
      
      // Client log specific details
      if (log.type === 'client_log') {
        if (log.details.logger && log.details.logger !== 'client') {
          details.push(`Logger: ${log.details.logger}`)
        }
        if (log.details.context && Object.keys(log.details.context).length > 0) {
          const contextStr = Object.entries(log.details.context)
            .map(([k, v]) => `${k}:${v}`)
            .join(', ')
          details.push(`Context: ${contextStr}`)
        }
      }
      
      // Server log specific details
      if (log.type === 'server_log') {
        if (log.details.details && Object.keys(log.details.details).length > 0) {
          const detailsStr = Object.entries(log.details.details)
            .slice(0, 3)  // Limit to first 3 details
            .map(([k, v]) => `${k}:${v}`)
            .join(', ')
          details.push(`Details: ${detailsStr}`)
        }
      }
      
      return details.join(' • ')
    }
    
    const getStatusIcon = (type, status) => {
      const icons = {
        task_started: '🚀',
        task_update: status === 'completed' ? '✅' : status === 'failed' ? '❌' : status === 'running' ? '⚡' : '📋',
        command_result: status === 'success' ? '✅' : '❌',
        live_output: '📟',
        interactive_prompt: '⌨️',
        alternative_execution: '🔄',
        client_log: status === 'error' ? '🔴' : status === 'warning' ? '🟡' : status === 'debug' ? '🔍' : '🔵',
        server_log: status === 'error' ? '❌' : status === 'warning' ? '⚠️' : '🖥️',
        system: '⚙️'
      }
      return icons[type] || 'ℹ️'
    }
    
    const getMessageClass = (type, status) => {
      if (status === 'success' || type === 'task_started') return 'text-green-400'
      if (status === 'error' || status === 'failed') return 'text-red-400'
      if (status === 'warning' || type === 'alternative_execution') return 'text-yellow-400'
      if (status === 'running') return 'text-blue-400'
      if (status === 'debug') return 'text-purple-400'
      if (type === 'client_log') return 'text-cyan-400'
      if (type === 'server_log') return 'text-indigo-400'
      return 'text-gray-300'
    }
    
    const getLogRowClass = (log) => {
      if (log.status === 'success' || log.type === 'task_started') return 'border-l-2 border-green-500/50'
      if (log.status === 'error' || log.status === 'failed') return 'border-l-2 border-red-500/50'
      if (log.status === 'warning' || log.type === 'alternative_execution') return 'border-l-2 border-yellow-500/50'
      if (log.status === 'running') return 'border-l-2 border-blue-500/50'
      if (log.status === 'debug') return 'border-l-2 border-purple-500/50'
      if (log.type === 'client_log') return 'border-l-2 border-cyan-500/50'
      if (log.type === 'server_log') return 'border-l-2 border-indigo-500/50'
      return 'border-l-2 border-gray-600/50'
    }
    
    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
      })
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
      if (logsContainer.value) {
        logsContainer.value.scrollTop = logsContainer.value.scrollHeight
      }
    }
    
    // Watch for task data changes
    watch(() => props.taskData, (newTaskData) => {
      if (newTaskData) {
        console.log('📊 Task data updated, repopulating logs...')
        populateLogsFromTaskData()
      }
    }, { deep: true, immediate: true })
    
    // Lifecycle
    onMounted(() => {
      console.log('TaskLogsViewer mounted for task:', props.taskId)
      
      // Add initial log
      addLog({
        type: 'system',
        status: 'info', 
        message: `📡 Started monitoring task ${props.taskId}`,
        timestamp: new Date().toISOString(),
        details: { monitoring: 'active' }
      })
      
      // Populate logs from task data if available
      if (props.taskData) {
        console.log('📋 Populating logs from existing task data...')
        populateLogsFromTaskData()
      }
      
      // Register WebSocket event listeners
      on('task_started', handleTaskStarted)
      on('task_update', handleTaskUpdate)
      on('command_result', handleCommandResult)
      on('live_output', handleLiveOutput)
      on('interactive_prompt', handleInteractivePrompt)
      on('waiting_for_input', handleInteractivePrompt)
      on('alternative_command_triggered', handleAlternativeCommandTriggered)
      
      // Register log event listeners
      on('client_log', handleClientLog)
      on('server_log', handleServerLog)
      
      console.log('TaskLogsViewer WebSocket listeners registered')
    })
    
    onUnmounted(() => {
      // Clean up event listeners
      off('task_started', handleTaskStarted)
      off('task_update', handleTaskUpdate)
      off('command_result', handleCommandResult)
      off('live_output', handleLiveOutput)
      off('interactive_prompt', handleInteractivePrompt)
      off('waiting_for_input', handleInteractivePrompt)
      off('alternative_command_triggered', handleAlternativeCommandTriggered)
      
      // Clean up log event listeners
      off('client_log', handleClientLog)
      off('server_log', handleServerLog)
      
      console.log('TaskLogsViewer WebSocket listeners cleaned up')
    })
    
    return {
      logs,
      autoScroll,
      logsContainer,
      isConnected,
      
      // Methods
      getLogMessage,
      getLogDetails,
      getStatusIcon,
      getMessageClass,
      getLogRowClass,
      formatTime,
      clearLogs,
      toggleAutoScroll,
      scrollToBottom
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar for logs container */
.task-logs-viewer ::-webkit-scrollbar {
  width: 6px;
}

.task-logs-viewer ::-webkit-scrollbar-track {
  background: #1f2937;
}

.task-logs-viewer ::-webkit-scrollbar-thumb {
  background: #4b5563;
  border-radius: 3px;
}

.task-logs-viewer ::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}
</style>