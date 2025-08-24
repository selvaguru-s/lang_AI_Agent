<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header Section -->
    <div class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-4">
          <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <!-- Task Title and Status -->
            <div class="flex-1 min-w-0">
              <h1 class="text-2xl font-bold text-gray-900 truncate">
                {{ task?.original_prompt || 'Loading task...' }}
              </h1>
              <div class="mt-2 flex flex-wrap items-center gap-3">
                <div class="flex items-center gap-2">
                  <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                        :class="getStatusClasses(task?.status)">
                    <span class="mr-1">{{ getStatusIcon(task?.status) }}</span>
                    {{ getStatusText(task?.status) }}
                  </span>
                </div>
                <div class="flex items-center gap-2">
                  <div class="w-2 h-2 rounded-full" 
                       :class="isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'"></div>
                  <span class="text-sm text-gray-600">
                    Auto-refreshing every 1 second
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Task Info -->
            <div class="flex flex-col sm:flex-row sm:items-center gap-4 text-sm text-gray-600">
              <div>
                <span class="font-medium">Task ID:</span>
                <span class="ml-1 font-mono text-xs bg-gray-100 px-2 py-1 rounded">
                  {{ task?.task_id }}
                </span>
              </div>
              <div>
                <span class="font-medium">Machine:</span>
                <span class="ml-1 font-mono bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs">
                  {{ task?.machine_id || 'Unknown' }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- Progress Bar -->
          <div v-if="task" class="mt-4">
            <div class="flex justify-between items-center text-sm text-gray-600 mb-2">
              <span>Progress: {{ getCurrentStep() }}/{{ getTotalSteps() }} steps</span>
              <span class="font-semibold text-primary-600">{{ getProgressPercentage() }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div class="bg-gradient-to-r from-primary-500 to-primary-600 h-2 rounded-full transition-all duration-500"
                   :style="{ width: getProgressPercentage() + '%' }">
              </div>
            </div>
            <div class="mt-2 flex justify-between items-center text-xs text-gray-500">
              <span>{{ getProgressStatus() }}</span>
              <span v-if="getETA()">{{ getETA() }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="grid grid-cols-1 xl:grid-cols-3 lg:grid-cols-2 gap-6">
        <!-- Left Column: AI Summary and Task Info -->
        <div class="xl:col-span-2 lg:col-span-1 space-y-6">
          <!-- AI Analysis Card -->
          <div v-if="task?.ai_summary || isGeneratingAISummary || (task?.status === 'completed' && !task?.ai_summary)" 
               class="bg-white shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <div class="flex justify-between items-start mb-4">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <span class="text-2xl">🤖</span>
                  </div>
                  <div class="ml-3">
                    <h3 class="text-lg leading-6 font-medium text-gray-900">AI Analysis</h3>
                    <p class="mt-1 text-sm text-gray-500">
                      {{ isGeneratingAISummary ? 'Analyzing task execution...' : 'Intelligent task summary' }}
                    </p>
                  </div>
                </div>
                <div class="flex items-center space-x-3">
                  <button v-if="task?.status === 'completed' && !isGeneratingAISummary"
                          @click="generateAISummary"
                          class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors">
                    {{ task?.ai_summary ? 'Regenerate' : 'Generate Summary' }}
                  </button>
                  <span class="text-xs text-gray-400">
                    {{ isGeneratingAISummary ? 'Generating...' : formatLastUpdate(lastAISummaryUpdate) }}
                  </span>
                </div>
              </div>
              
              <div class="mt-4">
                <div v-if="isGeneratingAISummary" class="flex items-center space-x-3 text-gray-600">
                  <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-primary-500 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                    <div class="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  </div>
                  <span class="text-sm italic">Analyzing execution results...</span>
                </div>
                <div v-else-if="task?.ai_summary" 
                     class="prose prose-sm max-w-none text-gray-700 bg-gray-50 p-4 rounded-lg">
                  {{ task.ai_summary }}
                </div>
                <div v-else class="text-center py-8 text-gray-500">
                  <p>AI analysis not yet available. Click "Generate Summary" to analyze this completed task.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Task Information Card -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg leading-6 font-medium text-gray-900">Task Information</h3>
                <span class="text-xs text-gray-400">Updated {{ formatLastUpdate(lastRefresh) }}</span>
              </div>
              
              <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2 lg:grid-cols-3">
                <div>
                  <dt class="text-sm font-medium text-gray-500">Created</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ formatDate(task?.created_at) }}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Duration</dt>
                  <dd class="mt-1 text-sm text-gray-900"
                      :class="{ 'text-primary-600 font-semibold': task?.status === 'running' }">
                    {{ getExecutionDuration() }}
                  </dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Success Rate</dt>
                  <dd class="mt-1 text-sm font-semibold"
                      :class="getSuccessRate() > 80 ? 'text-green-600' : getSuccessRate() > 50 ? 'text-yellow-600' : 'text-red-600'">
                    {{ getSuccessRate() }}%
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          <!-- Task Execution Logs -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <div class="flex items-center mb-4">
                <span class="text-xl mr-3">📋</span>
                <div>
                  <h3 class="text-lg leading-6 font-medium text-gray-900">Execution Logs</h3>
                  <p class="text-sm text-gray-500 mt-1">Real-time task execution events and status updates</p>
                </div>
              </div>
              
              <TaskLogsViewer 
                :key="`logs-${task?.task_id}-${lastRefresh}`"
                :task-id="task?.task_id || $route.params.id"
                :task-data="task"
                @log-event="handleLogEvent"
              />
            </div>
          </div>

          <!-- Live Terminal Output -->
          <div v-if="hasLiveOutput" class="bg-white shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <div class="flex justify-between items-center mb-4">
                <div class="flex items-center">
                  <span class="text-xl mr-2">📟</span>
                  <h3 class="text-lg leading-6 font-medium text-gray-900">Live Output</h3>
                </div>
                <div class="flex space-x-2">
                  <button @click="clearLiveOutput"
                          class="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-gray-700 transition-colors">
                    Clear
                  </button>
                  <button @click="scrollToBottom"
                          class="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-gray-700 transition-colors">
                    Bottom
                  </button>
                </div>
              </div>
              
              <div class="bg-gray-900 rounded-lg p-4 max-h-96 overflow-y-auto font-mono text-sm"
                   ref="terminalContainer">
                <pre class="text-green-400 whitespace-pre-wrap">{{ getLiveOutputText() }}</pre>
              </div>
              
              <!-- Interactive Input -->
              <div v-if="isWaitingForInput" class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div class="flex items-center mb-3 text-blue-700">
                  <span class="mr-2">⌨️</span>
                  <span class="font-medium">Command waiting for input...</span>
                </div>
                <div class="flex space-x-2">
                  <input v-model="userInput"
                         @keypress.enter="sendUserInput"
                         placeholder="Type your response and press Enter..."
                         class="flex-1 px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                         ref="userInputField"
                         autocomplete="off" />
                  <button @click="sendUserInput"
                          :disabled="!userInput.trim()"
                          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>
          
        </div>

        <!-- Right Column: Execution Steps -->
        <div class="space-y-6">
          <div class="bg-white shadow-sm rounded-xl border border-gray-100 overflow-hidden">
            <!-- Header -->
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-4 border-b border-gray-100">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <span class="text-blue-600 font-semibold text-sm">{{ getTotalSteps() }}</span>
                  </div>
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900">Execution Steps</h3>
                    <p class="text-sm text-gray-600">{{ getSuccessfulSteps() }} of {{ getTotalSteps() }} completed</p>
                  </div>
                </div>
                <div class="flex items-center space-x-2">
                  <!-- Progress Ring -->
                  <div class="relative w-12 h-12">
                    <svg class="w-12 h-12 transform -rotate-90" viewBox="0 0 36 36">
                      <path class="text-gray-200" stroke="currentColor" stroke-width="3" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                      <path class="text-blue-600" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round"
                            :stroke-dasharray="`${getProgressPercentage()}, 100`"
                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    </svg>
                    <div class="absolute inset-0 flex items-center justify-center">
                      <span class="text-xs font-semibold text-gray-700">{{ getProgressPercentage() }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Steps Container -->
            <div class="divide-y divide-gray-100">
              <div v-for="(subtask, index) in task?.subtasks || []" 
                   :key="index"
                   class="relative">
                <!-- Compact Step Row -->
                <div class="group hover:bg-gray-50 transition-colors duration-200">
                  <div class="flex items-center px-3 sm:px-4 py-3">
                    <!-- Step Indicator -->
                    <div class="flex-shrink-0 mr-2 sm:mr-3">
                      <div class="w-6 h-6 sm:w-7 sm:h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-200"
                           :class="getCompactStepClasses(index)">
                        <span v-if="getStepStatus(index) === 'success'">✓</span>
                        <span v-else-if="getStepStatus(index) === 'failed'">✗</span>
                        <span v-else-if="getStepStatus(index) === 'running'" class="animate-spin">⚡</span>
                        <span v-else>{{ index + 1 }}</span>
                      </div>
                    </div>
                    
                    <!-- Step Content -->
                    <div class="flex-1 min-w-0 mr-2 sm:mr-3">
                      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                        <h4 class="text-sm font-medium text-gray-900 truncate group-hover:text-gray-700 mb-1 sm:mb-0">
                          <span class="hidden sm:inline">Step {{ index + 1 }}: </span>{{ getCompactStepTitle(subtask.description) }}
                        </h4>
                        <div class="flex items-center space-x-2 text-xs">
                          <span class="px-2 py-1 rounded-full font-medium"
                                :class="getCompactStatusBadge(index)">
                            {{ getStepStatusText(index) }}
                          </span>
                        </div>
                      </div>
                      
                      <!-- Command Preview -->
                      <div class="mt-1 sm:mt-2">
                        <code class="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded font-mono break-all">
                          {{ getCompactCommand(subtask.command) }}
                        </code>
                      </div>
                    </div>
                    
                    <!-- Expand Button -->
                    <button @click="toggleMethodDetails(index)"
                            class="flex-shrink-0 w-8 h-8 rounded-full hover:bg-gray-200 flex items-center justify-center transition-colors duration-200 group-hover:bg-gray-200">
                      <svg class="w-4 h-4 text-gray-500 transform transition-transform duration-200"
                           :class="expandedMethods.includes(index) ? 'rotate-180' : ''">
                        <path fill="currentColor" d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
                      </svg>
                    </button>
                  </div>
                </div>
                
                <!-- Expanded Details -->
                <div v-if="expandedMethods.includes(index)"
                     class="bg-gray-50 border-t border-gray-100 animate-in slide-in-from-top duration-200">
                  <div class="px-3 sm:px-4 py-4 space-y-3 sm:space-y-4">
                    
                    <!-- Full Description -->
                    <div class="bg-white rounded-lg p-3 border border-gray-200">
                      <h5 class="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">Task Description</h5>
                      <p class="text-sm text-gray-700">{{ subtask.description }}</p>
                    </div>
                    
                    <!-- Full Command -->
                    <div class="bg-gray-900 rounded-lg p-3">
                      <div class="flex items-center justify-between mb-2">
                        <h5 class="text-xs font-semibold text-gray-300 uppercase tracking-wide">Command</h5>
                        <button @click="copyToClipboard(subtask.command)" 
                                class="text-xs text-gray-400 hover:text-gray-200 flex items-center space-x-1">
                          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z"/>
                            <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z"/>
                          </svg>
                          <span>Copy</span>
                        </button>
                      </div>
                      <code class="text-green-400 text-sm font-mono break-all">{{ subtask.command }}</code>
                    </div>

                    <!-- Expected Output -->
                    <div class="bg-blue-50 rounded-lg p-3 border border-blue-200">
                      <h5 class="text-xs font-semibold text-blue-700 uppercase tracking-wide mb-2">Expected Output</h5>
                      <p class="text-sm text-blue-800">{{ subtask.expected_output || 'No expected output defined' }}</p>
                    </div>
                    
                    <!-- Execution Attempts -->
                    <div v-if="subtask.attempts?.length" class="space-y-3">
                      <h5 class="text-xs font-semibold text-gray-700 uppercase tracking-wide flex items-center space-x-2">
                        <span>Execution History</span>
                        <span class="bg-gray-200 text-gray-700 px-2 py-0.5 rounded-full text-xs">{{ subtask.attempts.length }} attempts</span>
                      </h5>
                      
                      <div class="space-y-2">
                        <div v-for="(attempt, attemptIndex) in subtask.attempts" 
                             :key="attemptIndex"
                             class="border rounded-lg overflow-hidden"
                             :class="attempt.exit_code === 0 ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'">
                          
                          <!-- Attempt Header -->
                          <div class="px-3 py-2 flex justify-between items-center"
                               :class="attempt.exit_code === 0 ? 'bg-green-100' : 'bg-red-100'">
                            <div class="flex items-center space-x-2">
                              <span class="text-xs font-medium" 
                                    :class="attempt.exit_code === 0 ? 'text-green-800' : 'text-red-800'">
                                Attempt {{ attempt.attempt_number || (attemptIndex + 1) }}
                              </span>
                              <span class="text-xs" 
                                    :class="attempt.exit_code === 0 ? 'text-green-600' : 'text-red-600'">
                                {{ attempt.timestamp ? new Date(attempt.timestamp).toLocaleTimeString() : 'No timestamp' }}
                              </span>
                            </div>
                            <div class="flex items-center space-x-2">
                              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                                    :class="attempt.exit_code === 0 ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'">
                                {{ attempt.exit_code === 0 ? '✓ Success' : '✗ Failed' }}
                              </span>
                              <span class="text-xs font-mono px-2 py-1 rounded"
                                    :class="attempt.exit_code === 0 ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'">
                                {{ attempt.exit_code }}
                              </span>
                            </div>
                          </div>
                          
                          <!-- Output -->
                          <div v-if="attempt.output && attempt.output.trim()" 
                               class="bg-gray-900 p-3 max-h-64 overflow-y-auto">
                            <pre class="text-green-400 text-xs whitespace-pre-wrap font-mono">{{ attempt.output }}</pre>
                          </div>
                          <div v-else class="px-3 py-2 text-xs text-gray-500 italic">
                            No output captured
                          </div>
                        </div>
                      </div>
                    </div>
                    
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="task?.error_message" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-6">
      <div class="bg-red-50 border border-red-200 rounded-md p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <span class="text-red-400 text-xl">⚠️</span>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Execution Error</h3>
            <div class="mt-2 text-sm text-red-700">
              {{ task.error_message }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="!task && !error" class="flex items-center justify-center min-h-64">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading task details...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center py-12">
        <span class="text-6xl">❌</span>
        <h3 class="mt-4 text-lg font-medium text-gray-900">Failed to load task details</h3>
        <p class="mt-2 text-sm text-gray-500">{{ error.message || 'Unknown error occurred' }}</p>
        <div class="mt-6">
          <button @click="loadTask"
                  class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            Try Again
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useWebSocket } from '@/services/websocket'
import api from '@/services/api'
import TaskLogsViewer from '@/components/TaskLogsViewer.vue'

export default {
  name: 'TaskDetailsModern',
  components: {
    TaskLogsViewer
  },
  setup() {
    // Core data
    const task = ref(null)
    const error = ref(null)
    const route = useRoute()
    
    // WebSocket
    const { isConnected, on, off, sendUserInput: wsSendUserInput } = useWebSocket()
    
    // Auto-refresh
    const refreshInterval = ref(null)
    const lastRefresh = ref(Date.now())
    const lastAISummaryUpdate = ref(Date.now())
    const isGeneratingAISummary = ref(false)
    
    // Live output
    const liveOutputs = ref({})
    const terminalContainer = ref(null)
    
    
    // User interaction
    const userInput = ref('')
    const userInputField = ref(null)
    const isWaitingForInput = ref(false)
    const currentSubtaskId = ref(null)
    
    // UI state
    const expandedMethods = ref([])
    
    // Force refresh every 1 second - refreshes ALL data
    const startAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
      }
      
      refreshInterval.value = setInterval(async () => {
        console.log('🔄 Force refreshing ALL task data (1s interval)...')
        await loadTask()
        
        // Force refresh TaskLogsViewer by emitting an event
        if (task.value) {
          console.log('📋 Forcing logs refresh for task:', task.value.task_id)
        }
      }, 1000) // Refresh EVERYTHING every 1 second
    }
    
    const stopAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
      }
    }
    
    // Load task data
    const loadTask = async () => {
      try {
        const response = await api.get(`/tasks/${route.params.id}`)
        const newTask = response.data
        
        // Check if AI summary changed (indicating new generation)
        if (task.value && task.value.ai_summary !== newTask.ai_summary && newTask.ai_summary) {
          lastAISummaryUpdate.value = Date.now()
          isGeneratingAISummary.value = false
        }
        
        // Check if task is newly completed and needs AI summary
        if (task.value && task.value.status === 'running' && newTask.status === 'completed' && !newTask.ai_summary && !isGeneratingAISummary.value) {
          console.log('🤖 Task completed! Auto-generating AI summary...')
          isGeneratingAISummary.value = true
          // Auto-generate AI summary for completed tasks
          setTimeout(() => {
            console.log('📝 Generating AI summary via API...')
            generateAISummary()
          }, 2000) // Wait 2 seconds before generating
        }
        
        task.value = newTask
        lastRefresh.value = Date.now()
        error.value = null
      } catch (err) {
        console.error('Failed to load task:', err)
        error.value = err
      }
    }
    
    // Status and progress helpers
    const getStatusClasses = (status) => {
      const classes = {
        pending: 'bg-yellow-100 text-yellow-800',
        running: 'bg-blue-100 text-blue-800', 
        completed: 'bg-green-100 text-green-800',
        failed: 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    }
    
    const getStatusIcon = (status) => {
      const icons = {
        pending: '⏳',
        running: '⚡',
        completed: '✅', 
        failed: '❌'
      }
      return icons[status] || '❓'
    }
    
    const getStatusText = (status) => {
      const texts = {
        pending: 'Pending',
        running: 'Running',
        completed: 'Completed',
        failed: 'Failed'
      }
      return texts[status] || 'Unknown'
    }
    
    const getCurrentStep = () => {
      if (!task.value) return 0
      return Math.min(task.value.current_subtask_index + 1, task.value.subtasks?.length || 0)
    }
    
    const getTotalSteps = () => {
      return task.value?.subtasks?.length || 0
    }
    
    const getProgressPercentage = () => {
      if (!task.value || !task.value.subtasks?.length) return 0
      if (task.value.status === 'completed') return 100
      return Math.round((getCurrentStep() / getTotalSteps()) * 100)
    }
    
    const getSuccessfulSteps = () => {
      if (!task.value?.subtasks) return 0
      return task.value.subtasks.filter((subtask, index) => {
        if (!subtask.attempts?.length) return false
        const lastAttempt = subtask.attempts[subtask.attempts.length - 1]
        
        // Check if this step was validated as successful by the backend
        if (lastAttempt.validation_result?.is_valid) {
          return true
        }
        
        // Use the same logic as getStepStatus for consistency
        const command = lastAttempt.command || subtask.command || ''
        const output = lastAttempt.output || ''
        
        if (isStatusCheckCommand(command) && lastAttempt.exit_code !== 0) {
          const statusIndicators = ['inactive', 'active', 'not found', 'no process', 'failed', 'running', 'stopped', 'not installed']
          const hasStatusOutput = statusIndicators.some(indicator => output.toLowerCase().includes(indicator))
          
          if (hasStatusOutput || output.trim()) {
            return true  // Successfully provided status information
          }
        }
        
        // Standard exit code check
        return lastAttempt.exit_code === 0
      }).length
    }
    
    const getSuccessRate = () => {
      if (!task.value) return 0
      const total = getTotalSteps()
      if (total === 0) return 0
      const successful = getSuccessfulSteps()
      return Math.round((successful / total) * 100)
    }
    
    // Step helpers
    const getStepTitle = (description) => {
      return description || 'Execution Step'
    }
    
    const getStepCardClasses = (index) => {
      const status = getStepStatus(index)
      const classes = {
        pending: 'border-gray-200 bg-white',
        running: 'border-blue-300 bg-blue-50',
        success: 'border-green-300 bg-green-50',
        failed: 'border-red-300 bg-red-50'
      }
      return classes[status] || 'border-gray-200 bg-white'
    }
    
    const getStepNumberClasses = (index) => {
      const status = getStepStatus(index)
      const classes = {
        pending: 'bg-gray-200 text-gray-600',
        running: 'bg-blue-500 text-white',
        success: 'bg-green-500 text-white',
        failed: 'bg-red-500 text-white'
      }
      return classes[status] || 'bg-gray-200 text-gray-600'
    }
    
    const getStepStatus = (index) => {
      if (!task.value) return 'pending'
      
      const subtask = task.value.subtasks[index]
      if (!subtask.attempts?.length) {
        if (index < task.value.current_subtask_index) return 'success'
        if (index === task.value.current_subtask_index && task.value.status === 'running') return 'running'
        return 'pending'
      }
      
      const lastAttempt = subtask.attempts[subtask.attempts.length - 1]
      
      // Check if this step was validated as successful by the backend
      if (lastAttempt.validation_result?.is_valid) {
        return 'success'
      }
      
      // Fallback logic for status check commands
      const command = lastAttempt.command || subtask.command || ''
      const output = lastAttempt.output || ''
      
      if (isStatusCheckCommand(command) && lastAttempt.exit_code !== 0) {
        const statusIndicators = ['inactive', 'active', 'not found', 'no process', 'failed', 'running', 'stopped', 'not installed']
        const hasStatusOutput = statusIndicators.some(indicator => output.toLowerCase().includes(indicator))
        
        if (hasStatusOutput || output.trim()) {
          return 'success'  // Successfully provided status information
        }
      }
      
      // Standard exit code check
      return lastAttempt.exit_code === 0 ? 'success' : 'failed'
    }
    
    const isStatusCheckCommand = (command) => {
      const statusCommands = [
        'which', 'systemctl status', 'systemctl is-active', 'ps aux | grep', 
        'dpkg -s', 'dpkg -l', 'ss -tulnp', 'netstat', 'nginx -v', 'docker --version',
        'apt list', 'yum list', 'rpm -q', 'service', 'pgrep', 'pidof'
      ]
      const commandLower = command.toLowerCase()
      return statusCommands.some(statusCmd => commandLower.includes(statusCmd))
    }
    
    const getStepStatusIcon = (index) => {
      const status = getStepStatus(index)
      const icons = {
        pending: '⏳',
        running: '⚡',
        success: '✅',
        failed: '❌'
      }
      return icons[status] || '❓'
    }
    
    const getStepStatusText = (index) => {
      const status = getStepStatus(index)
      const texts = {
        pending: 'Pending',
        running: 'Running',
        success: 'Success',
        failed: 'Failed'
      }
      return texts[status] || 'Unknown'
    }
    
    const getStepStatusTextClasses = (index) => {
      const status = getStepStatus(index)
      const classes = {
        pending: 'text-gray-600',
        running: 'text-blue-600',
        success: 'text-green-600',
        failed: 'text-red-600'
      }
      return classes[status] || 'text-gray-600'
    }
    
    // Compact step helpers
    const getCompactStepClasses = (index) => {
      const status = getStepStatus(index)
      const classes = {
        pending: 'bg-gray-200 text-gray-600',
        running: 'bg-blue-500 text-white shadow-lg animate-pulse',
        success: 'bg-green-500 text-white shadow-lg',
        failed: 'bg-red-500 text-white shadow-lg'
      }
      return classes[status] || 'bg-gray-200 text-gray-600'
    }
    
    const getCompactStatusBadge = (index) => {
      const status = getStepStatus(index)
      const classes = {
        pending: 'bg-gray-100 text-gray-600',
        running: 'bg-blue-100 text-blue-700',
        success: 'bg-green-100 text-green-700',
        failed: 'bg-red-100 text-red-700'
      }
      return classes[status] || 'bg-gray-100 text-gray-600'
    }
    
    const getCompactStepTitle = (description) => {
      if (!description) return 'Execution Step'
      // Truncate description for compact view
      return description.length > 50 ? description.substring(0, 50) + '...' : description
    }
    
    const getCompactCommand = (command) => {
      if (!command) return 'No command'
      // Truncate command for compact view
      return command.length > 60 ? command.substring(0, 60) + '...' : command
    }
    
    // Copy to clipboard helper
    const copyToClipboard = async (text) => {
      try {
        await navigator.clipboard.writeText(text)
        console.log('✅ Copied to clipboard:', text)
      } catch (err) {
        console.error('❌ Failed to copy to clipboard:', err)
      }
    }
    
    // Time formatting
    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown'
      return new Date(dateString).toLocaleString()
    }
    
    const formatLastUpdate = (timestamp) => {
      const seconds = Math.floor((Date.now() - timestamp) / 1000)
      if (seconds < 5) return 'just now'
      if (seconds < 60) return `${seconds}s ago`
      const minutes = Math.floor(seconds / 60)
      if (minutes < 60) return `${minutes}m ago`
      const hours = Math.floor(minutes / 60)
      return `${hours}h ago`
    }
    
    const getExecutionDuration = () => {
      if (!task.value?.created_at) return 'Unknown'
      const start = new Date(task.value.created_at)
      const end = task.value.completed_at ? new Date(task.value.completed_at) : new Date()
      const duration = Math.floor((end - start) / 1000)
      
      if (duration < 60) return `${duration}s`
      if (duration < 3600) return `${Math.floor(duration / 60)}m ${duration % 60}s`
      const hours = Math.floor(duration / 3600)
      const minutes = Math.floor((duration % 3600) / 60)
      return `${hours}h ${minutes}m`
    }
    
    const getProgressStatus = () => {
      if (!task.value) return 'Loading...'
      if (task.value.status === 'completed') return '✅ Completed successfully'
      if (task.value.status === 'failed') return '❌ Execution failed'
      if (task.value.status === 'running') return '⚡ Executing...'
      return '⏳ Pending execution'
    }
    
    const getETA = () => {
      if (!task.value || task.value.status !== 'running') return null
      const completedSteps = getCurrentStep() - 1
      const totalSteps = getTotalSteps()
      if (completedSteps === 0) return null
      
      const startTime = new Date(task.value.created_at)
      const currentTime = new Date()
      const elapsedMs = currentTime - startTime
      const avgTimePerStep = elapsedMs / completedSteps
      const remainingSteps = totalSteps - completedSteps
      const etaMs = avgTimePerStep * remainingSteps
      
      if (etaMs < 60000) return `~${Math.round(etaMs / 1000)}s remaining`
      if (etaMs < 3600000) return `~${Math.round(etaMs / 60000)}m remaining`
      return `~${Math.round(etaMs / 3600000)}h remaining`
    }
    
    // Live output
    const hasLiveOutput = computed(() => {
      return Object.keys(liveOutputs.value).length > 0 && Object.values(liveOutputs.value).some(output => output.trim())
    })
    
    const getLiveOutputText = () => {
      return Object.values(liveOutputs.value).join('')
    }
    
    const clearLiveOutput = () => {
      liveOutputs.value = {}
    }
    
    const scrollToBottom = () => {
      nextTick(() => {
        if (terminalContainer.value) {
          terminalContainer.value.scrollTop = terminalContainer.value.scrollHeight
        }
      })
    }
    
    // User interaction
    const sendUserInput = () => {
      if (!userInput.value.trim() || !currentSubtaskId.value) return
      
      // Add to live output
      const input = userInput.value.trim()
      if (liveOutputs.value[currentSubtaskId.value]) {
        liveOutputs.value[currentSubtaskId.value] += `\n> ${input}\n`
      }
      
      // Send via WebSocket
      wsSendUserInput(task.value.task_id, task.value.machine_id, input)
      
      // Clear input and waiting state
      userInput.value = ''
      isWaitingForInput.value = false
      currentSubtaskId.value = null
    }
    
    // Method details
    const toggleMethodDetails = (index) => {
      const idx = expandedMethods.value.indexOf(index)
      if (idx >= 0) {
        expandedMethods.value.splice(idx, 1)
      } else {
        expandedMethods.value.push(index)
      }
    }
    
    // AI Summary generation
    const generateAISummary = async () => {
      if (!task.value || task.value.status !== 'completed') return
      
      try {
        isGeneratingAISummary.value = true
        await api.post(`/tasks/${task.value.task_id}/generate-summary`)
        // The WebSocket will handle the update
      } catch (error) {
        console.error('Failed to generate AI summary:', error)
        isGeneratingAISummary.value = false
      }
    }
    
    // WebSocket event handlers
    const handleLiveOutput = (message) => {
      if (message.task_id === route.params.id) {
        const subtaskId = message.subtask_id || 'default'
        
        if (!liveOutputs.value[subtaskId]) {
          liveOutputs.value[subtaskId] = ''
        }
        
        liveOutputs.value[subtaskId] += message.data
        scrollToBottom()
      }
    }
    
    
    const handleInteractivePrompt = (message) => {
      if (message.task_id === route.params.id) {
        const subtaskId = message.subtask_id || 'default'
        currentSubtaskId.value = subtaskId
        isWaitingForInput.value = true
        
        // Add prompt to output
        if (!liveOutputs.value[subtaskId]) {
          liveOutputs.value[subtaskId] = ''
        }
        liveOutputs.value[subtaskId] += `\n${message.data}`
        
        // Focus input
        nextTick(() => {
          if (userInputField.value) {
            userInputField.value.focus()
          }
        })
      }
    }
    
    const handleTaskUpdate = (message) => {
      if (message.task_id === route.params.id) {
        console.log('📊 Received task update via WebSocket:', message)
        // Reload task data immediately when updates are received
        loadTask()
        console.log('🔄 Task data refreshed due to WebSocket update')
      }
    }
    
    const handleAISummaryUpdate = (message) => {
      if (message.task_id === route.params.id) {
        console.log('🤖 Received AI summary update via WebSocket:', message.ai_summary)
        // Update AI summary in real-time
        if (task.value) {
          task.value.ai_summary = message.ai_summary
          lastAISummaryUpdate.value = Date.now()
          isGeneratingAISummary.value = false
          console.log('✅ AI summary updated in real-time without refresh!')
        } else {
          console.log('⚠️ Task not loaded yet, will reload task data to get AI summary')
          // If task isn't loaded yet, reload to get the summary
          loadTask()
        }
      }
    }
    
    // Handle log events from TaskLogsViewer
    const handleLogEvent = (logEntry) => {
      console.log('📋 TaskDetails received log event:', logEntry)
      
      // Trigger task refresh for important events
      if (logEntry.type === 'task_update' || logEntry.type === 'command_result') {
        console.log('🔄 Important log event detected, refreshing task data...')
        setTimeout(() => {
          loadTask()
        }, 100)
      }
      
      if (logEntry.level === 'critical' || logEntry.level === 'error') {
        console.warn('⚠️ Critical system event:', logEntry.message)
      }
    }
    
    // Lifecycle
    onMounted(async () => {
      console.log('🚀 TaskDetailsModern mounted for task:', route.params.id)
      console.log('🔌 WebSocket connected?', isConnected.value)
      
      await loadTask()
      
      // Always start auto-refresh regardless of task status
      console.log('▶️ Starting 1-second force auto-refresh for ALL task data')
      startAutoRefresh()
      
      // Keep WebSocket listeners for live output and user interaction
      on('live_output', handleLiveOutput)
      on('interactive_prompt', handleInteractivePrompt)
      on('waiting_for_input', handleInteractivePrompt)
    })
    
    onUnmounted(() => {
      stopAutoRefresh()
      
      // Clean up WebSocket listeners
      off('live_output', handleLiveOutput)
      off('interactive_prompt', handleInteractivePrompt)
      off('waiting_for_input', handleInteractivePrompt)
    })
    
    return {
      // Data
      task,
      error,
      lastRefresh,
      lastAISummaryUpdate,
      isGeneratingAISummary,
      isConnected,
      
      // Live output
      hasLiveOutput,
      liveOutputs,
      terminalContainer,
      getLiveOutputText,
      clearLiveOutput,
      scrollToBottom,
      
      // User interaction
      userInput,
      userInputField,
      isWaitingForInput,
      sendUserInput,
      
      // UI state
      expandedMethods,
      toggleMethodDetails,
      
      // Status helpers
      getStatusClasses,
      getStatusIcon,
      getStatusText,
      
      // Progress helpers
      getCurrentStep,
      getTotalSteps,
      getProgressPercentage,
      getSuccessfulSteps,
      getSuccessRate,
      getProgressStatus,
      getETA,
      
      // Step helpers
      getStepTitle,
      getStepCardClasses,
      getStepNumberClasses,
      getStepStatus,
      getStepStatusIcon,
      getStepStatusText,
      getStepStatusTextClasses,
      
      // Compact step helpers
      getCompactStepClasses,
      getCompactStatusBadge,
      getCompactStepTitle,
      getCompactCommand,
      copyToClipboard,
      
      // Time helpers
      formatDate,
      formatLastUpdate,
      getExecutionDuration,
      
      // Actions
      loadTask,
      generateAISummary,
      handleLogEvent
    }
  }
}
</script>

