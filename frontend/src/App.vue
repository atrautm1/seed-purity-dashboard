<template>
  <div class="min-h-screen bg-stone-50 text-stone-800 flex flex-col font-sans">
    <!-- Header -->
    <header class="bg-emerald-800 text-stone-100 shadow-md px-6 py-4 flex items-center justify-between border-b-4 border-amber-600">
      <router-link to="/">
  <div class="flex items-center space-x-3">
    <!-- Icon Container -->
    <span class="text-3xl">🌱</span>
    
    <!-- Vertical Text Wrapper -->
    <div class="flex flex-col leading-tight">
      <h1 class="text-2xl font-black tracking-wider">SAFE</h1>
      <span class="text-xs text-emerald-200 font-medium tracking-wide">Seed Analysis for Field Excellence</span>
    </div>
  </div>
  </router-link>
  <span class="text-xs uppercase bg-emerald-700 px-3 py-1 rounded-full text-emerald-200 font-semibold tracking-wider">Development</span>
</header>

    <div class="flex flex-1">
      <!-- Sidebar Navigation -->
      <AppSidebar v-if="isAuthenticated" />

      <!-- Dynamic Page Content -->
      <main class="flex-1 p-8 w-full max-w-7xl mx-auto">
        <router-view />
      </main>
    </div>
    <AppFooter v-if="isAuthenticated" />
  </div>
</template>

<script setup>
import { ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import AppFooter from './components/AppFooter.vue'
import AppSidebar from './components/AppSidebar.vue'

const route = useRoute()
const isAuthenticated = ref(false)

// Automatically check auth status on route changes so footer doesn't render on the Login screen
watchEffect(() => {
  const token = localStorage.getItem('auth_token')
  isAuthenticated.value = !!token && route.path !== '/login'
})
</script>