<template>
  <div class="min-h-screen bg-stone-100 flex flex-col justify-between p-6">

    <!-- Main Welcome & Navigation Grid -->
    <div class="max-w-5xl w-full mx-auto my-auto py-12 space-y-8">
      <div class="text-center space-y-2">
        <h2 class="text-2xl font-bold text-stone-900">Welcome to the Bioinformatics Suite</h2>
        <p class="text-xs text-stone-500 max-w-md mx-auto">Select a tool or pipeline below to begin your analysis.</p>
      </div>

      <!-- Two Action Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
        <!-- Consensus Generation Card -->
        <router-link 
          to="/consensus" 
          class="group bg-white border border-stone-200 hover:border-amber-500 rounded-xl p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between space-y-4"
        >
          <div class="space-y-2">
            <div class="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-bold text-base group-hover:bg-amber-600 group-hover:text-white transition-colors">
              CG
            </div>
            <h3 class="text-sm font-bold text-stone-900">Consensus Generation</h3>
            <p class="text-xs text-stone-500 leading-relaxed">
              Run full-stack bioinformatics pipelines, filter metadata with advanced rules, and visualize cluster metrics.
            </p>
          </div>
          <div class="text-xs font-medium text-amber-600 flex items-center space-x-1 group-hover:translate-x-1 transition-transform">
            <span>Launch Tool</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </router-link>

        <!-- Purity Calculation Card -->
        <router-link 
          to="/analysis" 
          class="group bg-white border border-stone-200 hover:border-amber-500 rounded-xl p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between space-y-4"
        >
          <div class="space-y-2">
            <div class="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-bold text-base group-hover:bg-amber-600 group-hover:text-white transition-colors">
              PC
            </div>
            <h3 class="text-sm font-bold text-stone-900">Purity Calculation</h3>
            <p class="text-xs text-stone-500 leading-relaxed">
              Evaluate genetic purity, analyze allele frequency distributions, and check seed supply chain integrity.
            </p>
          </div>
          <div class="text-xs font-medium text-amber-600 flex items-center space-x-1 group-hover:translate-x-1 transition-transform">
            <span>Launch Tool</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
const handleLogout = () => {
  localStorage.removeItem('auth_token')
  window.location.href = '/login'
}
</script>