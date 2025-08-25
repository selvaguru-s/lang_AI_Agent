<template>
  <span
    :class="[
      'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium transition-all duration-200',
      statusClasses
    ]"
  >
    <span :class="['w-1.5 h-1.5 rounded-full mr-2', dotClass]"></span>
    {{ displayText }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (value) => ['online', 'offline', 'completed', 'running', 'failed', 'pending', 'active', 'inactive'].includes(value)
  },
  text: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'sm',
    validator: (value) => ['xs', 'sm', 'md'].includes(value)
  }
})

const themeStore = useThemeStore()

const displayText = computed(() => {
  if (props.text) return props.text
  
  // Default text based on status
  switch (props.status) {
    case 'online':
    case 'active': return 'Online'
    case 'offline':
    case 'inactive': return 'Offline'
    case 'completed': return 'Completed'
    case 'running': return 'Running'
    case 'failed': return 'Failed'
    case 'pending': return 'Pending'
    default: return props.status.charAt(0).toUpperCase() + props.status.slice(1)
  }
})

const statusClasses = computed(() => {
  const sizeClasses = {
    xs: 'px-2 py-0.5 text-xs',
    sm: 'px-3 py-1 text-xs',
    md: 'px-4 py-2 text-sm'
  }
  
  const baseClasses = sizeClasses[props.size]
  
  switch (props.status) {
    case 'online':
    case 'active':
    case 'completed':
      return `${baseClasses} ${themeStore.colors.status.success.bg} ${themeStore.colors.status.success.text} ${themeStore.colors.status.success.border} border`
      
    case 'offline':
    case 'inactive':
    case 'failed':
      return `${baseClasses} ${themeStore.colors.status.error.bg} ${themeStore.colors.status.error.text} ${themeStore.colors.status.error.border} border`
      
    case 'running':
      return `${baseClasses} ${themeStore.colors.status.running.bg} ${themeStore.colors.status.running.text} ${themeStore.colors.status.running.border} border animate-pulse`
      
    case 'pending':
      return `${baseClasses} ${themeStore.colors.status.warning.bg} ${themeStore.colors.status.warning.text} ${themeStore.colors.status.warning.border} border`
      
    default:
      return `${baseClasses} ${themeStore.colors.bg.tertiary} ${themeStore.colors.text.secondary} ${themeStore.colors.border.secondary} border`
  }
})

const dotClass = computed(() => {
  switch (props.status) {
    case 'online':
    case 'active':
    case 'completed':
      return 'bg-success-500'
      
    case 'offline':
    case 'inactive':
    case 'failed':
      return 'bg-error-500'
      
    case 'running':
      return 'bg-primary-500 animate-pulse'
      
    case 'pending':
      return 'bg-warning-500'
      
    default:
      return themeStore.isDarkMode ? 'bg-gray-400' : 'bg-gray-500'
  }
})
</script>

<style scoped>
/* Smooth status transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}
</style>