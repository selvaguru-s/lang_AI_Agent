<template>
  <div :class="['min-h-screen transition-all duration-300', themeStore.isDarkMode ? 'bg-gray-900' : 'bg-white']">
    <!-- Enhanced Navigation -->
    <nav :class="['backdrop-blur-md shadow-lg sticky top-0 z-50 transition-all duration-300', themeStore.colors.bg.overlay, themeStore.colors.border.primary, 'border-b']">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <div class="flex-shrink-0 flex items-center space-x-3">
              <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
                </svg>
              </div>
              <div>
                <h1 :class="['text-xl font-bold', themeStore.colors.text.primary]">
                  AI Linux Agent
                </h1>
                <p :class="['text-xs', themeStore.colors.text.secondary]">Remote Command Center</p>
              </div>
            </div>
            <div class="hidden md:ml-8 md:flex md:items-center md:space-x-1">
              <router-link 
                to="/" 
                :class="['px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 shadow-sm', themeStore.colors.status.info.bg, themeStore.colors.status.info.text]"
              >
                <div class="flex items-center space-x-2">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10.707 2.293a1 1 0 00-1.414 0l-9 9a1 1 0 001.414 1.414L2 12.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-4.586l.293.293a1 1 0 001.414-1.414l-9-9z"/>
                  </svg>
                  <span>Dashboard</span>
                </div>
              </router-link>
              <router-link 
                to="/clients" 
                :class="['px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200', themeStore.colors.text.secondary, 'hover:' + themeStore.colors.bg.tertiary, 'hover:' + themeStore.colors.text.primary]"
              >
                <div class="flex items-center space-x-2">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 01-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4zm9 1a1 1 0 010-2h4a1 1 0 011 1v4a1 1 0 01-2 0V6.414l-2.293 2.293a1 1 0 11-1.414-1.414L13.586 5H12zm-9 7a1 1 0 012 0v1.586l2.293-2.293a1 1 0 111.414 1.414L6.414 15H8a1 1 0 010 2H4a1 1 0 01-1-1v-4zm13-1a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 010-2h1.586l-2.293-2.293a1 1 0 111.414-1.414L15.586 13H14a1 1 0 01-1-1z" clip-rule="evenodd"/>
                  </svg>
                  <span>Clients</span>
                </div>
              </router-link>
              <router-link 
                to="/tasks" 
                :class="['px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200', themeStore.colors.text.secondary, 'hover:' + themeStore.colors.bg.tertiary, 'hover:' + themeStore.colors.text.primary]"
              >
                <div class="flex items-center space-x-2">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
                  </svg>
                  <span>Tasks</span>
                </div>
              </router-link>
              
              <!-- Stats in Navigation Bar -->
              <div :class="['flex items-center space-x-4 ml-6 pl-6 border-l', themeStore.colors.border.secondary]">
                <!-- Connected Clients -->
                <div class="flex items-center space-x-2">
                  <div :class="['w-2 h-2 rounded-full', getOnlineClientCount() > 0 ? 'bg-success-500' : 'bg-error-500']"></div>
                  <span :class="['text-sm font-medium', themeStore.colors.text.primary]">{{ getOnlineClientCount() }}</span>
                  <span :class="['text-xs', themeStore.colors.text.tertiary]">clients</span>
                </div>
                
                <!-- Total Tasks -->
                <div class="flex items-center space-x-2">
                  <svg class="w-3 h-3 text-info-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
                  </svg>
                  <span :class="['text-sm font-medium', themeStore.colors.text.primary]">{{ recentTasks?.length || 0 }}</span>
                  <span :class="['text-xs', themeStore.colors.text.tertiary]">tasks</span>
                </div>
              </div>
            </div>
          </div>
          <!-- Theme Toggle and User Menu -->
          <div class="flex items-center space-x-3">
            <ThemeToggle />
            <div class="relative">
              <button
              @click="toggleUserMenu"
              class="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
              ref="userMenuButton"
            >
              <div class="hidden sm:block text-right">
                <div :class="['text-sm font-medium', themeStore.colors.text.primary]">
                  {{ authStore.userInfo.email }}
                </div>
                <div :class="['text-xs', themeStore.colors.text.secondary]">View profile</div>
              </div>
              <div class="w-10 h-10 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center shadow-lg">
                <span class="text-white text-sm font-semibold">
                  {{ authStore.userInfo.email?.charAt(0).toUpperCase() }}
                </span>
              </div>
              <svg class="w-4 h-4 text-gray-500 transition-transform duration-200" :class="userMenuOpen ? 'rotate-180' : ''" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
              </svg>
            </button>

            <!-- Dropdown Menu -->
            <div 
              v-show="userMenuOpen"
              ref="userMenuDropdown"
              class="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-200 py-2 z-50 animate-in slide-in-from-top-2 duration-200"
            >
              <!-- User Info Header -->
              <div class="px-4 py-3 border-b border-gray-100">
                <div class="flex items-center space-x-3">
                  <div class="w-12 h-12 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                    <span class="text-white font-semibold">
                      {{ authStore.userInfo.email?.charAt(0).toUpperCase() }}
                    </span>
                  </div>
                  <div>
                    <div class="font-medium text-gray-900">{{ authStore.userInfo.displayName || 'User' }}</div>
                    <div class="text-sm text-gray-500">{{ authStore.userInfo.email }}</div>
                  </div>
                </div>
              </div>

              <!-- API Key Section -->
              <div class="px-4 py-3 border-b border-gray-100">
                <div class="space-y-3">
                  <div class="flex items-center justify-between">
                    <label class="text-sm font-medium text-gray-700">🔑 API Key</label>
                    <button 
                      @click="refreshApiKey"
                      :disabled="isRefreshingApiKey"
                      class="text-xs text-blue-600 hover:text-blue-700 font-medium disabled:opacity-50"
                    >
                      {{ isRefreshingApiKey ? 'Refreshing...' : 'Refresh' }}
                    </button>
                  </div>
                  
                  <div class="flex items-center space-x-2 bg-gray-50 rounded-lg p-3">
                    <code class="flex-1 text-xs font-mono text-gray-800 break-all">
                      {{ showFullApiKey ? (currentApiKey || 'Loading...') : maskedApiKey }}
                    </code>
                    
                    <div class="flex items-center space-x-1">
                      <!-- Toggle Visibility -->
                      <button 
                        @click="toggleApiKeyVisibility"
                        class="p-1.5 text-gray-500 hover:text-gray-700 rounded hover:bg-gray-200 transition-all duration-200"
                        :title="showFullApiKey ? 'Hide API key' : 'Show API key'"
                      >
                        <svg v-if="showFullApiKey" class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd"/>
                          <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z"/>
                        </svg>
                        <svg v-else class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                          <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
                        </svg>
                      </button>
                      
                      <!-- Copy Button -->
                      <button 
                        @click="copyApiKey"
                        class="p-1.5 text-gray-500 hover:text-gray-700 rounded hover:bg-gray-200 transition-all duration-200"
                        title="Copy API key"
                      >
                        <svg v-if="apiKeyCopied" class="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        <svg v-else class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z"/>
                          <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z"/>
                        </svg>
                      </button>
                    </div>
                  </div>

                  <p class="text-xs text-gray-500">
                    Use this key for API authentication
                  </p>
                </div>
              </div>

              <!-- Menu Items -->
              <div class="py-1">
                <button 
                  @click="viewApiDocs"
                  class="w-full flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors duration-200"
                >
                  <svg class="w-4 h-4 mr-3 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd"/>
                  </svg>
                  API Documentation
                </button>
                
                <button 
                  @click="copyApiExample"
                  class="w-full flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors duration-200"
                >
                  <svg class="w-4 h-4 mr-3 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z"/>
                    <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z"/>
                  </svg>
                  Copy cURL Example
                </button>

                <div class="border-t border-gray-100 my-1"></div>
                
                <button
                  @click="handleLogout"
                  class="w-full flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors duration-200"
                >
                  <svg class="w-4 h-4 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Sign Out
                </button>
              </div>
            </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <div class="relative overflow-hidden">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">

        <!-- Main Content Area -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          
          <!-- Command Execution Panel - Left 2/3 -->
          <div class="lg:col-span-2">
            <div :class="['rounded-xl', themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white']" style="box-shadow: 0 -4px 16px -4px rgba(0, 0, 0, 0.1), 0 4px 16px -4px rgba(0, 0, 0, 0.1), -4px 0 16px -4px rgba(0, 0, 0, 0.1), 4px 0 16px -4px rgba(0, 0, 0, 0.1);">
              <!-- Header -->
              <div class="px-6 py-5 pb-4">
                <div class="flex items-center justify-between">
                  <div>
                    <h2 :class="['text-xl font-semibold', themeStore.isDarkMode ? 'text-white' : 'text-gray-900']">Command Center</h2>
                    <p :class="['text-sm mt-1', themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600']">Execute commands with AI assistance</p>
                  </div>
                  
                  <!-- Status Indicator -->
                  <div class="flex items-center space-x-3">
                    <div v-if="connectedClient" class="flex items-center space-x-2">
                      <div class="flex h-2 w-2">
                        <div class="animate-ping absolute h-2 w-2 rounded-full bg-green-400 opacity-75"></div>
                        <div class="relative h-2 w-2 rounded-full bg-green-500"></div>
                      </div>
                      <span :class="['text-sm font-medium', themeStore.isDarkMode ? 'text-white' : 'text-gray-900']">{{ connectedClient.hostname }}</span>
                    </div>
                    <div v-else class="flex items-center space-x-2">
                      <div class="h-2 w-2 rounded-full bg-red-500"></div>
                      <span :class="['text-sm', themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600']">Disconnected</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Command Form -->
              <div class="p-6">
                <form @submit.prevent="executeCommand" class="space-y-6">
                  
                  <div>
                    <label for="command" :class="['block text-sm font-medium mb-3', themeStore.isDarkMode ? 'text-white' : 'text-gray-900']">
                      Command or Description
                    </label>
                    <div class="relative">
                      <textarea
                        id="command"
                        v-model="commandInput"
                        rows="4"
                        :class="[
                          'block w-full rounded-lg border-0 py-3 px-4 shadow-sm ring-1 ring-inset focus:ring-2 focus:ring-inset',
                          'text-sm font-mono transition-all duration-200 resize-none',
                          themeStore.isDarkMode ? 'bg-gray-700 text-white ring-gray-600 focus:ring-blue-500 placeholder-gray-400' : 'bg-white text-gray-900 ring-gray-300 focus:ring-blue-600 placeholder-gray-500'
                        ]"
                        placeholder="Enter a command or describe what you want to do..."
                        required
                      ></textarea>
                      <div class="absolute inset-y-0 right-0 flex items-end pb-3 pr-3">
                        <svg class="h-4 w-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm3.293 1.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L7.586 10 5.293 7.707a1 1 0 010-1.414zM11 12a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/>
                        </svg>
                      </div>
                    </div>
                    <p :class="['mt-2 text-xs', themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600']">Use natural language or specific commands</p>
                  </div>
                  
                  <button
                    type="submit"
                    :disabled="isButtonDisabled"
                    :class="[
                      'w-full inline-flex justify-center items-center px-4 py-2.5 text-sm font-medium text-white',
                      'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
                      'rounded-lg shadow-sm transition-all duration-200',
                      'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-600'
                    ]"
                  >
                    <svg v-if="isExecuting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <svg v-else class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/>
                    </svg>
                    {{ isExecuting ? 'Executing...' : 'Execute' }}
                  </button>
                </form>
              </div>
            </div>
          </div>

          <!-- Live Terminal - Right 1/3 -->
          <div class="lg:col-span-1">
            <div :class="['rounded-xl', themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white']" style="box-shadow: 0 -4px 16px -4px rgba(0, 0, 0, 0.1), 0 4px 16px -4px rgba(0, 0, 0, 0.1), -4px 0 16px -4px rgba(0, 0, 0, 0.1), 4px 0 16px -4px rgba(0, 0, 0, 0.1);">
              <!-- Header -->
              <div class="px-4 py-3 pb-2 flex items-center justify-between">
                <div class="flex items-center space-x-2">
                  <div :class="['w-3 h-3 rounded-full', isConnected ? 'bg-green-500' : 'bg-red-500']"></div>
                  <h3 :class="['text-sm font-medium', themeStore.isDarkMode ? 'text-white' : 'text-gray-900']">Terminal</h3>
                </div>
                <span :class="['text-xs', themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600']">{{ wsConnectionStatus }}</span>
              </div>

              <!-- Terminal Body -->
              <div :class="['p-4 h-80 overflow-y-auto font-mono text-xs rounded-b-xl', themeStore.isDarkMode ? 'bg-black text-green-400' : 'bg-gray-900 text-green-400']">
                <div v-if="terminalOutput && terminalOutput.length > 0" class="space-y-1">
                  <div v-for="(line, index) in terminalOutput" :key="index" class="flex">
                    <span class="text-gray-500 text-xs mr-2 flex-shrink-0 w-12">{{ line.timestamp }}</span>
                    <span :class="getTerminalLineClass(line.type)" class="flex-1 break-all">{{ line.content }}</span>
                  </div>
                </div>
                <div v-else class="flex items-center justify-center h-full text-gray-400">
                  <div class="text-center">
                    <div class="text-2xl mb-2">$</div>
                    <p class="text-xs">Waiting for output...</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Tasks - Full Width -->
        <div class="mt-8">
          <div :class="['rounded-xl', themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white']" style="box-shadow: 0 -6px 20px -6px rgba(0, 0, 0, 0.15), 0 6px 20px -6px rgba(0, 0, 0, 0.15), -6px 0 20px -6px rgba(0, 0, 0, 0.15), 6px 0 20px -6px rgba(0, 0, 0, 0.15);">
            <!-- Header -->
            <div class="px-6 py-4 pb-3">
              <div class="flex items-center justify-between">
                <div>
                  <h2 :class="['text-lg font-semibold', themeStore.isDarkMode ? 'text-white' : 'text-gray-900']">Recent Tasks</h2>
                  <p :class="['text-sm mt-1', themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600']">{{ recentTasks?.length || 0 }} commands executed</p>
                </div>
                <router-link 
                  to="/tasks" 
                  class="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-700"
                >
                  View all
                  <svg class="ml-1 w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
                  </svg>
                </router-link>
              </div>
            </div>

            <!-- Tasks List -->
            <div class="space-y-2 p-3">
              <div v-if="!recentTasks || recentTasks.length === 0" class="p-8 text-center">
                <div class="w-12 h-12 mx-auto mb-4 text-gray-300">
                  <svg fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm0 2v8h12V6H4z" clip-rule="evenodd"/>
                  </svg>
                </div>
                <p :class="['text-sm font-medium', themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600']">No tasks yet</p>
                <p :class="['text-xs mt-1', themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500']">Execute your first command to get started</p>
              </div>
              
              <div v-else>
                <div
                  v-for="(task, index) in recentTasks.slice(0, 8)"
                  :key="task.task_id"
                  @mouseenter="(e) => e.target.style.boxShadow = '0 -2px 8px -2px rgba(0, 0, 0, 0.15), 0 2px 8px -2px rgba(0, 0, 0, 0.15), -2px 0 8px -2px rgba(0, 0, 0, 0.15), 2px 0 8px -2px rgba(0, 0, 0, 0.15)'"
                  @mouseleave="(e) => e.target.style.boxShadow = 'none'"
                  :class="['p-4 rounded-lg cursor-pointer transition-all duration-200 group', themeStore.isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50']"
                  @click="$router.push(`/tasks/${task.task_id}`)"
                >
                  <div class="flex items-center space-x-4">
                    <!-- Status Indicator -->
                    <div class="flex-shrink-0">
                      <div :class="[
                        'w-2 h-2 rounded-full',
                        task.status === 'completed' ? 'bg-green-500' :
                        task.status === 'running' ? 'bg-blue-500 animate-pulse' :
                        task.status === 'failed' ? 'bg-red-500' : 'bg-gray-400'
                      ]" style="box-shadow: 0 0 4px rgba(0, 0, 0, 0.3);"></div>
                    </div>

                    <!-- Task Content -->
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center justify-between">
                        <p :class="['text-sm font-medium line-clamp-1', themeStore.isDarkMode ? 'text-white group-hover:text-blue-400' : 'text-gray-900 group-hover:text-blue-600']">
                          {{ task.original_prompt }}
                        </p>
                        <div class="flex items-center space-x-3">
                          <span class="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full" :class="[
                            task.status === 'completed' ? (themeStore.isDarkMode ? 'bg-green-900 text-green-300' : 'bg-green-100 text-green-800') :
                            task.status === 'running' ? (themeStore.isDarkMode ? 'bg-blue-900 text-blue-300' : 'bg-blue-100 text-blue-800') :
                            task.status === 'failed' ? (themeStore.isDarkMode ? 'bg-red-900 text-red-300' : 'bg-red-100 text-red-800') : 
                            (themeStore.isDarkMode ? 'bg-gray-800 text-gray-300' : 'bg-gray-100 text-gray-800')
                          ]" style="box-shadow: 0 0 6px rgba(0, 0, 0, 0.2);">
                            {{ task.status === 'completed' ? 'Done' :
                               task.status === 'running' ? 'Running' :
                               task.status === 'failed' ? 'Failed' : 'Pending' }}
                          </span>
                        </div>
                      </div>
                      <div class="flex items-center mt-1 space-x-2">
                        <span :class="['text-xs', themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500']">{{ getRelativeTime(task.created_at) }}</span>
                      </div>
                    </div>

                    <!-- Arrow -->
                    <div :class="['flex-shrink-0 transition-colors', themeStore.isDarkMode ? 'text-gray-400 group-hover:text-gray-300' : 'text-gray-400 group-hover:text-gray-600']">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useWebSocket } from '@/services/websocket'
import { tasksAPI, clientsAPI, authAPI } from '@/services/api'
import { format } from 'date-fns'
import ThemeToggle from '@/components/ThemeToggle.vue'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const router = useRouter()
const { isConnected, on, off } = useWebSocket()

// State
const selectedMachine = ref('')
const commandInput = ref('')
const isExecuting = ref(false)
const clients = ref([])
const recentTasks = ref([])
const terminalOutput = ref([])

// Auto-select first available client
const connectedClient = computed(() => {
  const activeClient = clients.value.find(client => client.is_active)
  if (activeClient && !selectedMachine.value) {
    selectedMachine.value = activeClient.machine_id
  }
  return activeClient
})

// API Key state
const currentApiKey = ref('')
const showFullApiKey = ref(false)
const isRefreshingApiKey = ref(false)
const apiKeyCopied = ref(false)

// User menu state
const userMenuOpen = ref(false)
const userMenuButton = ref(null)
const userMenuDropdown = ref(null)

// Computed
const wsConnectionStatus = computed(() => isConnected.value ? 'Connected' : 'Disconnected')
const wsConnectionClass = computed(() => isConnected.value ? themeStore.gradients.success : themeStore.gradients.error)
const isButtonDisabled = computed(() => {
  return !connectedClient.value || !commandInput.value?.trim() || isExecuting.value
})

// API Key computed
const maskedApiKey = computed(() => {
  if (!currentApiKey.value) return '••••••••••••••••••••••••••••••••'
  return currentApiKey.value.substring(0, 8) + '••••••••••••••••••••••••' + currentApiKey.value.slice(-4)
})

// Methods
const executeCommand = async () => {
  if (!connectedClient.value || !commandInput.value.trim()) {
    return
  }
  
  try {
    isExecuting.value = true
    
    const response = await tasksAPI.create(commandInput.value, connectedClient.value.machine_id)
    
    addTerminalLine(`Command submitted: ${commandInput.value}`, 'info')
    addTerminalLine(`Task ID: ${response.data.task_id}`, 'info')
    addTerminalLine(`🔄 Redirecting to task details...`, 'info')
    
    commandInput.value = ''
    
    // Auto-redirect to task details page
    setTimeout(() => {
      router.push(`/tasks/${response.data.task_id}`)
    }, 1000) // Small delay to show the success message
    
  } catch (error) {
    console.error('executeCommand: error', error)
    addTerminalLine(`Error: ${error.response?.data?.detail || error.message}`, 'error')
  } finally {
    isExecuting.value = false
  }
}

const loadClients = async () => {
  try {
    const response = await clientsAPI.list()
    clients.value = response.data || []
  } catch (error) {
    console.error('Failed to load clients:', error)
    clients.value = []
  }
}

const loadRecentTasks = async () => {
  try {
    const response = await tasksAPI.list(10, 0)
    recentTasks.value = response.data || []
  } catch (error) {
    console.error('Failed to load recent tasks:', error)
    recentTasks.value = []
  }
}

const addTerminalLine = (content, type = 'info') => {
  terminalOutput.value.push({
    timestamp: format(new Date(), 'HH:mm:ss'),
    content,
    type
  })
  
  // Keep only last 100 lines
  if (terminalOutput.value.length > 100) {
    terminalOutput.value = terminalOutput.value.slice(-100)
  }
}

const getTaskStatusClass = (status) => {
  switch (status) {
    case 'completed': return 'status-online'
    case 'running': return 'status-running'
    case 'failed': return 'status-offline'
    default: return 'status-pending'
  }
}

const formatDate = (dateString) => {
  return format(new Date(dateString), 'MMM d, yyyy HH:mm')
}

const getTerminalLineClass = (type) => {
  switch (type) {
    case 'error': return 'text-error-400'
    case 'success': return 'text-success-400' 
    case 'info': return 'text-info-400'
    default: return 'text-success-400'
  }
}

// New dashboard helper functions
const getOnlineClientCount = () => {
  return clients.value?.filter(client => client.is_active)?.length || 0
}


const getModernTaskStatusClass = (status) => {
  switch (status) {
    case 'completed': return 'bg-gradient-to-br from-green-400 to-green-600'
    case 'running': return 'bg-gradient-to-br from-blue-400 to-blue-600 animate-pulse'
    case 'failed': return 'bg-gradient-to-br from-red-400 to-red-600'
    default: return 'bg-gradient-to-br from-gray-400 to-gray-600'
  }
}

const getTaskStatusBadgeClass = (status) => {
  switch (status) {
    case 'completed': return `${themeStore.colors.status.success.bg} ${themeStore.colors.status.success.text}`
    case 'running': return `${themeStore.colors.status.running.bg} ${themeStore.colors.status.running.text}`
    case 'failed': return `${themeStore.colors.status.error.bg} ${themeStore.colors.status.error.text}`
    default: return `${themeStore.colors.bg.tertiary} ${themeStore.colors.text.secondary}`
  }
}

const getTaskStatusIcon = (status) => {
  switch (status) {
    case 'completed': return '✅'
    case 'running': return '⚡'
    case 'failed': return '❌'
    default: return '⏳'
  }
}

const getRelativeTime = (dateString) => {
  if (!dateString) return 'Unknown'
  const now = new Date()
  const date = new Date(dateString)
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return format(date, 'MMM d')
}

// API Key methods
const loadCurrentApiKey = async () => {
  try {
    // Get from auth store first (faster)
    if (authStore.apiKey) {
      currentApiKey.value = authStore.apiKey
      return
    }
    
    // If not in store, fetch from API
    const response = await authAPI.getMe()
    currentApiKey.value = response.data.api_key
  } catch (error) {
    console.error('Failed to load API key:', error)
    currentApiKey.value = authStore.apiKey || ''
  }
}

const toggleApiKeyVisibility = () => {
  showFullApiKey.value = !showFullApiKey.value
}

const copyApiKey = async () => {
  if (!currentApiKey.value) return
  
  try {
    await navigator.clipboard.writeText(currentApiKey.value)
    apiKeyCopied.value = true
    setTimeout(() => {
      apiKeyCopied.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy API key:', error)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = currentApiKey.value
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    apiKeyCopied.value = true
    setTimeout(() => {
      apiKeyCopied.value = false
    }, 2000)
  }
}

const refreshApiKey = async () => {
  try {
    isRefreshingApiKey.value = true
    const response = await authAPI.getMe()
    currentApiKey.value = response.data.api_key
    console.log('✅ API key refreshed')
  } catch (error) {
    console.error('Failed to refresh API key:', error)
  } finally {
    isRefreshingApiKey.value = false
  }
}

const getApiBaseUrl = () => {
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
}

const getCurlExample = () => {
  if (!currentApiKey.value) return 'Loading...'
  return `curl -X GET "${getApiBaseUrl()}/tasks/list" \\
  -H "Authorization: Bearer ${currentApiKey.value}" \\
  -H "Content-Type: application/json"`
}

const copyCurlExample = async () => {
  try {
    await navigator.clipboard.writeText(getCurlExample())
    console.log('✅ cURL example copied to clipboard')
  } catch (error) {
    console.error('Failed to copy cURL example:', error)
  }
}

// User menu methods
const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value
}

const closeUserMenu = () => {
  userMenuOpen.value = false
}

const handleLogout = () => {
  closeUserMenu()
  authStore.logout()
}

const viewApiDocs = () => {
  // This would open API documentation - placeholder for now
  console.log('Opening API documentation...')
  closeUserMenu()
}

const copyApiExample = async () => {
  try {
    await navigator.clipboard.writeText(getCurlExample())
    console.log('✅ API example copied to clipboard')
    closeUserMenu()
  } catch (error) {
    console.error('Failed to copy API example:', error)
  }
}

// Click outside to close dropdown
const handleClickOutside = (event) => {
  if (userMenuOpen.value && 
      userMenuButton.value && 
      userMenuDropdown.value &&
      !userMenuButton.value.contains(event.target) && 
      !userMenuDropdown.value.contains(event.target)) {
    closeUserMenu()
  }
}

// WebSocket event handlers
const handleTaskUpdate = (data) => {
  // Show command being executed
  if (data.attempt && data.attempt.command) {
    addTerminalLine(`$ ${data.attempt.command}`, 'info')
  }
  
  // Show command output
  if (data.attempt && data.attempt.output) {
    // Split output into lines for better display
    const outputLines = data.attempt.output.split('\n').filter(line => line.trim())
    outputLines.forEach(line => {
      addTerminalLine(line, data.attempt.exit_code === 0 ? 'success' : 'error')
    })
  }
  
  // Show status updates
  if (data.status) {
    addTerminalLine(`Task ${data.task_id}: ${data.status}`, data.status === 'failed' ? 'error' : 'info')
    
    // Show summary when task completes
    if (data.status === 'completed') {
      addTerminalLine(`✅ Task completed successfully!`, 'success')
      addTerminalLine(`📋 View full details: /tasks/${data.task_id}`, 'info')
    } else if (data.status === 'failed') {
      addTerminalLine(`❌ Task failed: ${data.error_message || 'Unknown error'}`, 'error')
    }
  }
  
  loadRecentTasks()
}

const handleTaskStarted = (data) => {
  addTerminalLine(`🚀 Task ${data.task_id} started on ${data.machine_id}`, 'info')
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadClients(),
    loadRecentTasks(),
    loadCurrentApiKey()
  ])
  
  // Register WebSocket event listeners
  console.log('📝 Dashboard registering WebSocket event listeners')
  on('task_update', handleTaskUpdate)
  on('task_started', handleTaskStarted)
  console.log('✅ Dashboard WebSocket event listeners registered')
  
  // Add click outside listener for user menu
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  // Remove click outside listener
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.terminal {
  background-color: #1a1a1a;
  color: #00ff00;
  font-family: 'Courier New', monospace;
  padding: 1rem;
  border-radius: 0.5rem;
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-online {
  background-color: #10b981;
}

.status-offline {
  background-color: #ef4444;
}

.status-pending {
  background-color: #f59e0b;
}

.status-running {
  background-color: #3b82f6;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff40;
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Additional animations for user dropdown */
.animate-in {
  animation-name: slideIn;
  animation-duration: 200ms;
  animation-fill-mode: forwards;
}

.slide-in-from-top-2 {
  animation-name: slideInFromTop;
  animation-duration: 200ms;
  animation-fill-mode: forwards;
}

@keyframes slideInFromTop {
  from {
    opacity: 0;
    transform: translateY(-8px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>