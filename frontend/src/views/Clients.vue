<template>
  <div class="clients-modern">
    <!-- Header Section -->
    <div class="header-section">
      <div class="header-card">
        <div class="header-content">
          <div class="header-left">
            <h1>Client Machines</h1>
            <div class="clients-summary">
              <span class="total-count">{{ clients.length }} total clients</span>
              <span class="active-count">{{ getActiveCount() }} active</span>
            </div>
          </div>
          <div class="refresh-section">
            <button @click="loadClients" class="refresh-btn">
              <span class="btn-icon">🔄</span>
              Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Clients Grid -->
    <div class="clients-grid">
      <div v-for="client in clients" :key="client.machine_id || client.id" class="modern-client-card">
        <div class="client-header">
          <div class="client-info">
            <h3 class="client-hostname">{{ client.hostname }}</h3>
            <div class="client-id">{{ client.machine_id || client.id }}</div>
          </div>
          <div class="status-badge" :class="{ active: client.is_active }">
            <span class="status-dot"></span>
            <span class="status-text">{{ client.is_active ? 'Online' : 'Offline' }}</span>
          </div>
        </div>
        
        <div class="client-details">
          <div class="detail-row">
            <div class="detail-item">
              <div class="detail-label">Operating System</div>
              <div class="detail-value os-info">{{ client.os_info }}</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Architecture</div>
              <div class="detail-value arch-info">{{ client.architecture }}</div>
            </div>
          </div>
          
          <div class="detail-row">
            <div class="detail-item full-width">
              <div class="detail-label">Last Seen</div>
              <div class="detail-value last-seen">{{ getRelativeTime(client.last_seen) }}</div>
            </div>
          </div>
        </div>
        
        <div class="client-actions">
          <button @click="pingClient(client)" class="ping-btn" :disabled="!client.is_active">
            <span class="btn-icon">📡</span>
            Ping Client
          </button>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-if="clients.length === 0" class="empty-state">
      <div class="empty-icon">💻</div>
      <h3>No Client Machines Found</h3>
      <p>Connect your first Linux client to get started.</p>
      <button @click="loadClients" class="refresh-btn">
        <span class="btn-icon">🔄</span>
        Check Again
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { clientsAPI } from '@/services/api'

export default {
  name: 'Clients',
  setup() {
    const clients = ref([])
    const authStore = useAuthStore()

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
      loadClients
    }
  }
}
</script>

<style scoped>
.clients-modern {
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

.clients-summary {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
}

.total-count {
  color: #4a5568;
  font-weight: 500;
}

.active-count {
  color: #48bb78;
  font-weight: 600;
}

.refresh-btn {
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

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.btn-icon {
  font-size: 1.1em;
}

.clients-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.modern-client-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.modern-client-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
}

.client-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.client-hostname {
  margin: 0 0 0.5rem 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #2d3748;
}

.client-id {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: #718096;
  background: rgba(113, 128, 150, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  display: inline-block;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
  background: rgba(245, 101, 101, 0.1);
  color: #c53030;
  border: 1px solid rgba(245, 101, 101, 0.2);
}

.status-badge.active {
  background: rgba(72, 187, 120, 0.1);
  color: #2f855a;
  border-color: rgba(72, 187, 120, 0.2);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f56565;
  animation: pulse 2s infinite;
}

.status-badge.active .status-dot {
  background: #48bb78;
}

.client-details {
  margin-bottom: 1.5rem;
}

.detail-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-item {
  flex: 1;
}

.detail-item.full-width {
  flex: none;
  width: 100%;
}

.detail-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.25rem;
}

.detail-value {
  font-size: 0.9rem;
  color: #2d3748;
  font-weight: 500;
}

.os-info {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-weight: 600;
}

.arch-info {
  background: rgba(113, 128, 150, 0.1);
  color: #4a5568;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
}

.last-seen {
  color: #667eea;
  font-weight: 600;
}

.client-actions {
  padding-top: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.ping-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ping-btn:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.2);
  transform: translateY(-1px);
}

.ping-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(113, 128, 150, 0.1);
  color: #718096;
  border-color: rgba(113, 128, 150, 0.2);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
  color: white;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.7;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.empty-state p {
  margin: 0 0 2rem 0;
  opacity: 0.8;
  font-size: 1.1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .clients-modern {
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
  
  .clients-grid {
    grid-template-columns: 1fr;
  }
  
  .client-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .status-badge {
    align-self: flex-start;
  }
  
  .detail-row {
    flex-direction: column;
    gap: 0.5rem;
  }
}

/* Animations */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>