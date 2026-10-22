<template>
  <div class="min-h-screen flex items-center justify-center bg-stone-100 px-4">
    <div class="max-w-md w-full bg-white rounded-xl border border-stone-200 p-8 shadow-sm space-y-6">
      <div class="text-center space-y-1">
        <h2 class="text-lg font-bold text-stone-900">Bioinformatics Portal</h2>
        <p class="text-xs text-stone-500">Please sign in to access the pipeline tools.</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-medium text-stone-700 mb-1">Username</label>
          <input 
            type="text" 
            v-model="username" 
            required 
            class="w-full text-xs border border-stone-300 rounded-lg p-2.5 focus:ring-1 focus:ring-amber-500"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-stone-700 mb-1">Password</label>
          <input 
            type="password" 
            v-model="password" 
            required 
            class="w-full text-xs border border-stone-300 rounded-lg p-2.5 focus:ring-1 focus:ring-amber-500"
          />
        </div>

        <div v-if="errorMessage" class="text-xs text-red-600 bg-red-50 border border-red-200 p-2.5 rounded-lg">
          {{ errorMessage }}
        </div>

        <button 
          type="submit" 
          class="w-full bg-amber-600 hover:bg-amber-700 text-white font-medium text-xs py-2.5 rounded-lg transition-colors shadow-xs"
        >
          Sign In
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const errorMessage = ref('')

const handleLogin = async () => {
  errorMessage.value = ''
  try {
    const formData = new URLSearchParams()
    formData.append('username', username.value)
    formData.append('password', password.value)

    const response = await fetch('/api/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })

    if (!response.ok) {
      throw new Error('Invalid username or password')
    }

    const data = await response.json()
    
    // Store token securely in localStorage
    localStorage.setItem('auth_token', data.access_token)
    
    // Force a clean reload to the root dashboard route
    window.location.href = '/'
  } catch (e) {
    errorMessage.value = e.message
  }
}
</script>