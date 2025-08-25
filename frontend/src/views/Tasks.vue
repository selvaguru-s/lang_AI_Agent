<template>
  <div :class="['min-h-screen transition-all duration-300', themeStore.gradients.primary]">
    <!-- Header Section -->
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div :class="['backdrop-blur-sm rounded-2xl shadow-xl border overflow-hidden mb-8', themeStore.colors.bg.card, themeStore.colors.border.primary]">
        <div class="px-8 py-6 flex justify-between items-center">
          <div>
            <h1 :class="['text-3xl font-bold mb-2', themeStore.colors.text.primary]">Task Management</h1>
            <div class="flex items-center space-x-2">
              <div class="w-2 h-2 rounded-full animate-pulse" :class="isConnected ? 'bg-success-500' : 'bg-error-500'"></div>
              <span :class="['text-sm font-medium', themeStore.colors.text.secondary]">{{ isConnected ? 'Real-time updates active' : 'Connecting...' }}</span>
            </div>
          </div>
          <button @click="showCreateModal = true" :class="['flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold text-white transition-all duration-200 transform hover:scale-105', themeStore.gradients.info, 'shadow-lg hover:shadow-xl']">
            <span>✨</span>
            <span>Create New Task</span>
          </button>
        </div>
      </div>

      <!-- Tasks Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="task in tasks" :key="task.task_id" :class="['backdrop-blur-sm rounded-2xl shadow-xl border overflow-hidden transition-all duration-300 hover:scale-105', themeStore.colors.bg.card, themeStore.colors.border.primary]">
          <div class="p-6">
            <div class="flex justify-between items-start mb-4">
              <div class="flex-1 mr-4">
                <h3 :class="['text-lg font-bold mb-2 line-clamp-2', themeStore.colors.text.primary]">{{ task.original_prompt }}</h3>
                <div class="flex flex-wrap gap-2 mb-2">
                  <span :class="['text-xs font-mono px-2 py-1 rounded-lg', themeStore.colors.status.info.bg, themeStore.colors.status.info.text]">{{ task.machine_id }}</span>
                  <span :class="['text-xs px-2 py-1 rounded-lg', themeStore.colors.bg.tertiary, themeStore.colors.text.secondary]">{{ formatDate(task.created_at) }}</span>
                </div>
              </div>
              <StatusBadge :status="task.status" />
            </div>
            
            <div class="mb-4">
              <div class="flex justify-between items-center mb-2">
                <span :class="['text-sm font-medium', themeStore.colors.text.secondary]">Progress: {{ task.current_subtask_index + 1 }}/{{ task.subtasks.length }}</span>
                <span :class="['text-sm font-bold', themeStore.colors.status.info.text]">{{ Math.round(((task.current_subtask_index + 1) / task.subtasks.length) * 100) }}%</span>
              </div>
              <div :class="['w-full h-2 rounded-full overflow-hidden', themeStore.colors.bg.tertiary]">
                <div class="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500 rounded-full" :style="{ width: Math.round(((task.current_subtask_index + 1) / task.subtasks.length) * 100) + '%' }"></div>
              </div>
            </div>
            
            <div class="pt-4 border-t" :class="themeStore.colors.border.secondary">
              <router-link :to="`/tasks/${task.task_id}`" :class="['w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-xl font-semibold transition-all duration-200', themeStore.colors.status.info.bg, themeStore.colors.status.info.text, 'hover:opacity-80']">
                <span>👁️</span>
                <span>View Details</span>
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Create Task Modal -->
      <div v-if="showCreateModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50" @click.self="showCreateModal = false">
        <div :class="['w-full max-w-lg mx-4 rounded-2xl shadow-2xl border overflow-hidden', themeStore.colors.bg.card, themeStore.colors.border.primary]">
          <div class="px-6 py-4 border-b flex justify-between items-center" :class="themeStore.colors.border.secondary">
            <h2 :class="['text-xl font-bold', themeStore.colors.text.primary]">✨ Create New Task</h2>
            <button @click="showCreateModal = false" :class="['p-2 rounded-lg transition-colors', themeStore.colors.text.secondary, `hover:${themeStore.colors.bg.tertiary}`]">&times;</button>
          </div>
          <form @submit.prevent="createTask" class="p-6">
            <div class="space-y-4">
              <div>
                <label :class="['block text-sm font-semibold mb-2', themeStore.colors.text.primary]">Task Description:</label>
                <textarea v-model="newTask.prompt" required rows="4" :class="['w-full px-4 py-3 rounded-xl border transition-all duration-200 focus:ring-2 focus:ring-blue-500/20', themeStore.colors.bg.secondary, themeStore.colors.text.primary, themeStore.colors.border.secondary, 'focus:border-blue-500']" placeholder="Describe what you want to accomplish..."></textarea>
              </div>
              <div>
                <label :class="['block text-sm font-semibold mb-2', themeStore.colors.text.primary]">Machine ID:</label>
                <input v-model="newTask.machine_id" required :class="['w-full px-4 py-3 rounded-xl border transition-all duration-200 focus:ring-2 focus:ring-blue-500/20', themeStore.colors.bg.secondary, themeStore.colors.text.primary, themeStore.colors.border.secondary, 'focus:border-blue-500']" placeholder="Enter target machine ID" />
              </div>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button type="button" @click="showCreateModal = false" :class="['px-6 py-3 rounded-xl font-semibold transition-all duration-200', themeStore.colors.bg.tertiary, themeStore.colors.text.secondary, 'hover:opacity-80']">Cancel</button>
              <button type="submit" :class="['flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold text-white transition-all duration-200 transform hover:scale-105', themeStore.gradients.info, 'shadow-lg hover:shadow-xl']">
                <span>🚀</span>
                <span>Create Task</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useWebSocket } from '@/services/websocket'
import { tasksAPI } from '@/services/api'
import StatusBadge from '@/components/StatusBadge.vue'

export default {
  name: 'Tasks',
  components: {
    StatusBadge
  },
  setup() {
    const tasks = ref([])
    const showCreateModal = ref(false)
    const newTask = ref({
      prompt: '',
      machine_id: ''
    })
    const authStore = useAuthStore()
    const themeStore = useThemeStore()
    const router = useRouter()
    const { isConnected, on, off } = useWebSocket()

    const loadTasks = async () => {
      try {
        const response = await tasksAPI.list()
        tasks.value = response.data
      } catch (error) {
        console.error('Failed to load tasks:', error)
      }
    }

    const createTask = async () => {
      try {
        const response = await tasksAPI.create(newTask.value.prompt, newTask.value.machine_id)
        showCreateModal.value = false
        newTask.value = { prompt: '', machine_id: '' }
        
        // Auto-redirect to the new task
        router.push(`/tasks/${response.data.task_id}`)
      } catch (error) {
        console.error('Failed to create task:', error)
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString()
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

    // WebSocket event handlers for real-time updates
    const handleTaskUpdate = (data) => {
      // Find and update the task in the list
      const taskIndex = tasks.value.findIndex(t => t.task_id === data.task_id)
      if (taskIndex !== -1) {
        // Update existing task
        tasks.value[taskIndex].status = data.status
        if (data.status === 'completed' || data.status === 'failed') {
          // Reload the full task data to get latest info
          loadTasks()
        }
      } else {
        // New task created, reload list
        loadTasks()
      }
    }

    const handleTaskStarted = (data) => {
      // Reload tasks when a new one starts
      loadTasks()
    }

    onMounted(() => {
      loadTasks()
      
      // Set up real-time updates
      on('task_update', handleTaskUpdate)
      on('task_started', handleTaskStarted)
      
      // Auto-refresh every 5 seconds for better responsiveness
      const refreshInterval = setInterval(() => {
        console.log('🔄 Tasks page auto-refreshing...')
        loadTasks()
      }, 5000)
      
      // Cleanup on unmount
      onUnmounted(() => {
        clearInterval(refreshInterval)
        off('task_update', handleTaskUpdate)
        off('task_started', handleTaskStarted)
      })
    })

    return {
      tasks,
      showCreateModal,
      newTask,
      createTask,
      formatDate,
      getStatusIcon,
      isConnected,
      themeStore
    }
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Responsive Design */
@media (max-width: 768px) {
  .grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3 {
    grid-template-columns: 1fr;
  }
}

/* Animations */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>