<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useWebSocket } from '@/services/websocket'

const authStore = useAuthStore()
const { connect, disconnect } = useWebSocket()

onMounted(async () => {
  // Initialize authentication
  await authStore.initializeAuth()
  
  // Connect WebSocket if authenticated
  if (authStore.isAuthenticated) {
    try {
      await connect(authStore.apiKey)
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
    }
  }
})

// Watch for auth changes to manage WebSocket connection
authStore.$subscribe((mutation, state) => {
  if (state.isAuthenticated && state.apiKey) {
    connect(state.apiKey).catch(console.error)
  } else {
    disconnect()
  }
})
</script>