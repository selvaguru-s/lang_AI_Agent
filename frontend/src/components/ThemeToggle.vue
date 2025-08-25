<template>
  <div class="relative">
    <button
      @click="toggleTheme"
      :class="[
        'relative flex items-center justify-center w-10 h-10 rounded-xl transition-all duration-300',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        themeStore.isDarkMode 
          ? 'bg-gray-800 hover:bg-gray-700 text-yellow-400 focus:ring-yellow-500' 
          : 'bg-white hover:bg-gray-50 text-orange-500 focus:ring-orange-500 shadow-soft'
      ]"
      :title="themeStore.isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
    >
      <!-- Sun Icon (Light Mode) -->
      <svg
        v-if="!themeStore.isDarkMode"
        class="w-5 h-5 transition-transform duration-300 hover:rotate-90"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path
          fill-rule="evenodd"
          d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
          clip-rule="evenodd"
        />
      </svg>
      
      <!-- Moon Icon (Dark Mode) -->
      <svg
        v-else
        class="w-5 h-5 transition-transform duration-300 hover:-rotate-12"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path
          d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"
        />
      </svg>
      
      <!-- Subtle animation overlay -->
      <div
        :class="[
          'absolute inset-0 rounded-xl transition-opacity duration-300',
          themeStore.isDarkMode 
            ? 'bg-gradient-to-br from-yellow-400/20 to-orange-400/20 opacity-0 hover:opacity-100'
            : 'bg-gradient-to-br from-orange-400/20 to-yellow-400/20 opacity-0 hover:opacity-100'
        ]"
      ></div>
    </button>
    
    <!-- Tooltip -->
    <div
      v-if="showTooltip"
      :class="[
        'absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2',
        'px-3 py-2 text-xs font-medium rounded-lg shadow-lg pointer-events-none',
        'transition-all duration-200 z-50',
        themeStore.isDarkMode 
          ? 'bg-gray-700 text-gray-200 border border-gray-600'
          : 'bg-gray-900 text-white'
      ]"
    >
      {{ themeStore.isDarkMode ? 'Light Mode' : 'Dark Mode' }}
      
      <!-- Tooltip Arrow -->
      <div
        :class="[
          'absolute top-full left-1/2 transform -translate-x-1/2',
          'border-4 border-transparent',
          themeStore.isDarkMode 
            ? 'border-t-gray-700'
            : 'border-t-gray-900'
        ]"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
const showTooltip = ref(false)

const toggleTheme = () => {
  themeStore.toggleTheme()
  
  // Brief visual feedback
  showTooltip.value = true
  setTimeout(() => {
    showTooltip.value = false
  }, 1500)
}
</script>

<style scoped>
/* Custom hover effects */
button:hover svg {
  filter: drop-shadow(0 0 8px currentColor);
}

/* Smooth theme transition */
* {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}
</style>