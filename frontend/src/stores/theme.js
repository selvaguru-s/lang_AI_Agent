import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDarkMode = ref(false)
  
  // Initialize theme from localStorage or system preference
  const initializeTheme = () => {
    // Check localStorage first
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      isDarkMode.value = savedTheme === 'dark'
    } else {
      // Check system preference
      isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    
    // Apply the theme
    applyTheme()
  }
  
  // Apply theme to document
  const applyTheme = () => {
    const htmlElement = document.documentElement
    if (isDarkMode.value) {
      htmlElement.classList.add('dark')
    } else {
      htmlElement.classList.remove('dark')
    }
  }
  
  // Toggle theme
  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value
    localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
    applyTheme()
  }
  
  // Set specific theme
  const setTheme = (theme) => {
    isDarkMode.value = theme === 'dark'
    localStorage.setItem('theme', theme)
    applyTheme()
  }
  
  // Computed properties
  const currentTheme = computed(() => isDarkMode.value ? 'dark' : 'light')
  const themeIcon = computed(() => isDarkMode.value ? '🌙' : '☀️')
  
  // Professional color getters based on theme
  const colors = computed(() => ({
    // Background colors
    bg: {
      primary: isDarkMode.value ? 'bg-gray-900' : 'bg-white',
      secondary: isDarkMode.value ? 'bg-gray-800' : 'bg-gray-50',
      tertiary: isDarkMode.value ? 'bg-gray-850' : 'bg-gray-100',
      overlay: isDarkMode.value ? 'bg-gray-800/90' : 'bg-white/90',
      card: isDarkMode.value ? 'bg-gray-800/50' : 'bg-white/80',
    },
    // Text colors
    text: {
      primary: isDarkMode.value ? 'text-gray-100' : 'text-gray-900',
      secondary: isDarkMode.value ? 'text-gray-300' : 'text-gray-600',
      tertiary: isDarkMode.value ? 'text-gray-400' : 'text-gray-500',
      muted: isDarkMode.value ? 'text-gray-500' : 'text-gray-400',
    },
    // Border colors
    border: {
      primary: isDarkMode.value ? 'border-gray-700' : 'border-gray-200',
      secondary: isDarkMode.value ? 'border-gray-600' : 'border-gray-300',
      focus: isDarkMode.value ? 'border-primary-400' : 'border-primary-500',
    },
    // Status colors remain consistent but adapt to theme
    status: {
      success: {
        bg: isDarkMode.value ? 'bg-success-900/20' : 'bg-success-50',
        text: isDarkMode.value ? 'text-success-400' : 'text-success-700',
        border: isDarkMode.value ? 'border-success-800' : 'border-success-200',
        icon: isDarkMode.value ? 'text-success-400' : 'text-success-600',
      },
      error: {
        bg: isDarkMode.value ? 'bg-error-900/20' : 'bg-error-50',
        text: isDarkMode.value ? 'text-error-400' : 'text-error-700',
        border: isDarkMode.value ? 'border-error-800' : 'border-error-200',
        icon: isDarkMode.value ? 'text-error-400' : 'text-error-600',
      },
      warning: {
        bg: isDarkMode.value ? 'bg-warning-900/20' : 'bg-warning-50',
        text: isDarkMode.value ? 'text-warning-400' : 'text-warning-700',
        border: isDarkMode.value ? 'border-warning-800' : 'border-warning-200',
        icon: isDarkMode.value ? 'text-warning-400' : 'text-warning-600',
      },
      info: {
        bg: isDarkMode.value ? 'bg-info-900/20' : 'bg-info-50',
        text: isDarkMode.value ? 'text-info-400' : 'text-info-700',
        border: isDarkMode.value ? 'border-info-800' : 'border-info-200',
        icon: isDarkMode.value ? 'text-info-400' : 'text-info-600',
      },
      running: {
        bg: isDarkMode.value ? 'bg-primary-900/20' : 'bg-primary-50',
        text: isDarkMode.value ? 'text-primary-400' : 'text-primary-700',
        border: isDarkMode.value ? 'border-primary-800' : 'border-primary-200',
        icon: isDarkMode.value ? 'text-primary-400' : 'text-primary-600',
      },
    },
  }))
  
  // Gradient backgrounds
  const gradients = computed(() => ({
    primary: isDarkMode.value 
      ? 'bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900'
      : 'bg-gradient-to-br from-primary-50 via-blue-50 to-indigo-50',
    success: isDarkMode.value
      ? 'bg-gradient-to-br from-success-900 to-success-800'
      : 'bg-gradient-to-br from-success-500 to-success-600',
    error: isDarkMode.value
      ? 'bg-gradient-to-br from-error-900 to-error-800'
      : 'bg-gradient-to-br from-error-500 to-error-600',
    warning: isDarkMode.value
      ? 'bg-gradient-to-br from-warning-900 to-warning-800'
      : 'bg-gradient-to-br from-warning-500 to-warning-600',
    info: isDarkMode.value
      ? 'bg-gradient-to-br from-info-900 to-info-800'
      : 'bg-gradient-to-br from-info-500 to-info-600',
  }))
  
  return {
    // State
    isDarkMode,
    
    // Actions
    initializeTheme,
    toggleTheme,
    setTheme,
    
    // Getters
    currentTheme,
    themeIcon,
    colors,
    gradients,
  }
})