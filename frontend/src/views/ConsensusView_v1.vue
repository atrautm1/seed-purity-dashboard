<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-2xl font-bold text-stone-900">Consensus Sequence Generator</h2>
      <p class="text-sm text-stone-500 mt-1">Establish baseline genetic profiles for crop varieties from dart sequencing datasets.</p>
    </div>

    <form @submit.prevent="runConsensusPipeline" class="bg-white rounded-xl shadow-xs border border-stone-200 p-6 space-y-6">
  <!-- General Parameters Group -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
    <div>
      <label class="block text-sm font-semibold text-stone-700 mb-1">Crop Name</label>
      <input v-model="form.cropName" type="text" placeholder="e.g. Wheat" class="w-full rounded-lg border-stone-300 shadow-xs focus:border-emerald-500 focus:ring-emerald-500 p-2 border" />
    </div>
    
    <div>
      <label class="block text-sm font-semibold text-stone-700 mb-1">Minimum Cluster Size</label>
      <input v-model.number="form.minClusterSize" type="number" min="0" placeholder="Default: 3" class="w-full rounded-lg border-stone-300 shadow-xs focus:border-emerald-500 focus:ring-emerald-500 p-2 border" />
    </div>
  </div>

  <!-- DArT Files Sub-Section Group -->
  <div class="bg-stone-50 border border-stone-200 rounded-lg p-5 space-y-4">
    <div class="border-b border-stone-200 pb-2">
      <h3 class="text-sm font-bold text-emerald-800 uppercase tracking-wider">DArT Files</h3>
      <p class="text-xs text-stone-500">Upload your raw genetic sequence data.</p>
    </div>

    <div class="grid grid-cols-1 gap-4">
      <!-- Metadata File -->
      <div>
        <label class="block text-xs font-semibold text-stone-600 mb-1">1. Metadata File (.csv)</label>
        <input type="file" @change="handleFileUpload($event, 'metadata')" accept=".csv" class="w-full text-sm block file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 border border-stone-300 rounded-lg p-1 bg-white" />
      </div>

      <!-- Counts File -->
      <div>
        <label class="block text-xs font-semibold text-stone-600 mb-1">2. Counts File (.csv)</label>
        <input type="file" @change="handleFileUpload($event, 'counts')" accept=".csv" class="w-full text-sm block file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 border border-stone-300 rounded-lg p-1 bg-white" />
      </div>

      <!-- Genotype File -->
      <div>
        <label class="block text-xs font-semibold text-stone-600 mb-1">3. Genotype File (.csv)</label>
        <input type="file" @change="handleFileUpload($event, 'genotype')" class="w-full text-sm block file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 border border-stone-300 rounded-lg p-1 bg-white" />
      </div>
    </div>
  </div>

  <!-- Execution Button -->
  <div class="pt-2">
    <button type="submit" :disabled="loading" class="bg-emerald-700 hover:bg-emerald-800 text-white font-medium py-2.5 px-5 rounded-lg shadow-sm transition-colors disabled:opacity-50 flex items-center space-x-2">
      <span>{{ loading ? 'Running Python Core...' : 'Execute Consensus Pipeline' }}</span>
    </button>
  </div>
</form>


    <!-- Simulated Output Payload Box -->
    <!-- <div v-if="output" class="bg-amber-50/60 border border-amber-200 rounded-xl p-5 space-y-3">
      <h3 class="text-sm font-bold text-amber-900 tracking-wide uppercase">Pipeline Execution Result</h3>
      <div class="bg-stone-900 text-stone-200 p-4 rounded-lg font-mono text-xs overflow-x-auto shadow-inner">
        {{ output }}
      </div>
    </div> -->

    <div v-if="output" class="bg-amber-50/60 border border-amber-200 rounded-xl p-5 space-y-5">
      <div class="flex items-center justify-between">
    <div class="flex items-center space-x-3">
      <h3 class="text-sm font-bold text-amber-900 tracking-wide uppercase">Pipeline Execution Result</h3>
      
      <!-- Dynamic Status Pill -->
      <span 
  :class="output.status === 'success' 
    ? 'bg-green-100 text-green-800 border-green-300' 
    : (output.status === 'running' 
      ? 'bg-amber-100 text-amber-800 border-amber-300 animate-pulse' 
      : 'bg-red-100 text-red-800 border-red-300')"
  class="px-2.5 py-0.5 text-xs font-semibold rounded-full border uppercase tracking-wider transition-colors duration-300"
>
  {{ output.status === 'running' ? 'Running...' : (output.status === 'success' ? 'Success' : 'Failure') }}
</span>
    </div>

    <!-- Download button (Only shows if successful and download URL exists) -->
    <a 
      v-if="output.download_url && output.status === 'success'" 
      v-bind:href="output.download_url" 
      download 
      class="text-xs bg-amber-600 hover:bg-amber-700 text-white font-medium px-3 py-1.5 rounded-lg transition-colors"
    >
      Download CSV
    </a>
  </div>

  <!-- SECTION 1: Graphs / Visualizations -->
  <!-- <div class="bg-white border border-stone-200 rounded-lg p-4 shadow-sm space-y-2">
        <h4 class="text-xs font-semibold text-stone-700 uppercase tracking-wider">Visualizations</h4>
        
        <div class="w-full h-80 bg-stone-50 rounded border border-stone-200 p-2">
          <PlotlyChart 
            v-if="output.graph" 
            :data="output.graph.data" 
            :layout="output.graph.layout" 
          />
          <span v-else class="text-stone-400 text-xs flex items-center justify-center h-full">
            No graph data available
          </span>
        </div>
      </div> -->

  <div class="bg-white border border-stone-200 rounded-lg p-4 shadow-sm space-y-4">
  <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-stone-100 pb-3">
    <h4 class="text-xs font-semibold text-stone-700 uppercase tracking-wider">Visualizations</h4>
    
    <!-- Tab Navigation Buttons -->
    <div v-if="output.graphs && output.graphs.length > 0" class="flex flex-wrap gap-1 bg-stone-100 p-1 rounded-lg">
      <button 
        v-for="(graph, index) in output.graphs" 
        :key="index"
        @click="activeGraphTab = index"
        :class="activeGraphTab === index 
          ? 'bg-white text-stone-900 shadow-sm font-semibold' 
          : 'text-stone-600 hover:text-stone-900'"
        class="px-3 py-1 text-xs rounded-md transition-all"
      >
        {{ graph.title || `Chart ${index + 1}` }}
      </button>
    </div>
  </div>
  
  <!-- Chart Container -->
  <!-- Chart Container -->
<div class="w-full h-80 bg-stone-50 rounded border border-stone-200 p-2">
  <PlotlyChart 
    v-if="output.graphs && output.graphs.length > 0 && output.graphs[activeGraphTab]" 
    :key="activeGraphTab"
    :data="output.graphs[activeGraphTab].data" 
    :layout="output.graphs[activeGraphTab].layout" 
  />
  <span v-else class="text-stone-400 text-xs flex items-center justify-center h-full">
    No graph data available
  </span>
</div>
</div>

  <!-- SECTION 2: Execution Logs -->
  <div class="space-y-2">
    <h4 class="text-xs font-semibold text-stone-700 uppercase tracking-wider">Execution Logs</h4>
    <div class="bg-stone-900 text-stone-200 p-4 rounded-lg font-mono text-xs overflow-x-auto shadow-inner whitespace-pre-wrap max-h-48 overflow-y-auto">
      {{ output.logs || 'No logs recorded.' }}
    </div>
  </div>
</div>
  </div>
</template>

<script setup>
import { apiFetch } from '@/utils/api'
import { ref } from 'vue'
import PlotlyChart from '@/components/PlotlyChart.vue'
const loading = ref(false)
const output = ref(null)
const activeGraphTab = ref(0)

const form = ref({
  cropName: 'Wheat',
  minClusterSize: 3,
  metadataFile: null,
  countsFile: null,
  genotypeFile: null
})

// Capture the target file when it drops into the DOM input node
function handleFileUpload(event, fileKey) {
  const file = event.target.files[0]
  if (file) {
    if (fileKey === 'metadata') form.value.metadataFile = file
    if (fileKey === 'counts') form.value.countsFile = file
    if (fileKey === 'genotype') form.value.genotypeFile = file
  }
}

async function runConsensusPipeline() {
  // Guard clause to ensure files exist before triggering upload pipeline
  if (!form.value.metadataFile || !form.value.countsFile || !form.value.genotypeFile) {
    alert("Please upload all three DArT files before running the pipeline.")
    return
  }

  loading.value = true
  
  // Initialize output state so logs start empty and status shows running
  output.value = {
    status: 'running',
    logs: '',
    graph: null,
    download_url: null,
    parameters_used: null
  }

  try {
    const formData = new FormData()
    formData.append('crop_name', form.value.cropName)
    formData.append('min_cluster_size', form.value.minClusterSize || 3)
    formData.append('metadata_file', form.value.metadataFile)
    formData.append('counts_file', form.value.countsFile)
    formData.append('genotype_file', form.value.genotypeFile)

    const response = await apiFetch('/api/consensus', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) throw new Error('Server error during pipeline execution.')

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = '' // <-- BUFFER TO CATCH PARTIAL CHUNKS

    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      // Append incoming chunk to the buffer
      buffer += decoder.decode(value, { stream: true })
      
      // Split by newline
      const lines = buffer.split('\n')
      
      // Keep the last element in the buffer if it's an incomplete line; 
      // process all preceding fully-formed lines.
      buffer = lines.pop()

      for (const line of lines) {
        if (!line.trim()) continue
        
        try {
          const packet = JSON.parse(line)

          if (packet.type === 'log') {
            output.value.logs += packet.message
          } else if (packet.type === 'result') {
            output.value.status = packet.status
            output.value.graphs = packet.graphs
            output.value.download_url = packet.download_url
            output.value.parameters_used = packet.parameters_used
            console.log(packet.graphs)
          }
        } catch (parseError) {
          console.error("Skipping malformed line:", line, parseError)
        }
      }
    }

  } catch (err) {
    console.error(err)
    output.value.status = 'failure'
    output.value.logs += `\n[ERROR] Failed to execute pipeline backend script: ${err.message}`
  } finally {
    loading.value = false
  }
}
</script>

