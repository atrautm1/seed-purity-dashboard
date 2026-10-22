<template>
  <div ref="chartElement" class="w-full h-full min-h-[300px]"></div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import Plotly from 'plotly.js-dist-min'

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  layout: {
    type: Object,
    default: () => ({})
  },
  config: {
    type: Object,
    default: () => ({ responsive: true, displayModeBar: true })
  }
})

const chartElement = ref(null)

const renderChart = async () => {
  await nextTick()
  if (chartElement.value && props.data) {
    try {
      // Deep clone data and layout so Plotly cannot mutate reactive props in-place
      const clonedData = JSON.parse(JSON.stringify(props.data))
      const clonedLayout = JSON.parse(JSON.stringify(props.layout))

      Plotly.react(chartElement.value, clonedData, clonedLayout, props.config)
    } catch (e) {
      console.error("Plotly render error:", e)
    }
  }
}

onMounted(() => {
  renderChart()
})

watch(
  () => [props.data, props.layout],
  () => {
    renderChart()
  },
  { deep: true }
)
</script>