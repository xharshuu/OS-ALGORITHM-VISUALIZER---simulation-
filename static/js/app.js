/**
 * Main Application Logic & Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  // Preset Datasets
  const PRESETS = {
    standard: [
      { pid: "P1", arrival: 0, burst: 5, priority: 2 },
      { pid: "P2", arrival: 1, burst: 3, priority: 1 },
      { pid: "P3", arrival: 2, burst: 8, priority: 4 },
      { pid: "P4", arrival: 3, burst: 6, priority: 3 },
    ],
    preemption_demo: [
      { pid: "P1", arrival: 0, burst: 8, priority: 3 },
      { pid: "P2", arrival: 1, burst: 4, priority: 1 },
      { pid: "P3", arrival: 2, burst: 2, priority: 2 },
    ],
    time_slice_boundary: [
      { pid: "P1", arrival: 0, burst: 4, priority: 1 },
      { pid: "P2", arrival: 2, burst: 2, priority: 2 },
      { pid: "P3", arrival: 4, burst: 3, priority: 1 },
    ],
    idle_periods: [
      { pid: "P1", arrival: 1, burst: 3, priority: 2 },
      { pid: "P2", arrival: 6, burst: 4, priority: 1 },
    ],
  };

  // State
  let processes = JSON.parse(JSON.stringify(PRESETS.standard));
  let pidCounter = 5;
  let currentSimulationResult = null;

  // DOM Elements
  const processTableBody = document.getElementById("processTableBody");
  const btnAddProcess = document.getElementById("btnAddProcess");
  const btnResetData = document.getElementById("btnResetData");
  const btnClearAll = document.getElementById("btnClearAll");
  const presetSelect = document.getElementById("presetSelect");
  const algorithmSelect = document.getElementById("algorithmSelect");
  const quantumContainer = document.getElementById("quantumContainer");
  const quantumInput = document.getElementById("quantumInput");
  const btnRunSimulation = document.getElementById("btnRunSimulation");
  const btnCompareAll = document.getElementById("btnCompareAll");
  const errorAlert = document.getElementById("errorAlert");
  const loadingOverlay = document.getElementById("loadingOverlay");

  // Metrics elements
  const metricAvgWT = document.getElementById("metricAvgWT");
  const metricAvgTAT = document.getElementById("metricAvgTAT");
  const metricAvgRT = document.getElementById("metricAvgRT");
  const metricCPUUtil = document.getElementById("metricCPUUtil");
  const metricThroughput = document.getElementById("metricThroughput");
  const metricTotalElapsed = document.getElementById("metricTotalElapsed");
  const resultsTableBody = document.getElementById("resultsTableBody");

  // Initialize playback instance
  const playback = new window.SimulationPlayback({
    containerId: "ganttContainer",
    clockId: "simClock",
    runningProcId: "runningProcessChip",
    playBtnId: "btnPlayPause",
    prevBtnId: "btnPrevStep",
    nextBtnId: "btnNextStep",
    resetBtnId: "btnResetPlay",
    completeBtnId: "btnShowComplete",
    speedSelectId: "playbackSpeedSelect",
  });

  // Render Process Input Table
  function renderProcessTable() {
    processTableBody.innerHTML = "";
    processes.forEach((p, index) => {
      const color = window.GanttVisualizer.getProcessColor(p.pid);
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>
          <div class="d-flex align-items-center gap-2">
            <span class="process-badge" style="background-color: ${color.bg}; min-width: 32px;">${p.pid}</span>
            <input type="text" class="table-input" value="${p.pid}" data-index="${index}" data-field="pid" style="max-width: 80px;" />
          </div>
        </td>
        <td>
          <input type="number" min="0" class="table-input" value="${p.arrival}" data-index="${index}" data-field="arrival" />
        </td>
        <td>
          <input type="number" min="1" class="table-input" value="${p.burst}" data-index="${index}" data-field="burst" />
        </td>
        <td>
          <input type="number" min="0" class="table-input" value="${p.priority}" data-index="${index}" data-field="priority" />
        </td>
        <td class="text-end">
          <button class="btn btn-sm btn-outline-danger-custom btn-delete-row" data-index="${index}" title="Remove Process">
            <i class="bi bi-trash3"></i>
          </button>
        </td>
      `;
      processTableBody.appendChild(row);
    });

    // Attach listeners to input fields
    document.querySelectorAll(".table-input").forEach((input) => {
      input.addEventListener("change", handleInputChange);
    });

    // Attach listeners to delete buttons
    document.querySelectorAll(".btn-delete-row").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const idx = parseInt(btn.getAttribute("data-index"), 10);
        removeProcess(idx);
      });
    });
  }

  function handleInputChange(e) {
    const idx = parseInt(e.target.getAttribute("data-index"), 10);
    const field = e.target.getAttribute("data-field");
    let val = e.target.value.trim();

    if (field === "pid") {
      processes[idx].pid = val;
    } else {
      processes[idx][field] = parseInt(val, 10);
    }
  }

  function addProcess() {
    const newPid = `P${pidCounter++}`;
    processes.push({
      pid: newPid,
      arrival: 0,
      burst: 4,
      priority: 1,
    });
    renderProcessTable();
  }

  function removeProcess(index) {
    if (processes.length <= 1) {
      showError("At least one process must remain in the schedule.");
      return;
    }
    processes.splice(index, 1);
    renderProcessTable();
  }

  function resetData(presetKey = "standard") {
    processes = JSON.parse(JSON.stringify(PRESETS[presetKey] || PRESETS.standard));
    pidCounter = processes.length + 1;
    renderProcessTable();
    hideError();
  }

  function clearAllProcesses() {
    if (confirm("Are you sure you want to clear all processes?")) {
      processes = [{ pid: "P1", arrival: 0, burst: 1, priority: 0 }];
      pidCounter = 2;
      renderProcessTable();
      hideError();
    }
  }

  function showError(msg) {
    errorAlert.textContent = msg;
    errorAlert.classList.remove("d-none");
  }

  function hideError() {
    errorAlert.textContent = "";
    errorAlert.classList.add("d-none");
  }

  function toggleQuantumVisibility() {
    const isRoundRobin = algorithmSelect.value === "round_robin";
    if (isRoundRobin) {
      quantumContainer.classList.remove("d-none");
    } else {
      quantumContainer.classList.add("d-none");
    }
  }

  // Frontend validation
  function validateFrontendInputs() {
    hideError();
    if (processes.length === 0) {
      showError("Please add at least one process.");
      return false;
    }

    const seenPids = new Set();
    for (let i = 0; i < processes.length; i++) {
      const p = processes[i];
      if (!p.pid || !p.pid.trim()) {
        showError(`Process #${i + 1} has an empty Process ID.`);
        return false;
      }
      if (seenPids.has(p.pid)) {
        showError(`Duplicate Process ID '${p.pid}'. All PIDs must be unique.`);
        return false;
      }
      seenPids.add(p.pid);

      if (isNaN(p.arrival) || p.arrival < 0) {
        showError(`Process '${p.pid}' arrival time must be a non-negative integer.`);
        return false;
      }
      if (isNaN(p.burst) || p.burst <= 0) {
        showError(`Process '${p.pid}' burst time must be a positive integer (> 0).`);
        return false;
      }
      if (isNaN(p.priority) || p.priority < 0) {
        showError(`Process '${p.pid}' priority must be a non-negative integer.`);
        return false;
      }
    }

    if (algorithmSelect.value === "round_robin") {
      const q = parseInt(quantumInput.value, 10);
      if (isNaN(q) || q <= 0) {
        showError("Round Robin time quantum must be a positive integer (> 0).");
        return false;
      }
    }

    return true;
  }

  // Execute Scheduling Simulation
  async function runSimulation() {
    if (!validateFrontendInputs()) return;

    hideError();
    loadingOverlay.classList.add("active");

    const payload = {
      algorithm: algorithmSelect.value,
      processes: processes,
      quantum: parseInt(quantumInput.value, 10) || 2,
    };

    try {
      const response = await fetch("/api/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) {
        showError(data.error || "Simulation failed. Please check inputs.");
        return;
      }

      currentSimulationResult = data;
      displayResults(data);
    } catch (err) {
      showError("Connection error while communicating with simulation backend.");
      console.error(err);
    } finally {
      loadingOverlay.classList.remove("active");
    }
  }

  // Display Simulation Results
  function displayResults(data) {
    const metrics = data.metrics;
    metricAvgWT.textContent = metrics.average_waiting_time;
    metricAvgTAT.textContent = metrics.average_turnaround_time;
    metricAvgRT.textContent = metrics.average_response_time;
    metricCPUUtil.textContent = `${metrics.cpu_utilization}%`;
    metricThroughput.textContent = metrics.throughput;
    metricTotalElapsed.textContent = metrics.total_elapsed_time;

    // Populate Results Table
    resultsTableBody.innerHTML = "";
    data.processes.forEach((p) => {
      const color = window.GanttVisualizer.getProcessColor(p.pid);
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>
          <span class="process-badge" style="background-color: ${color.bg};">${p.pid}</span>
        </td>
        <td>${p.arrival}</td>
        <td>${p.burst}</td>
        <td>${p.priority}</td>
        <td>${p.first_start}</td>
        <td class="fw-bold">${p.completion_time}</td>
        <td>${p.turnaround_time}</td>
        <td>${p.waiting_time}</td>
        <td>${p.response_time}</td>
      `;
      resultsTableBody.appendChild(row);
    });

    // Load Gantt timeline into playback engine
    playback.loadData(data.timeline, metrics.total_elapsed_time);

    // Render Charts
    window.AppCharts.renderProcessChart("processMetricsCanvas", data.processes);
  }

  // Cross-Algorithm Comparison
  async function runAlgorithmComparison() {
    if (!validateFrontendInputs()) return;

    hideError();
    loadingOverlay.classList.add("active");

    const payload = {
      processes: processes,
      quantum: parseInt(quantumInput.value, 10) || 2,
    };

    try {
      const response = await fetch("/api/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) {
        showError(data.error || "Comparison failed.");
        return;
      }

      // Render Comparison Chart
      window.AppCharts.renderComparisonChart("comparisonCanvas", data);

      // Scroll smoothly to comparison chart
      const compSection = document.getElementById("comparisonSection");
      if (compSection) {
        compSection.scrollIntoView({ behavior: "smooth" });
      }
    } catch (err) {
      showError("Connection error while requesting algorithm comparison.");
      console.error(err);
    } finally {
      loadingOverlay.classList.remove("active");
    }
  }

  // Event Listeners
  btnAddProcess.addEventListener("click", addProcess);
  btnResetData.addEventListener("click", () => resetData(presetSelect.value));
  btnClearAll.addEventListener("click", clearAllProcesses);
  presetSelect.addEventListener("change", (e) => resetData(e.target.value));
  algorithmSelect.addEventListener("change", toggleQuantumVisibility);
  btnRunSimulation.addEventListener("click", runSimulation);
  btnCompareAll.addEventListener("click", runAlgorithmComparison);

  // Initial setup
  toggleQuantumVisibility();
  renderProcessTable();
  // Auto-run initial simulation with standard sample
  runSimulation();
});
