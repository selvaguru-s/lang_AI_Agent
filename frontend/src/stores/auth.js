import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  onAuthStateChanged
} from 'firebase/auth'
import { auth } from '@/services/firebase'
import { authAPI } from '@/services/api'
import { websocketService } from '@/services/websocket'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const apiKey = ref(localStorage.getItem('apiKey') || null)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!user.value && !!apiKey.value)
  const userInfo = computed(() => ({
    uid: user.value?.uid,
    email: user.value?.email,
    displayName: user.value?.displayName,
    photoURL: user.value?.photoURL
  }))

  // Actions
  const setUser = async (userData) => {
    user.value = userData
    // Get and store the Firebase ID token for API calls
    if (userData) {
      try {
        const idToken = await userData.getIdToken()
        user.value.accessToken = idToken
      } catch (error) {
        console.error('Failed to get Firebase ID token:', error)
      }
    }
  }

  const setApiKey = async (key) => {
    apiKey.value = key
    if (key) {
      localStorage.setItem('apiKey', key)
      // Connect WebSocket when API key is set
      try {
        console.log('🔗 Attempting to connect WebSocket with API key:', key?.substring(0, 8) + '...')
        await websocketService.connect(key)
        console.log('✅ WebSocket connected successfully from auth store')
      } catch (error) {
        console.error('❌ Failed to connect WebSocket from auth store:', error)
      }
    } else {
      localStorage.removeItem('apiKey')
      // Disconnect WebSocket when API key is removed
      websocketService.disconnect()
    }
  }

  const setError = (errorMessage) => {
    error.value = errorMessage
  }

  const clearError = () => {
    error.value = null
  }

  const loginWithEmailPassword = async (email, password) => {
    try {
      isLoading.value = true
      clearError()
      
      const userCredential = await signInWithEmailAndPassword(auth, email, password)
      const idToken = await userCredential.user.getIdToken()
      
      // Get API key from backend
      const response = await authAPI.login(idToken)
      
      await setUser(userCredential.user)
      await setApiKey(response.data.api_key)
      
      return response.data
    } catch (error) {
      console.error('Login error:', error)
      setError(error.message)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const signupWithEmailPassword = async (email, password) => {
    try {
      isLoading.value = true
      clearError()
      
      const userCredential = await createUserWithEmailAndPassword(auth, email, password)
      const idToken = await userCredential.user.getIdToken()
      
      // Get API key from backend
      const response = await authAPI.login(idToken)
      
      await setUser(userCredential.user)
      await setApiKey(response.data.api_key)
      
      return response.data
    } catch (error) {
      console.error('Signup error:', error)
      setError(error.message)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const loginWithGoogle = async () => {
    try {
      isLoading.value = true
      clearError()
      
      const provider = new GoogleAuthProvider()
      const userCredential = await signInWithPopup(auth, provider)
      const idToken = await userCredential.user.getIdToken()
      
      // Get API key from backend
      const response = await authAPI.login(idToken)
      
      await setUser(userCredential.user)
      await setApiKey(response.data.api_key)
      
      return response.data
    } catch (error) {
      console.error('Google login error:', error)
      setError(error.message)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      await signOut(auth)
      setUser(null)
      await setApiKey(null)
      clearError()
    } catch (error) {
      console.error('Logout error:', error)
      setError(error.message)
      throw error
    }
  }

  const refreshToken = async () => {
    try {
      if (!user.value) return false
      
      const idToken = await user.value.getIdToken(true)
      const response = await authAPI.refresh(idToken)
      
      await setApiKey(response.data.api_key)
      return true
    } catch (error) {
      console.error('Token refresh error:', error)
      // If refresh fails, logout user
      await logout()
      return false
    }
  }

  const initializeAuth = () => {
    return new Promise((resolve) => {
      const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
        if (firebaseUser) {
          await setUser(firebaseUser)
          
          // If we have an API key, we're good
          if (apiKey.value) {
            resolve(true)
          } else {
            // Try to get API key
            try {
              const idToken = await firebaseUser.getIdToken()
              const response = await authAPI.login(idToken)
              await setApiKey(response.data.api_key)
              resolve(true)
            } catch (error) {
              console.error('Failed to get API key:', error)
              await logout()
              resolve(false)
            }
          }
        } else {
          setUser(null)
          await setApiKey(null)
          resolve(false)
        }
        unsubscribe()
      })
    })
  }

  return {
    // State
    user,
    apiKey,
    isLoading,
    error,
    
    // Getters
    isAuthenticated,
    userInfo,
    
    // Actions
    loginWithEmailPassword,
    signupWithEmailPassword,
    loginWithGoogle,
    logout,
    refreshToken,
    initializeAuth,
    clearError
  }
})