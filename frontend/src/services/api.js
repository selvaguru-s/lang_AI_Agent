import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.apiKey) {
      config.headers.Authorization = `Bearer ${authStore.apiKey}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (idToken) => api.post('/auth/login', { id_token: idToken }),
  refresh: (idToken) => api.post('/auth/refresh', { id_token: idToken }),
  getMe: () => api.get('/auth/me')
}

// Tasks API
export const tasksAPI = {
  create: (prompt, machineId) => api.post('/tasks', { prompt, machine_id: machineId }),
  getStatus: (taskId) => api.get(`/tasks/status/${taskId}`),
  list: (limit = 20, offset = 0) => api.get('/tasks/list', { params: { limit, offset } }),
  cancel: (taskId) => api.delete(`/tasks/${taskId}`)
}

// Clients API
export const clientsAPI = {
  register: (clientInfo) => api.post('/clients/register', clientInfo),
  list: () => api.get('/clients/list'),
  getDetails: (machineId) => api.get(`/clients/${machineId}`),
  remove: (machineId) => api.delete(`/clients/${machineId}`),
  ping: (machineId) => api.post(`/clients/${machineId}/ping`)
}

export default api