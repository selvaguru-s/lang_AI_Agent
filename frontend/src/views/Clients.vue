<template>
  <div :class="['min-h-screen transition-all duration-300', themeStore.gradients.primary]">
    <!-- Header Section -->
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div :class="['backdrop-blur-sm rounded-2xl shadow-xl border overflow-hidden mb-8', themeStore.colors.bg.card, themeStore.colors.border.primary]">
        <div class="px-8 py-6 flex justify-between items-center">
          <div>
            <h1 :class="['text-3xl font-bold mb-2', themeStore.colors.text.primary]">Client Machines</h1>
            <div class="flex items-center space-x-4">
              <span :class="['text-sm font-medium', themeStore.colors.text.secondary]">{{ clients.length }} total clients</span>
              <span :class="['text-sm font-semibold', themeStore.colors.status.success.text]">{{ getActiveCount() }} active</span>
            </div>
          </div>
          <button @click="loadClients" :class="['flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold text-white transition-all duration-200 transform hover:scale-105', themeStore.gradients.info, 'shadow-lg hover:shadow-xl']">
            <span>🔄</span>
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <!-- Clients Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="client in clients" :key="client.machine_id || client.id" :class="['backdrop-blur-sm rounded-2xl shadow-xl border overflow-hidden transition-all duration-300 hover:scale-105', themeStore.colors.bg.card, themeStore.colors.border.primary]">
          <div class="p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <h3 :class="['text-xl font-bold mb-2', themeStore.colors.text.primary]">{{ client.hostname }}</h3>
                <div :class="['text-xs font-mono px-3 py-1 rounded-lg inline-block', themeStore.colors.bg.tertiary, themeStore.colors.text.secondary]">{{ client.machine_id || client.id }}</div>
              </div>
              <StatusBadge :status="client.is_active ? 'online' : 'offline'" />
            </div>
            <div class="space-y-4">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <div :class="['text-xs font-semibold uppercase tracking-wide mb-1', themeStore.colors.text.tertiary]">Operating System</div>
                  <div :class="['px-3 py-2 rounded-lg text-sm font-medium', themeStore.colors.status.info.bg, themeStore.colors.status.info.text]">{{ client.os_info }}</div>
                </div>
                <div>
                  <div :class="['text-xs font-semibold uppercase tracking-wide mb-1', themeStore.colors.text.tertiary]">Architecture</div>
                  <div :class="['px-3 py-2 rounded-lg text-sm font-mono', themeStore.colors.bg.tertiary, themeStore.colors.text.primary]">{{ client.architecture }}</div>
                </div>
              </div>
              
              <div>
                <div :class="['text-xs font-semibold uppercase tracking-wide mb-1', themeStore.colors.text.tertiary]">Last Seen</div>
                <div :class="['text-sm font-semibold', themeStore.colors.status.info.text]">{{ getRelativeTime(client.last_seen) }}</div>
              </div>
            </div>
            
            <div class="mt-6 pt-4 border-t" :class="themeStore.colors.border.secondary">
              <button @click="pingClient(client)" :disabled="!client.is_active" :class="['w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-xl font-semibold transition-all duration-200', client.is_active ? `${themeStore.colors.status.info.bg} ${themeStore.colors.status.info.text} hover:opacity-80` : `${themeStore.colors.bg.tertiary} ${themeStore.colors.text.tertiary} cursor-not-allowed`]">
              <span>📡</span>
              <span>Ping Client</span>
            </button>
            </div>
          </div>
        </div>
        
        <!-- Empty State -->
        <div v-if="clients.length === 0" :class="['col-span-full flex flex-col items-center justify-center py-16', themeStore.colors.text.secondary]">
          <div class="text-6xl mb-4 opacity-50">💻</div>
          <h3 :class="['text-xl font-bold mb-2', themeStore.colors.text.primary]">No Client Machines Found</h3>
          <p :class="['text-sm mb-6', themeStore.colors.text.secondary]">Connect your first Linux client to get started.</p>
          <button @click="loadClients" :class="['flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold text-white transition-all duration-200 transform hover:scale-105', themeStore.gradients.info, 'shadow-lg hover:shadow-xl']">
            <span>🔄</span>
            <span>Check Again</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { clientsAPI } from '@/services/api'
import StatusBadge from '@/components/StatusBadge.vue'

export default {
  name: 'Clients',
  components: {
    StatusBadge
  },
  setup() {
    const clients = ref([])
    const authStore = useAuthStore()
    const themeStore = useThemeStore()

    const loadClients = async () => {
      try {
        const response = await clientsAPI.list()
        clients.value = response.data
      } catch (error) {
        console.error('Failed to load clients:', error)
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString()
    }
    
    const getRelativeTime = (dateString) => {
      const now = new Date()
      const date = new Date(dateString)
      const diffMs = now - date
      const diffMins = Math.floor(diffMs / 60000)
      
      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins}m ago`
      
      const diffHours = Math.floor(diffMins / 60)
      if (diffHours < 24) return `${diffHours}h ago`
      
      const diffDays = Math.floor(diffHours / 24)
      if (diffDays < 30) return `${diffDays}d ago`
      
      return formatDate(dateString)
    }
    
    const getActiveCount = () => {
      return clients.value.filter(client => client.is_active).length
    }
    
    const pingClient = async (client) => {
      try {
        console.log('Pinging client:', client.machine_id || client.id)
        // TODO: Implement ping client API call
        alert(`Ping sent to ${client.hostname}`)
      } catch (error) {
        console.error('Failed to ping client:', error)
        alert('Failed to ping client')
      }
    }

    onMounted(() => {
      loadClients()
    })

    return {
      clients,
      formatDate,
      getRelativeTime,
      getActiveCount,
      pingClient,
      loadClients,
      themeStore
    }
  }
}
</script>

<style scoped>
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