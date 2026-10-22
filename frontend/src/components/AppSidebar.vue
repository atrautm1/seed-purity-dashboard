<template>
<aside class="w-64 bg-stone-100 border-r border-stone-200 p-4 space-y-2">
        <p class="text-xs font-semibold text-stone-400 uppercase tracking-wider px-3 mb-4">Analytical Workspaces</p>
        <router-link 
          to="/consensus" 
          class="flex items-center space-x-3 px-3 py-2.5 rounded-lg font-medium transition-all"
          active-class="bg-emerald-100 text-emerald-900 border-l-4 border-emerald-700 shadow-xs"
        >
          <span>🧬</span>
          <span>Consensus Generation</span>
        </router-link>
        
        <router-link 
          to="/analysis" 
          class="flex items-center space-x-3 px-3 py-2.5 rounded-lg font-medium transition-all"
          active-class="bg-emerald-100 text-emerald-900 border-l-4 border-emerald-700 shadow-xs"
        >
          <span>📊</span>
          <span>Purity and Analysis</span>
        </router-link>
      </aside>
</template>