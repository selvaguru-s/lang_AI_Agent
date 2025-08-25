<template>
  <div :class="['min-h-screen transition-all duration-300', themeStore.isDarkMode ? 'bg-gray-900' : 'bg-gray-50']">
    <!-- Background Elements -->
    <div class="absolute inset-0 overflow-hidden">
      <!-- Animated Background Shapes -->
      <div class="absolute top-10 left-10 w-32 h-32 bg-blue-500/10 rounded-full blur-xl animate-pulse"></div>
      <div class="absolute top-1/3 right-20 w-40 h-40 bg-purple-500/10 rounded-full blur-xl animate-pulse" style="animation-delay: 1s;"></div>
      <div class="absolute bottom-20 left-1/4 w-28 h-28 bg-indigo-500/10 rounded-full blur-xl animate-pulse" style="animation-delay: 2s;"></div>
    </div>
    
    <div class="relative flex min-h-screen">
      <!-- Left Side - Enhanced Branding -->
      <div class="hidden lg:flex lg:w-1/2 items-center justify-center p-12 relative">
        <!-- Background Gradient -->
        <div class="absolute inset-0 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700"></div>
        <div class="absolute inset-0 bg-black/20"></div>
        
        <!-- Content -->
        <div class="relative text-center text-white max-w-lg z-10">
          <!-- Logo with Animation -->
          <div class="relative mb-8">
            <div class="w-24 h-24 mx-auto bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm" style="box-shadow: 0 0 40px rgba(255, 255, 255, 0.1);">
              <svg class="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
              </svg>
            </div>
            <!-- Pulsing Ring -->
            <div class="absolute inset-0 w-24 h-24 mx-auto rounded-2xl border-2 border-white/30 animate-ping"></div>
          </div>
          
          <h1 class="text-5xl font-bold mb-6 bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent">AI Linux Agent</h1>
          <p class="text-xl mb-10 text-white/90 leading-relaxed">Revolutionize your infrastructure management with intelligent command execution and real-time monitoring</p>
          
          <!-- Feature Cards -->
          <div class="space-y-4">
            <div class="flex items-center space-x-4 bg-white/10 backdrop-blur-sm rounded-lg p-4 transition-all duration-300 hover:bg-white/20">
              <div class="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-green-300" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm3.293 1.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L7.586 10 5.293 7.707a1 1 0 010-1.414zM11 12a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/>
                </svg>
              </div>
              <div class="text-left">
                <h3 class="font-semibold text-white">Smart Command Execution</h3>
                <p class="text-sm text-white/70">Execute complex commands with AI assistance</p>
              </div>
            </div>
            
            <div class="flex items-center space-x-4 bg-white/10 backdrop-blur-sm rounded-lg p-4 transition-all duration-300 hover:bg-white/20">
              <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-300" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
              </div>
              <div class="text-left">
                <h3 class="font-semibold text-white">Real-time Monitoring</h3>
                <p class="text-sm text-white/70">Monitor system performance and health</p>
              </div>
            </div>
            
            <div class="flex items-center space-x-4 bg-white/10 backdrop-blur-sm rounded-lg p-4 transition-all duration-300 hover:bg-white/20">
              <div class="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-purple-300" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"/>
                </svg>
              </div>
              <div class="text-left">
                <h3 class="font-semibold text-white">Multi-Server Management</h3>
                <p class="text-sm text-white/70">Manage multiple Linux servers from one place</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side - Forms -->
      <div class="flex-1 flex items-center justify-center p-6 sm:p-12 relative">
        <div class="w-full max-w-md">
          
          <!-- Mobile Logo -->
          <div class="lg:hidden text-center mb-8">
            <div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center" style="box-shadow: 0 -4px 16px -4px rgba(59, 130, 246, 0.3), 0 4px 16px -4px rgba(59, 130, 246, 0.3), -4px 0 16px -4px rgba(59, 130, 246, 0.3), 4px 0 16px -4px rgba(59, 130, 246, 0.3);">
              <svg class="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
              </svg>
            </div>
            <h2 :class="['text-3xl font-bold mb-2', themeStore.isDarkMode ? 'text-white' : 'text-gray-900']">AI Linux Agent</h2>
            <p :class="['text-sm', themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600']">Professional Infrastructure Management</p>
          </div>

          <!-- Auth Form Card -->
          <div :class="['rounded-2xl p-8 transition-all duration-300', themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white']" style="box-shadow: 0 -8px 32px -8px rgba(0, 0, 0, 0.1), 0 8px 32px -8px rgba(0, 0, 0, 0.1), -8px 0 32px -8px rgba(0, 0, 0, 0.1), 8px 0 32px -8px rgba(0, 0, 0, 0.1);">
            
            <!-- Mode Tabs -->
            <div class="mb-8">
              <div :class="['flex space-x-1 p-1 rounded-xl', themeStore.isDarkMode ? 'bg-gray-700' : 'bg-gray-100']">
                <button
                  @click="setMode('signin')"
                  :class="[
                    'flex-1 py-3 px-4 text-sm font-semibold rounded-lg transition-all duration-300 transform hover:scale-105',
                    currentMode === 'signin' 
                      ? (themeStore.isDarkMode ? 'bg-blue-600 text-white shadow-lg' : 'bg-white text-blue-600 shadow-md') 
                      : (themeStore.isDarkMode ? 'text-gray-300 hover:text-white hover:bg-gray-600' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200')
                  ]"
                >
                  Sign In
                </button>
                <button
                  @click="setMode('signup')"
                  :class="[
                    'flex-1 py-3 px-4 text-sm font-semibold rounded-lg transition-all duration-300 transform hover:scale-105',
                    currentMode === 'signup' 
                      ? (themeStore.isDarkMode ? 'bg-blue-600 text-white shadow-lg' : 'bg-white text-blue-600 shadow-md') 
                      : (themeStore.isDarkMode ? 'text-gray-300 hover:text-white hover:bg-gray-600' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200')
                  ]"
                >
                  Sign Up
                </button>
                <button
                  @click="setMode('reset')"
                  :class="[
                    'flex-1 py-3 px-4 text-sm font-semibold rounded-lg transition-all duration-300 transform hover:scale-105',
                    currentMode === 'reset' 
                      ? (themeStore.isDarkMode ? 'bg-blue-600 text-white shadow-lg' : 'bg-white text-blue-600 shadow-md') 
                      : (themeStore.isDarkMode ? 'text-gray-300 hover:text-white hover:bg-gray-600' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200')
                  ]"
                >
                  Reset
                </button>
              </div>
            </div>

            <!-- Form Header -->
            <div class="text-center mb-8">
              <h3 :class="['text-3xl font-bold mb-3', themeStore.isDarkMode ? 'text-white' : 'text-gray-900']">
                {{ getFormTitle() }}
              </h3>
              <p :class="['text-sm leading-relaxed', themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600']">
                {{ getFormSubtitle() }}
              </p>
            </div>

            <!-- Error Display -->
            <div v-if="error" :class="['mb-6 px-4 py-3 rounded-xl text-sm border', themeStore.colors.status.error.bg, themeStore.colors.status.error.text, themeStore.colors.status.error.border]">
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                {{ error }}
              </div>
            </div>

            <!-- Success Display -->
            <div v-if="success" :class="['mb-6 px-4 py-3 rounded-xl text-sm border', themeStore.colors.status.success.bg, themeStore.colors.status.success.text, themeStore.colors.status.success.border]">
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                {{ success }}
              </div>
            </div>

            <!-- Forms -->
            <form @submit.prevent="handleSubmit" class="space-y-6">
              
              <!-- Email Field -->
              <div>
                <label for="email" :class="['block text-sm font-semibold mb-3', themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-700']">
                  <div class="flex items-center space-x-2">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                      <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                    </svg>
                    <span>Email Address</span>
                  </div>
                </label>
                <div class="relative">
                  <input
                    id="email"
                    v-model="form.email"
                    type="email"
                    required
                    :class="[
                      'w-full px-5 py-4 rounded-xl transition-all duration-300 text-sm font-medium',
                      'focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none',
                      'transform focus:scale-[1.02] hover:scale-[1.01]',
                      themeStore.isDarkMode ? 
                        'bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:bg-gray-600' :
                        'bg-gray-50 border border-gray-200 text-gray-900 placeholder-gray-500 focus:bg-white',
                      emailError ? 'border-red-500 ring-red-500' : ''
                    ]"
                    placeholder="Enter your email address"
                    @blur="validateEmail"
                  />
                  <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                    <svg v-if="emailError" class="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                    </svg>
                  </div>
                </div>
                <p v-if="emailError" class="mt-1 text-sm text-red-600">{{ emailError }}</p>
              </div>

              <!-- Password Field -->
              <div v-if="currentMode !== 'reset'">
                <label for="password" :class="['block text-sm font-semibold mb-3', themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-700']">
                  <div class="flex items-center space-x-2">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/>
                    </svg>
                    <span>Password</span>
                  </div>
                </label>
                <div class="relative">
                  <input
                    id="password"
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    :class="[
                      'w-full px-5 py-4 pr-12 rounded-xl transition-all duration-300 text-sm font-medium',
                      'focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none',
                      'transform focus:scale-[1.02] hover:scale-[1.01]',
                      themeStore.isDarkMode ? 
                        'bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:bg-gray-600' :
                        'bg-gray-50 border border-gray-200 text-gray-900 placeholder-gray-500 focus:bg-white',
                      passwordError ? 'border-red-500 ring-red-500' : ''
                    ]"
                    placeholder="Enter your password"
                    @blur="validatePassword"
                  />
                  <button
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute inset-y-0 right-0 flex items-center pr-3"
                  >
                    <svg v-if="showPassword" class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd"/>
                      <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z"/>
                    </svg>
                    <svg v-else class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                      <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
                    </svg>
                  </button>
                </div>
                <p v-if="passwordError" class="mt-1 text-sm text-red-600">{{ passwordError }}</p>
                
                <!-- Password Strength Indicator -->
                <div v-if="currentMode === 'signup' && form.password" class="mt-2">
                  <div class="flex space-x-1">
                    <div v-for="i in 4" :key="i" :class="[
                      'h-1 flex-1 rounded-full transition-colors duration-200',
                      passwordStrength >= i ? getStrengthColor(passwordStrength) : 'bg-gray-200'
                    ]"></div>
                  </div>
                  <p class="mt-1 text-xs text-gray-600">{{ getStrengthText(passwordStrength) }}</p>
                </div>
              </div>

              <!-- Confirm Password Field -->
              <div v-if="currentMode === 'signup'">
                <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
                  Confirm Password
                </label>
                <div class="relative">
                  <input
                    id="confirmPassword"
                    v-model="form.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    required
                    :class="[
                      'w-full px-4 py-3 border rounded-xl transition-all duration-200 bg-gray-50 focus:bg-white pr-10',
                      'focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                      confirmPasswordError ? 'border-red-300' : 'border-gray-300'
                    ]"
                    placeholder="Confirm your password"
                    @blur="validateConfirmPassword"
                  />
                  <button
                    type="button"
                    @click="showConfirmPassword = !showConfirmPassword"
                    class="absolute inset-y-0 right-0 flex items-center pr-3"
                  >
                    <svg v-if="showConfirmPassword" class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd"/>
                      <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z"/>
                    </svg>
                    <svg v-else class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                      <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
                    </svg>
                  </button>
                </div>
                <p v-if="confirmPasswordError" class="mt-1 text-sm text-red-600">{{ confirmPasswordError }}</p>
              </div>

              <!-- Remember Me -->
              <div v-if="currentMode === 'signin'" class="flex items-center justify-between">
                <label class="flex items-center">
                  <input
                    v-model="form.rememberMe"
                    type="checkbox"
                    class="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">Remember me</span>
                </label>
                <button
                  type="button"
                  @click="setMode('reset')"
                  class="text-sm text-indigo-600 hover:text-indigo-500"
                >
                  Forgot password?
                </button>
              </div>

              <!-- Submit Button -->
              <button
                type="submit"
                :disabled="loading || !isFormValid"
                :class="[
                  'w-full py-4 px-6 rounded-xl font-semibold text-white transition-all duration-300 transform',
                  'focus:outline-none focus:ring-4 focus:ring-blue-500/50 focus:ring-offset-2',
                  (loading || !isFormValid)
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 hover:scale-105 hover:-translate-y-1'
                ]"
                style="box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);"
              >
                <div class="flex items-center justify-center">
                  <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ getSubmitText() }}
                </div>
              </button>

              <!-- Divider -->
              <div v-if="currentMode !== 'reset'" class="relative my-8">
                <div class="absolute inset-0 flex items-center">
                  <div :class="['w-full border-t', themeStore.isDarkMode ? 'border-gray-600' : 'border-gray-300']"></div>
                </div>
                <div class="relative flex justify-center text-sm">
                  <span :class="['px-6 font-medium', themeStore.isDarkMode ? 'bg-gray-800 text-gray-400' : 'bg-white text-gray-500']">or continue with</span>
                </div>
              </div>

              <!-- Google Sign In -->
              <button
                v-if="currentMode !== 'reset'"
                type="button"
                @click="handleGoogleLogin"
                :disabled="loading"
                :class="[
                  'w-full flex items-center justify-center py-4 px-6 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105',
                  'focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2',
                  'disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none',
                  themeStore.isDarkMode ? 
                    'border border-gray-600 bg-gray-700 text-white hover:bg-gray-600' :
                    'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                ]"
                style="box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);"
              >
                <svg class="w-5 h-5 mr-3" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Continue with Google
              </button>
            </form>

            <!-- Footer Links -->
            <div v-if="currentMode === 'reset'" class="mt-6 text-center">
              <button
                @click="setMode('signin')"
                class="text-sm text-indigo-600 hover:text-indigo-500"
              >
                ← Back to Sign In
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { sendPasswordResetEmail } from 'firebase/auth'
import { auth } from '@/services/firebase'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

// State
const currentMode = ref('signin') // 'signin', 'signup', 'reset'
const loading = ref(false)
const error = ref('')
const success = ref('')

// Form state
const form = reactive({
  email: '',
  password: '',
  confirmPassword: '',
  rememberMe: false
})

// Validation state
const emailError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')

// UI state
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// Password strength
const passwordStrength = computed(() => {
  if (!form.password) return 0
  
  let strength = 0
  if (form.password.length >= 8) strength++
  if (/[A-Z]/.test(form.password)) strength++
  if (/[0-9]/.test(form.password)) strength++
  if (/[^A-Za-z0-9]/.test(form.password)) strength++
  
  return strength
})

// Form validation
const isFormValid = computed(() => {
  if (!form.email || emailError.value) return false
  
  if (currentMode.value !== 'reset') {
    if (!form.password || passwordError.value) return false
    
    if (currentMode.value === 'signup') {
      if (!form.confirmPassword || confirmPasswordError.value) return false
      if (passwordStrength.value < 2) return false
    }
  }
  
  return true
})

// Watch for mode changes to clear errors
watch(currentMode, () => {
  clearErrors()
  clearForm()
})

// Methods
const setMode = (mode) => {
  currentMode.value = mode
}

const clearErrors = () => {
  error.value = ''
  success.value = ''
  emailError.value = ''
  passwordError.value = ''
  confirmPasswordError.value = ''
}

const clearForm = () => {
  form.email = ''
  form.password = ''
  form.confirmPassword = ''
  form.rememberMe = false
}

// Validation methods
const validateEmail = () => {
  emailError.value = ''
  
  if (!form.email) {
    emailError.value = 'Email is required'
    return false
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.email)) {
    emailError.value = 'Please enter a valid email address'
    return false
  }
  
  return true
}

const validatePassword = () => {
  passwordError.value = ''
  
  if (!form.password) {
    passwordError.value = 'Password is required'
    return false
  }
  
  if (currentMode.value === 'signup') {
    if (form.password.length < 8) {
      passwordError.value = 'Password must be at least 8 characters long'
      return false
    }
    
    if (passwordStrength.value < 2) {
      passwordError.value = 'Password is too weak. Include uppercase, numbers, or symbols.'
      return false
    }
  }
  
  return true
}

const validateConfirmPassword = () => {
  confirmPasswordError.value = ''
  
  if (!form.confirmPassword) {
    confirmPasswordError.value = 'Please confirm your password'
    return false
  }
  
  if (form.password !== form.confirmPassword) {
    confirmPasswordError.value = 'Passwords do not match'
    return false
  }
  
  return true
}

// Helper methods
const getFormTitle = () => {
  switch (currentMode.value) {
    case 'signin': return 'Welcome Back'
    case 'signup': return 'Create Account'
    case 'reset': return 'Reset Password'
    default: return 'Welcome'
  }
}

const getFormSubtitle = () => {
  switch (currentMode.value) {
    case 'signin': return 'Sign in to your account to continue'
    case 'signup': return 'Create a new account to get started'
    case 'reset': return 'Enter your email to receive a reset link'
    default: return ''
  }
}

const getSubmitText = () => {
  if (loading.value) {
    switch (currentMode.value) {
      case 'signin': return 'Signing in...'
      case 'signup': return 'Creating account...'
      case 'reset': return 'Sending email...'
    }
  }
  
  switch (currentMode.value) {
    case 'signin': return 'Sign In'
    case 'signup': return 'Create Account'
    case 'reset': return 'Send Reset Email'
    default: return 'Submit'
  }
}

const getStrengthColor = (strength) => {
  switch (strength) {
    case 1: return 'bg-red-400'
    case 2: return 'bg-orange-400'
    case 3: return 'bg-yellow-400'
    case 4: return 'bg-green-400'
    default: return 'bg-gray-200'
  }
}

const getStrengthText = (strength) => {
  switch (strength) {
    case 1: return 'Weak password'
    case 2: return 'Fair password'
    case 3: return 'Good password'
    case 4: return 'Strong password'
    default: return 'Enter a password'
  }
}

// Error handling
const handleAuthError = (error) => {
  console.error('Auth error:', error)
  
  // Firebase error codes
  switch (error.code) {
    case 'auth/user-not-found':
      return 'No account found with this email address'
    case 'auth/wrong-password':
      return 'Incorrect password. Please try again.'
    case 'auth/email-already-in-use':
      return 'An account with this email already exists'
    case 'auth/weak-password':
      return 'Password is too weak. Please choose a stronger password.'
    case 'auth/invalid-email':
      return 'Please enter a valid email address'
    case 'auth/too-many-requests':
      return 'Too many failed attempts. Please try again later.'
    case 'auth/network-request-failed':
      return 'Network error. Please check your connection.'
    default:
      return error.message || 'An unexpected error occurred. Please try again.'
  }
}

// Submit handlers
const handleSubmit = async () => {
  clearErrors()
  
  // Validate form
  if (currentMode.value === 'reset') {
    if (!validateEmail()) return
  } else {
    if (!validateEmail() || !validatePassword()) return
    if (currentMode.value === 'signup' && !validateConfirmPassword()) return
  }
  
  loading.value = true
  
  try {
    switch (currentMode.value) {
      case 'signin':
        await authStore.loginWithEmailPassword(form.email, form.password)
        router.push('/')
        break
        
      case 'signup':
        await authStore.signupWithEmailPassword(form.email, form.password)
        router.push('/')
        break
        
      case 'reset':
        await sendPasswordResetEmail(auth, form.email)
        success.value = 'Password reset email sent! Check your inbox.'
        setTimeout(() => setMode('signin'), 3000)
        break
    }
  } catch (err) {
    error.value = handleAuthError(err)
  } finally {
    loading.value = false
  }
}

const handleGoogleLogin = async () => {
  clearErrors()
  loading.value = true
  
  try {
    await authStore.loginWithGoogle()
    router.push('/')
  } catch (err) {
    error.value = handleAuthError(err)
  } finally {
    loading.value = false
  }
}
</script>