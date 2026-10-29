<template>
  <div class="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
    <div>
      <h2 class="text-2xl font-bold text-stone-900">
        Purity Calculation and Analysis
      </h2>
      <p class="text-sm text-stone-500 mt-1">
        Using consensus sequences, estimate the purity of a set of samples.
      </p>
    </div>

    <form
      @submit.prevent="runPurityPipeline"
      class="bg-white rounded-xl shadow-xs border border-stone-200 p-6 space-y-6"
    >
      <!-- General Parameters Group -->
      <div
        class="bg-stone-50 border border-stone-200 rounded-lg p-5 space-y-4 shadow-m"
      >
        <div class="border-b border-stone-200 pb-2">
          <h3
            class="text-sm font-bold text-emerald-800 uppercase tracking-wider"
          >
            Genotype Files
          </h3>
          <p class="text-xs text-stone-500">
            Upload your genotype data along with metadata and consensus data.
          </p>
        </div>

        <div class="grid grid-cols-1 gap-4">
          <!-- Metadata File -->
          <div>
            <label class="block text-xs font-semibold text-stone-600 mb-1"
              >1. Metadata File (.csv)</label
            >
            <input
              type="file"
              @change="handleFileUpload($event, 'metadata')"
              accept=".csv"
              class="w-full text-sm block file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 border border-stone-300 rounded-lg p-1 bg-white"
            />

            <div
              v-if="fileError"
              class="mt-2 text-xs bg-red-50 text-red-700 border border-red-200 rounded-md p-2.5 flex items-center justify-between"
            >
              <span>{{ fileError }}</span>
              <span class="font-semibold"
                >Required: {{ requiredColumns.join(", ") }}</span
              >
            </div>
          </div>
          <div
            v-if="
              availableColumns.length > 0 ||
              form.selectedMetadataColumns.length > 0
            "
            class="mt-4 space-y-2"
          >
            <!-- Section Title -->
            <label class="block text-xs font-semibold text-stone-600">
              Metadata Columns
            </label>

            <!-- Side-by-Side Selector Grid -->
            <div
              class="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] items-center gap-3"
            >
              <!-- Available Columns Box -->
              <div class="border border-stone-300 rounded-lg p-4 bg-white">
                <h4
                  class="text-sm font-semibold text-stone-700 mb-3 flex justify-between items-center"
                >
                  <span>Available Columns</span>
                  <span
                    class="text-xs bg-stone-100 text-stone-600 px-2 py-0.5 rounded-full"
                  >
                    {{ availableColumns.length }}
                  </span>
                </h4>
                <ul
                  class="h-52 overflow-y-auto space-y-1 pr-1 border border-stone-100 rounded p-2 bg-stone-50/50"
                >
                  <li
                    v-for="col in availableColumns"
                    :key="col"
                    class="flex items-center justify-between text-sm p-1.5 hover:bg-stone-100 rounded transition-colors"
                  >
                    <span class="text-stone-800 truncate mr-2">{{ col }}</span>
                    <button
                      type="button"
                      @click="selectColumn(col)"
                      class="text-xs bg-emerald-50 text-emerald-700 hover:bg-emerald-100 px-2.5 py-1 rounded font-semibold shrink-0"
                    >
                      +
                    </button>
                  </li>
                  <li
                    v-if="availableColumns.length === 0"
                    class="text-xs text-stone-400 text-center py-16"
                  >
                    All columns selected
                  </li>
                </ul>
              </div>

              <!-- Directional Arrow (Responsive: points down on mobile, right on desktop) -->
              <div
                class="flex items-center justify-center text-stone-400 font-bold text-xl py-1 md:py-0"
              >
                <span class="md:hidden">&darr;</span>
                <span class="hidden md:inline">&rarr;</span>
              </div>

              <!-- Selected Columns Box -->
              <div
                class="border border-stone-300 rounded-lg p-4 bg-white shadow-sm"
              >
                <h4
                  class="text-sm font-semibold text-stone-700 mb-3 flex justify-between items-center"
                >
                  <span>To include in Analysis</span>
                  <span
                    class="text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full"
                  >
                    {{ form.selectedMetadataColumns.length }}
                  </span>
                </h4>
                <ul
                  class="h-52 overflow-y-auto space-y-1 pr-1 border border-stone-100 rounded p-2 bg-stone-50/50"
                >
                  <li
                    v-for="col in form.selectedMetadataColumns"
                    :key="col"
                    class="flex items-center justify-between text-sm p-1.5 hover:bg-stone-100 rounded transition-colors"
                  >
                    <!-- Show '-' button ONLY if it's NOT a required column -->
                    <button
                      v-if="!requiredColumns.includes(col)"
                      type="button"
                      @click="deselectColumn(col)"
                      class="text-xs bg-red-50 text-red-700 hover:bg-red-100 px-2.5 py-1 rounded font-semibold shrink-0 mr-2"
                    >
                      &minus;
                    </button>

                    <span class="text-stone-800 truncate text-right flex-1">{{
                      col
                    }}</span>
                  </li>
                  <li
                    v-if="form.selectedMetadataColumns.length === 0"
                    class="text-xs text-stone-400 text-center py-16"
                  >
                    No columns selected
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Counts File -->
          <div>
            <label class="block text-xs font-semibold text-stone-600 mb-1"
              >2. Consensus File (.csv)</label
            >
            <input
              type="file"
              @change="handleFileUpload($event, 'consensus')"
              accept=".csv"
              class="w-full text-sm block file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 border border-stone-300 rounded-lg p-1 bg-white"
            />
          </div>

          <!-- Genotype File -->
          <div>
            <label class="block text-xs font-semibold text-stone-600 mb-1"
              >3. Sample Genotype File (.csv)</label
            >
            <input
              type="file"
              @change="handleFileUpload($event, 'genotype')"
              class="w-full text-sm block file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 border border-stone-300 rounded-lg p-1 bg-white"
            />
          </div>
        </div>
      </div>
      <!-- Execution Button -->
      <div class="pt-2">
        <button
          type="submit"
          :disabled="loading"
          class="bg-emerald-700 hover:bg-emerald-800 text-white font-medium py-2.5 px-5 rounded-lg shadow-sm transition-colors disabled:opacity-50 flex items-center space-x-2"
        >
          <span>{{ loading ? "Running..." : "Calculate Purity Scores" }}</span>
        </button>
      </div>
    </form>
    <!-- </div> -->

    <div
      v-if="output"
      class="bg-stone-950 text-stone-200 rounded-xl p-4 font-mono text-xs shadow-md space-y-2"
    >
      <div
        class="flex justify-between items-center border-b border-stone-800 pb-2"
      >
        <span class="font-bold flex items-center space-x-2">
          <span
            :class="
              output.status === 'running'
                ? 'bg-amber-500 animate-pulse'
                : output.status === 'success'
                  ? 'bg-green-500'
                  : 'bg-red-500'
            "
            class="w-2.5 h-2.5 rounded-full inline-block"
          ></span>
          <span>Pipeline Execution Logs</span>
        </span>
        <span class="text-[10px] text-stone-500 uppercase tracking-wider">{{
          output.status
        }}</span>
      </div>
      <pre
        ref="logContainer"
        class="whitespace-pre-wrap h-40 overflow-y-auto text-stone-300 leading-relaxed"
        >{{ output.logs }}</pre
      >
    </div>
    <div
      v-if="output"
      class="bg-amber-50/60 border border-amber-200 rounded-xl p-5 space-y-5"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <h3 class="text-sm font-bold text-amber-900 tracking-wide uppercase">
            Pipeline Execution Result
          </h3>

          <!-- Dynamic Status Pill -->
          <span
            :class="
              output.status === 'success'
                ? 'bg-green-100 text-green-800 border-green-300'
                : output.status === 'running'
                  ? 'bg-amber-100 text-amber-800 border-amber-300 animate-pulse'
                  : 'bg-red-100 text-red-800 border-red-300'
            "
            class="px-2.5 py-0.5 text-xs font-semibold rounded-full border uppercase tracking-wider transition-colors duration-300"
          >
            {{
              output.status === "running"
                ? "Running..."
                : output.status === "success"
                  ? "Success"
                  : "Failure"
            }}
          </span>
        </div>

        <!-- Download button (Only shows if successful and download URL exists) -->
        <!-- <a 
      v-if="output.download_url && output.status === 'success'" 
      v-bind:href="output.download_url" 
      download 
      class="text-xs bg-amber-600 hover:bg-amber-700 text-white font-medium px-3 py-1.5 rounded-lg transition-colors"
    >
      Download CSV
    </a> -->
        <a
          v-if="output.download_url && output.status === 'success'"
          v-bind:href="downloaded ? null : output.download_url"
          @click="handleDownload"
          :class="
            downloaded
              ? 'bg-stone-200 text-stone-400 cursor-not-allowed pointer-events-none border-stone-300'
              : 'bg-amber-600 hover:bg-amber-700 text-white cursor-pointer shadow-xs'
          "
          class="inline-flex items-center space-x-1.5 text-xs font-medium px-3.5 py-2 rounded-lg transition-colors border border-transparent"
        >
          <svg
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
          <span>{{
            downloaded ? "Bundle Downloaded" : "Download (.csv)"
          }}</span>
        </a>
      </div>
    </div>
    <!-- Dashboard Main Grid (Only shown when data is loaded) -->
    <div
      v-if="rawDataset && rawDataset.length > 0"
      class="grid grid-cols-1 lg:grid-cols-4 gap-6"
    >
      <!-- Controls & Sidebar Filters (1 Column) -->
      <div
        class="lg:col-span-1 space-y-4 bg-white p-5 rounded-xl border border-stone-200 shadow-2xs"
      >
        <h2 class="text-sm font-bold text-stone-800 border-b pb-2">
          Grouping & Filters
        </h2>

        <!-- Axis & Split Controls -->
        <div>
          <label class="block text-xs font-semibold text-stone-600 mb-1"
            >X-Axis Grouping</label
          >
          <select
            v-model="xAxisCol"
            class="w-full border border-stone-300 rounded-lg p-2 text-xs"
          >
            <option
              v-for="col in detectedCategoricalCols"
              :key="col"
              :value="col"
            >
              {{ col }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-semibold text-stone-600 mb-1"
            >Color / Categorical Split</label
          >
          <select
            v-model="colorCol"
            class="w-full border border-stone-300 rounded-lg p-2 text-xs"
          >
            <option
              v-for="col in detectedCategoricalCols"
              :key="col"
              :value="col"
            >
              {{ col }}
            </option>
          </select>
        </div>
        <div
          v-for="col in detectedCategoricalCols"
          :key="col"
          class="space-y-1 pt-3 border-t border-stone-100"
        >
          <div class="flex justify-between items-center">
            <label
              class="block text-xs font-bold text-stone-700 uppercase tracking-wide"
              >{{ col }}</label
            >
            <span class="text-[10px] text-stone-400"
              >({{ (activeFilters[col] || []).length }}/{{
                filterOptionsMap[col]?.length || 0
              }})</span
            >
          </div>

          <div class="max-h-28 overflow-y-auto space-y-1 pr-1 text-xs">
            <label
              v-for="val in filterOptionsMap[col]"
              :key="val"
              class="flex items-center space-x-2 cursor-pointer hover:bg-stone-50 p-1 rounded"
            >
              <input
                type="checkbox"
                :value="val"
                v-model="activeFilters[col]"
                class="rounded border-stone-300 text-amber-600 focus:ring-amber-500"
              />
              <span class="text-stone-600 truncate">{{ val }}</span>
            </label>
          </div>
        </div>
        <!-- Dynamic Category Filters -->
        <div>
          <label class="block text-xs font-semibold text-stone-600 mb-1"
            >Points Mode</label
          >
          <select
            v-model="pointsMode"
            class="w-full border border-stone-300 rounded-lg p-2 text-xs"
          >
            <option value="outliers">Outliers Only</option>
            <option value="all">All Points</option>
            <option :value="false">None</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-semibold text-stone-600 mb-1"
            >Color Palette</label
          >
          <select
            v-model="selectedPalette"
            class="w-full border border-stone-300 rounded-lg p-2 text-xs"
          >
            <option value="G10">Tableau / G10</option>
            <option value="Flatly">Flatly Theme Match</option>
            <option value="D3">D3 Corporate</option>
            <option value="Set2">Set2 (Soft)</option>
          </select>
        </div>
      </div>

      <!-- Main Visualizations Section (3 Columns) -->
      <div class="lg:col-span-3 space-y-6">
        <!-- Tab Controls -->
        <div class="flex space-x-2 border-b border-stone-200 pb-2">
          <button
            @click="activeTab = 'plots'"
            :class="
              activeTab === 'plots'
                ? 'bg-amber-600 text-white'
                : 'bg-stone-100 text-stone-600'
            "
            class="px-4 py-1.5 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
          >
            Plots
          </button>
          <button
            @click="activeTab = 'table'"
            :class="
              activeTab === 'table'
                ? 'bg-amber-600 text-white'
                : 'bg-stone-100 text-stone-600'
            "
            class="px-4 py-1.5 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
          >
            Summary Table
          </button>
        </div>

        <!-- Tab 1: Plotly Charts -->
        <div v-show="activeTab === 'plots'" class="space-y-6">
          <div
            class="bg-white p-4 border border-stone-200 rounded-xl shadow-2xs"
          >
            <div id="box-plot-graph" class="w-full h-96"></div>
          </div>

          <div
            class="bg-white p-4 border border-stone-200 rounded-xl shadow-2xs"
          >
            <div id="scatter-plot-graph" class="w-full h-96"></div>
          </div>

          <div
            class="bg-white p-4 border border-stone-200 rounded-xl shadow-2xs"
          >
            <div id="barnhart-graph" class="w-full h-96"></div>
          </div>

          <div
            class="bg-white p-4 border border-stone-200 rounded-xl shadow-2xs"
          >
            <div id="purity-pie-graph" class="w-full h-96"></div>
          </div>
        </div>

        <!-- Tab 2: Aggregated Metrics Table -->
        <div
          v-show="activeTab === 'table'"
          class="bg-white p-4 border rounded-xl shadow-2xs overflow-x-auto"
        >
          <h3 class="text-xs font-bold text-stone-700 mb-3">
            Aggregated Metrics
          </h3>
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="bg-stone-800 text-white">
                <th class="p-2 border">{{ xAxisCol }}</th>
                <th class="p-2 border">{{ colorCol }}</th>
                <th class="p-2 border text-center">Count</th>
                <th class="p-2 border text-center">Mean Purity</th>
                <th class="p-2 border text-center">Std Dev</th>
                <th class="p-2 border text-center">% Class A</th>
                <th class="p-2 border text-center">% Class B</th>
                <th class="p-2 border text-center">% Class C</th>
                <th class="p-2 border text-center">% Class D</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, idx) in summaryTableData"
                :key="idx"
                :class="idx % 2 === 1 ? 'bg-stone-50' : 'bg-white'"
              >
                <td class="p-2 border font-medium">{{ row.xVal }}</td>
                <td class="p-2 border">{{ row.colorVal }}</td>
                <td class="p-2 border text-center">{{ row.count }}</td>
                <td class="p-2 border text-center">
                  {{ row.mean.toFixed(2) }}%
                </td>
                <td class="p-2 border text-center">
                  {{ row.stdDev.toFixed(2) }}
                </td>
                <td class="p-2 border text-center text-green-600 font-medium">
                  {{ row.pctA.toFixed(1) }}%
                </td>
                <td class="p-2 border text-center text-yellow-600 font-medium">
                  {{ row.pctB.toFixed(1) }}%
                </td>
                <td class="p-2 border text-center text-orange-600 font-medium">
                  {{ row.pctC.toFixed(1) }}%
                </td>
                <td class="p-2 border text-center text-red-600 font-medium">
                  {{ row.pctD.toFixed(1) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from "vue";
import Plotly from "plotly.js-dist-min";
import { apiFetch } from "@/utils/api";
import Papa from "papaparse";

const availableColumns = ref([]);
const detectedCategoricalCols = ref(["Assigned Cluster", "reference"]);
const loading = ref(false);
const output = ref(null);
const rawDataset = ref([]);
const activeTab = ref("plots");
const requiredColumns = ["sample_id", "reference"];
const fileError = ref(null);
const downloaded = ref(false);

const form = ref({
  metadataFile: null,
  consensusFile: null,
  genotypeFile: null,
  selectedMetadataColumns: [],
});

// Configurable Dropdown Selections
const pointsMode = ref("outliers");
const selectedPalette = ref("G10");

const categoricalCols = [
  "Assigned Cluster",
  "Best Consensus ID",
  "Reference",
  "Seed Class",
  "Sample Type",
  "Prediction Type",
  "Study",
  "Year",
  "Tissue",
  "Provider",
  "Product Type",
];

// Palettes Configuration
const PALETTES = {
  G10: ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
  Flatly: ["#18BC9C", "#3498DB", "#E74C3C", "#F39C12", "#9B59B6", "#34495E"],
  D3: ["#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a"],
  Set2: ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f"],
};

// Color scheme map for Barnhart Quality Classes
const purityColorsMap = {
  A: "#2ca02c",
  B: "#bcbd22",
  C: "#ff7f0e",
  D: "#d62728",
};
// Dynamic Schema State
const filterOptionsMap = ref({});
const activeFilters = ref({});
const xAxisCol = ref("reference");
const colorCol = ref("Assigned Cluster");

const handleDownload = () => {
  setTimeout(() => {
    downloaded.value = true;
  }, 200);
};

// --- Calculated Summary Table (Fixed Standard Deviation Syntax) ---
const summaryTableData = computed(() => {
  if (!filteredDataset.value.length) return [];

  const groups = {};
  filteredDataset.value.forEach((row) => {
    const xKey = row[xAxisCol.value] || "N/A";
    const colorKey = row[colorCol.value] || "N/A";
    const groupKey = `${xKey}___${colorKey}`;

    if (!groups[groupKey]) {
      groups[groupKey] = { xVal: xKey, colorVal: colorKey, items: [] };
    }
    groups[groupKey].items.push(row);
  });

  return Object.values(groups).map((g) => {
    const values = g.items
      .map((i) => i["Purity Index"])
      .filter((v) => v != null);
    const count = values.length;
    const mean = count ? values.reduce((a, b) => a + b, 0) / count : 0;

    // Corrected Standard Deviation calculation
    const stdDev =
      count > 1
        ? Math.sqrt(
            values.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) /
              (count - 1),
          )
        : 0;

    const pctA =
      (g.items.filter((i) => i["Purity Class"] === "A").length / count) * 100 ||
      0;
    const pctB =
      (g.items.filter((i) => i["Purity Class"] === "B").length / count) * 100 ||
      0;
    const pctC =
      (g.items.filter((i) => i["Purity Class"] === "C").length / count) * 100 ||
      0;
    const pctD =
      (g.items.filter((i) => i["Purity Class"] === "D").length / count) * 100 ||
      0;

    return {
      xVal: g.xVal,
      colorVal: g.colorVal,
      count,
      mean,
      stdDev,
      pctA,
      pctB,
      pctC,
      pctD,
    };
  });
});

// const filteredDataset = computed(() => {
//   if (!rawDataset.value.length) return [];

//   return rawDataset.value.filter((d) => {
//     // Check every categorical column's active filters
//     for (const col of detectedCategoricalCols.value) {
//       const allowedValues = activeFilters.value[col];
//       if (allowedValues) {
//         const val =
//           d[col] !== undefined && d[col] !== null ? String(d[col]) : "N/A";
//         // If the row's value is not in the allowed checked list, filter it out
//         if (!allowedValues.includes(val) && !allowedValues.includes(d[col])) {
//           return false;
//         }
//       }
//     }
//     return true;
//   });
// });

const filteredDataset = computed(() => {
  return rawDataset.value;
});

// --- Simplified Plotly Chart Rendering Logic ---
const renderCharts = async () => {
  if (!rawDataset.value || rawDataset.value.length === 0) {
    console.warn("renderCharts aborted: rawDataset is empty.");
    return;
  }

  await nextTick(); // Ensure DOM containers are fully rendered

  const boxEl = document.getElementById("box-plot-graph");
  if (!boxEl) {
    console.warn(
      "renderCharts aborted: DOM element #box-plot-graph not found. Are you on the Plots tab?",
    );
    return;
  }

  console.log("Rendering graphs with dataset size:", rawDataset.value.length);

  const palette = PALETTES.G10;
  const colorCategories = [
    ...new Set(rawDataset.value.map((d) => d[colorCol.value])),
  ];
  const colorMap = {};
  colorCategories.forEach((cat, idx) => {
    colorMap[cat] = palette[idx % palette.length];
  });

  // 1. Box Plot
  const boxTraces = colorCategories.map((cat) => {
    const subset = rawDataset.value.filter((d) => d[colorCol.value] === cat);
    return {
      type: "box",
      x: subset.map((d) => d[xAxisCol.value]),
      y: subset.map((d) => d["Purity Index"]),
      name: String(cat),
      boxpoints: pointsMode.value || "outliers",
      marker: { color: colorMap[cat] },
    };
  });
  Plotly.newPlot(
    "box-plot-graph",
    boxTraces,
    {
      title: { text: `Purity Index by ${xAxisCol.value}` },
      boxmode: "group",
      margin: { l: 30, r: 20, t: 40, b: 30 },
      template: "plotly_white",
    },
    { responsive: true },
  );

  // 2. Scatter Plot (Sample Volume vs Purity Pass Rate)
  const groupMap = {};
  rawDataset.value.forEach((d) => {
    const xVal = d[xAxisCol.value] || "N/A";
    const cVal = d[colorCol.value] || "N/A";
    const key = `${xVal}___${cVal}`;
    if (!groupMap[key]) {
      groupMap[key] = { xVal, cVal, total: 0, pass: 0 };
    }
    groupMap[key].total++;
    if (d["Purity Index"] >= 90) groupMap[key].pass++;
  });

  const scatterData = Object.values(groupMap);
  const scatterTraces = colorCategories.map((cat) => {
    const subset = scatterData.filter((d) => d.cVal === cat);
    return {
      type: "scatter",
      mode: "markers",
      x: subset.map((d) => (d.total > 0 ? (d.pass / d.total) * 100 : 0)),
      y: subset.map((d) => d.total),
      text: subset.map((d) => d.xVal),
      name: String(cat),
      marker: { color: colorMap[cat], size: 12 },
    };
  });

  Plotly.newPlot(
    "scatter-plot-graph",
    scatterTraces,
    {
      title: { text: `Sample Volume vs. Purity by ${xAxisCol.value}` },
      template: "plotly_white",
      xaxis: { title: { text: "% of Samples ≥ 90% Purity" } },
      yaxis: { title: { text: "Total Sample Count" } },
      margin: { l: 30, r: 20, t: 40, b: 30 },
    },
    { responsive: true },
  );

  // 3. Control Chart / Strip Plot
  const barnhartTraces = ["A", "B", "C", "D"].map((pClass) => {
    const subset = rawDataset.value.filter((d) => d["Purity Class"] === pClass);
    return {
      type: "scatter",
      mode: "markers",
      x: subset.map((d) => d[xAxisCol.value]),
      y: subset.map((d) => d["Purity Index"]),
      name: `Class ${pClass}`,
      marker: { color: purityColorsMap[pClass], size: 8 },
    };
  });

  Plotly.newPlot(
    "barnhart-graph",
    barnhartTraces,
    {
      title: { text: "Purity Control Chart (Quality Bands)" },
      template: "plotly_white",
      yaxis: { range: [0, 105], title: { text: "Purity Index (%)" } },
      margin: { l: 30, r: 30, t: 40, b: 30 },
    },
    { responsive: true },
  );

  // 4. Distribution Pie Chart
  const pieCounts = { A: 0, B: 0, C: 0, D: 0 };
  rawDataset.value.forEach((d) => {
    if (d["Purity Class"]) pieCounts[d["Purity Class"]]++;
  });

  Plotly.newPlot(
    "purity-pie-graph",
    [
      {
        type: "pie",
        labels: ["Class A", "Class B", "Class C", "Class D"],
        values: [pieCounts.A, pieCounts.B, pieCounts.C, pieCounts.D],
        marker: {
          colors: [
            purityColorsMap.A,
            purityColorsMap.B,
            purityColorsMap.C,
            purityColorsMap.D,
          ],
        },
        hole: 0.3,
      },
    ],
    {
      title: { text: "Purity Classes" },
      margin: { l: 20, r: 20, t: 40, b: 20 },
      template: "plotly_white",
    },
    { responsive: true },
  );
};

function handleFileUpload(event, fileKey) {
  const file = event.target.files[0];
  if (!file) return;

  if (fileKey === "metadata") {
    // Reset previous errors
    fileError.value = null;

    Papa.parse(file, {
      header: true,
      preview: 1, // Only read headers
      complete: (results) => {
        const fields = results.meta.fields || [];

        // Check which required columns are missing
        const missingColumns = requiredColumns.filter(
          (reqCol) => !fields.includes(reqCol),
        );

        if (missingColumns.length > 0) {
          // Validation failed: alert user and clear file reference
          fileError.value = `The uploaded CSV is missing required columns.`;
          form.value.metadataFile = null;
          availableColumns.value = [];
          form.value.selectedMetadataColumns = [];
          event.target.value = "";
          return;
        }

        // Validation passed
        form.value.metadataFile = file;

        // 1. Put ONLY required columns in the "included" box initially
        form.value.selectedMetadataColumns = [...requiredColumns];

        // 2. Put all other columns in the "available" box
        availableColumns.value = fields.filter(
          (col) => !requiredColumns.includes(col),
        );
      },
      error: (error) => {
        fileError.value = "Failed to parse CSV file. Please check the format.";
        console.error("Papa Parse error:", error);
      },
    });
  } else if (fileKey === "consensus") {
    form.value.consensusFile = file;
  } else if (fileKey === "genotype") {
    form.value.genotypeFile = file;
  }
}

// Move column from Available -> Selected
function deselectColumn(col) {
  if (requiredColumns.includes(col)) return; // Prevent removing required columns

  form.value.selectedMetadataColumns =
    form.value.selectedMetadataColumns.filter((c) => c !== col);
  availableColumns.value.push(col);
}

function selectColumn(col) {
  availableColumns.value = availableColumns.value.filter((c) => c !== col);
  form.value.selectedMetadataColumns.push(col);
}

async function runPurityPipeline() {
  // Guard clause to ensure files exist before triggering upload pipeline
  if (
    !form.value.metadataFile ||
    !form.value.consensusFile ||
    !form.value.genotypeFile
  ) {
    alert("Please upload all three DArT files before running the pipeline.");
    return;
  }
  downloaded.value = false;
  loading.value = true;

  // Initialize output state so logs start empty and status shows running
  output.value = {
    status: "running",
    logs: "",
    graph: null,
    download_url: null,
    parameters_used: null,
  };

  try {
    const formData = new FormData();
    formData.append("metadata_file", form.value.metadataFile);
    formData.append("consensus_file", form.value.consensusFile);
    formData.append("genotype_file", form.value.genotypeFile);
    formData.append(
      "selected_columns",
      JSON.stringify(form.value.selectedMetadataColumns),
    );

    const response = await apiFetch("/api/purity", {
      method: "POST",
      body: formData,
    });

    if (!response.ok)
      throw new Error("Server error during pipeline execution.");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = ""; // Buffer to catch partial chunks

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      // Append incoming chunk to the buffer
      buffer += decoder.decode(value, { stream: true });

      // Split by newline
      const lines = buffer.split("\n");

      // Keep the last element in the buffer if it's an incomplete line;
      // process all preceding fully-formed lines.
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.trim()) continue;

        try {
          const packet = JSON.parse(line);

          if (packet.type === "log") {
            output.value.logs += packet.message;
          } else if (packet.type === "result") {
            output.value.status = packet.status;
            output.value.parameters_used = packet.parameters_used;
            output.value.download_url = packet.download_url;
            // Direct assignment because backend sends to_dict(orient="records")
            rawDataset.value = Array.isArray(packet.graphs)
              ? packet.graphs
              : [];

            console.log(
              "Data successfully loaded. Rows received:",
              rawDataset.value.length,
            );

            // Hardcode or set default axes for testing graphs
            xAxisCol.value = "reference";
            colorCol.value = "Assigned Cluster";

            // Render charts immediately once data is loaded
            await nextTick();
            renderCharts();
          }
        } catch (parseError) {
          console.error("Skipping malformed line:", line, parseError);
        }
      }
    }
  } catch (err) {
    console.error(err);
    output.value.status = "failure";
    output.value.logs += `\n[ERROR] Failed to execute pipeline backend script: ${err.message}`;
  } finally {
    loading.value = false;
  }
}

// Existing watch for general dropdowns, data updates, and tab switches
watch(
  [rawDataset, xAxisCol, colorCol, pointsMode, selectedPalette, activeTab],
  async () => {
    if (rawDataset.value.length > 0 && activeTab.value === "plots") {
      await nextTick();
      renderCharts();
    }
  },
);

// 2. Separate deep watch specifically for checkbox filter toggles
watch(
  activeFilters,
  async () => {
    if (rawDataset.value.length > 0 && activeTab.value === "plots") {
      await nextTick();
      renderCharts();
    }
  },
  { deep: true }, // Crucial for detecting inner checkbox array changes
);
</script>
