<template>
  <div class="tasks-modern">
    <!-- Header Section -->
    <div class="header-section">
      <div class="header-card">
        <div class="header-content">
          <div class="header-left">
            <h1>Task Management</h1>
            <div class="connection-status">
              <span class="status-dot" :class="isConnected ? 'online' : 'offline'"></span>
              <span class="status-text">{{ isConnected ? 'Real-time updates active' : 'Connecting...' }}</span>
            </div>
          </div>
          <button @click="showCreateModal = true" class="create-btn">
            <span class="btn-icon">✨</span>
            Create New Task
          </button>
        </div>
      </div>
    </div>

    <!-- Tasks Grid -->
    <div class="tasks-grid">
      <div v-for="task in tasks" :key="task.task_id" class="modern-task-card">
        <div class="task-card-header">
          <div class="task-info">
            <h3 class="task-title">{{ task.original_prompt }}</h3>
            <div class="task-meta">
              <span class="machine-badge">{{ task.machine_id }}</span>
              <span class="date-badge">{{ formatDate(task.created_at) }}</span>
            </div>
          </div>
          <div class="status-badge" :class="`status-${task.status}`">
            <span class="status-icon">{{ getStatusIcon(task.status) }}</span>
            <span class="status-text">{{ task.status }}</span>
          </div>
        </div>
        
        <div class="progress-section">
          <div class="progress-info">
            <span>Progress: {{ task.current_subtask_index + 1 }}/{{ task.subtasks.length }}</span>
            <span class="percentage">{{ Math.round(((task.current_subtask_index + 1) / task.subtasks.length) * 100) }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: Math.round(((task.current_subtask_index + 1) / task.subtasks.length) * 100) + '%' }"></div>
          </div>
        </div>
        
        <div class="task-actions">
          <router-link :to="`/tasks/${task.task_id}`" class="view-details-btn">
            <span class="btn-icon">👁️</span>
            View Details
          </router-link>
        </div>
      </div>
    </div>

    <!-- Create Task Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modern-modal">
        <div class="modal-header">
          <h2>✨ Create New Task</h2>
          <button @click="showCreateModal = false" class="close-btn">&times;</button>
        </div>
        <form @submit.prevent="createTask" class="modal-form">
          <div class="form-group">
            <label class="form-label">Task Description:</label>
            <textarea v-model="newTask.prompt" required rows="4" class="form-textarea" placeholder="Describe what you want to accomplish..."></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Machine ID:</label>
            <input v-model="newTask.machine_id" required class="form-input" placeholder="Enter target machine ID" />
          </div>
          <div class="form-actions">
            <button type="button" @click="showCreateModal = false" class="cancel-btn">Cancel</button>
            <button type="submit" class="submit-btn">
              <span class="btn-icon">🚀</span>
              Create Task
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWebSocket } from '@/services/websocket'
import { tasksAPI } from '@/services/api'

export default {
  name: 'Tasks',
  setup() {
    const tasks = ref([])
    const showCreateModal = ref(false)
    const newTask = ref({
      prompt: '',
      machine_id: ''
    })
    const authStore = useAuthStore()
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
      isConnected
    }
  }
}
</script>

<style scoped>
.tasks-modern {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.header-section {
  margin-bottom: 2rem;
}

.header-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 700;
  color: #2d3748;
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
  animation: pulse 2s infinite;
}

.status-dot.online {
  background: #48bb78;
}

.status-dot.offline {
  background: #f56565;
}

.status-text {
  font-size: 0.9rem;
  color: #4a5568;
  font-weight: 500;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.btn-icon {
  font-size: 1.1em;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.modern-task-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.modern-task-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
}

.task-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.task-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
  line-height: 1.4;
}

.task-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.machine-badge,
.date-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 500;
}

.machine-badge {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  font-family: 'Courier New', monospace;
}

.date-badge {
  background: rgba(113, 128, 150, 0.1);
  color: #4a5568;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
  color: white;
}

.status-pending { background: linear-gradient(135deg, #fbb6ce, #f093fb); }
.status-running { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.status-completed { background: linear-gradient(135deg, #43e97b, #38f9d7); }
.status-failed { background: linear-gradient(135deg, #fa709a, #fee140); }

.progress-section {
  margin: 1rem 0;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #4a5568;
  font-weight: 600;
}

.percentage {
  color: #667eea;
  font-weight: 700;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
  transition: width 0.5s ease;
}

.task-actions {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.view-details-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.view-details-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: translateX(4px);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modern-modal {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 0;
  width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slideUp 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #2d3748;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #718096;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #2d3748;
  background: rgba(0, 0, 0, 0.1);
}

.modal-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #2d3748;
  font-size: 0.9rem;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.8);
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  background: white;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.cancel-btn,
.submit-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.cancel-btn {
  background: rgba(113, 128, 150, 0.1);
  color: #4a5568;
}

.cancel-btn:hover {
  background: rgba(113, 128, 150, 0.2);
}

.submit-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.submit-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(102, 126, 234, 0.4);
}

/* Responsive Design */
@media (max-width: 768px) {
  .tasks-modern {
    padding: 0.5rem;
  }
  
  .header-card {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .tasks-grid {
    grid-template-columns: 1fr;
  }
  
  .task-card-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .status-badge {
    align-self: flex-start;
  }
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>