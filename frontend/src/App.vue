<template>
  <div 
    id="app" 
    :class="[
      'min-h-screen transition-colors duration-300',
      themeStore.colors.bg.secondary
    ]"
  >
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useWebSocket } from '@/services/websocket'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const { connect, disconnect } = useWebSocket()

onMounted(async () => {
  // Initialize theme first (for smooth loading)
  themeStore.initializeTheme()
  
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

<style>
/* Global theme transition for smooth mode switching */
* {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke, box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Scrollbar styling for dark mode */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gray-600 rounded-full;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400 dark:bg-gray-500;
}

/* Selection styling for dark mode */
::selection {
  @apply bg-primary-200 text-primary-900 dark:bg-primary-800 dark:text-primary-100;
}

/* Focus visible styling */
:focus-visible {
  outline: 2px solid theme('colors.primary.500');
  outline-offset: 2px;
}
</style>