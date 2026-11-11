/**
 * Interactive Controller for Memory Allocation, Page Replacement,
 * Deadlock (Banker's Algorithm), and Process States.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Navigation View Switcher
  const navLinks = document.querySelectorAll(".sidebar-nav-item[data-view]");
  const viewSections = document.querySelectorAll(".module-view");

  function switchView(targetView) {
    navLinks.forEach((l) => {
      if (l.getAttribute("data-view") === targetView) {
        l.classList.add("active");
      } else {
        l.classList.remove("active");
      }
    });

    viewSections.forEach((sec) => {
      if (sec.id === targetView) {
        sec.classList.remove("d-none");
      } else {
        sec.classList.add("d-none");
      }
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      switchView(link.getAttribute("data-view"));
    });
  });

  // Dashboard quick-launch buttons
  document.querySelectorAll(".btn-quick-nav").forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-target");
      if (target) {
        switchView(target);
      }
    });
  });

  // ==========================================
  // 1. Memory Allocation Controller
  // ==========================================
  let memoryBlocks = [
    { id: "B1", size: 100 },
    { id: "B2", size: 500 },
    { id: "B3", size: 200 },
    { id: "B4", size: 300 },
    { id: "B5", size: 600 },
  ];

  let memoryProcesses = [
    { pid: "P1", size: 212 },
    { pid: "P2", size: 417 },
    { pid: "P3", size: 112 },
    { pid: "P4", size: 426 },
  ];

  const memBlocksBody = document.getElementById("memBlocksBody");
  const memProcsBody = document.getElementById("memProcsBody");
  const btnAddMemBlock = document.getElementById("btnAddMemBlock");
  const btnAddMemProc = document.getElementById("btnAddMemProc");
  const btnRunMemAlloc = document.getElementById("btnRunMemAlloc");
  const memAlgorithmSelect = document.getElementById("memAlgorithmSelect");
  const memVisualTrack = document.getElementById("memVisualTrack");
  const memResultsBody = document.getElementById("memResultsBody");

  function renderMemoryInputs() {
    if (memBlocksBody) {
      memBlocksBody.innerHTML = "";
      memoryBlocks.forEach((b, idx) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td><input type="text" class="table-input" value="${b.id}" data-idx="${idx}" data-field="id" style="max-width: 80px;" /></td>
          <td><input type="number" min="1" class="table-input" value="${b.size}" data-idx="${idx}" data-field="size" /></td>
          <td class="text-end">
            <button class="btn btn-sm btn-outline-danger-custom btn-del-mem-b" data-idx="${idx}"><i class="bi bi-trash3"></i></button>
          </td>`;
        memBlocksBody.appendChild(row);
      });

      memBlocksBody.querySelectorAll(".table-input").forEach((inp) => {
        inp.addEventListener("change", (e) => {
          const idx = parseInt(e.target.getAttribute("data-idx"), 10);
          const field = e.target.getAttribute("data-field");
          memoryBlocks[idx][field] = field === "size" ? parseInt(e.target.value, 10) : e.target.value;
        });
      });

      memBlocksBody.querySelectorAll(".btn-del-mem-b").forEach((btn) => {
        btn.addEventListener("click", () => {
          if (memoryBlocks.length > 1) {
            memoryBlocks.splice(parseInt(btn.getAttribute("data-idx"), 10), 1);
            renderMemoryInputs();
          }
        });
      });
    }

    if (memProcsBody) {
      memProcsBody.innerHTML = "";
      memoryProcesses.forEach((p, idx) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td><input type="text" class="table-input" value="${p.pid}" data-idx="${idx}" data-field="pid" style="max-width: 80px;" /></td>
          <td><input type="number" min="1" class="table-input" value="${p.size}" data-idx="${idx}" data-field="size" /></td>
          <td class="text-end">
            <button class="btn btn-sm btn-outline-danger-custom btn-del-mem-p" data-idx="${idx}"><i class="bi bi-trash3"></i></button>
          </td>`;
        memProcsBody.appendChild(row);
      });

      memProcsBody.querySelectorAll(".table-input").forEach((inp) => {
        inp.addEventListener("change", (e) => {
          const idx = parseInt(e.target.getAttribute("data-idx"), 10);
          const field = e.target.getAttribute("data-field");
          memoryProcesses[idx][field] = field === "size" ? parseInt(e.target.value, 10) : e.target.value;
        });
      });

      memProcsBody.querySelectorAll(".btn-del-mem-p").forEach((btn) => {
        btn.addEventListener("click", () => {
          if (memoryProcesses.length > 1) {
            memoryProcesses.splice(parseInt(btn.getAttribute("data-idx"), 10), 1);
            renderMemoryInputs();
          }
        });
      });
    }
  }

  if (btnAddMemBlock) {
    btnAddMemBlock.addEventListener("click", () => {
      memoryBlocks.push({ id: `B${memoryBlocks.length + 1}`, size: 250 });
      renderMemoryInputs();
    });
  }

  if (btnAddMemProc) {
    btnAddMemProc.addEventListener("click", () => {
      memoryProcesses.push({ pid: `P${memoryProcesses.length + 1}`, size: 150 });
      renderMemoryInputs();
    });
  }

  async function runMemoryAllocation() {
    const payload = {
      blocks: memoryBlocks,
      processes: memoryProcesses,
      algorithm: memAlgorithmSelect.value,
    };

    try {
      const res = await fetch("/api/memory/allocate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        alert(data.error || "Memory allocation failed");
        return;
      }

      // Render Visual Memory Map
      const totalMem = data.summary.total_memory;
      memVisualTrack.innerHTML = "";
      data.blocks.forEach((b) => {
        const widthPct = (b.initial_size / totalMem) * 100;
        const blkDiv = document.createElement("div");
        blkDiv.className = "mem-block-bar";
        blkDiv.style.width = `${widthPct.toFixed(2)}%`;

        if (b.allocated_pid) {
          const usedPct = (b.allocated_size / b.initial_size) * 100;
          const fragPct = 100 - usedPct;
          blkDiv.innerHTML = `
            <div class="mem-block-allocated" style="width: ${usedPct}%;" title="${b.allocated_pid}: ${b.allocated_size} KB">
              ${b.allocated_pid} (${b.allocated_size}K)
            </div>
            ${
              fragPct > 0
                ? `<div class="mem-block-frag" style="width: ${fragPct}%;" title="Internal Frag: ${b.internal_frag} KB">
                    ${b.internal_frag}K
                  </div>`
                : ""
            }
          `;
        } else {
          blkDiv.innerHTML = `<div class="mem-block-free" style="width: 100%;" title="${b.id}: Free ${b.remaining_size} KB">
            ${b.id} Free (${b.remaining_size}K)
          </div>`;
        }
        memVisualTrack.appendChild(blkDiv);
      });

      // Render Summary Cards
      document.getElementById("memTotal").textContent = `${data.summary.total_memory} KB`;
      document.getElementById("memAllocated").textContent = `${data.summary.allocated_memory} KB`;
      document.getElementById("memFree").textContent = `${data.summary.free_memory} KB`;
      document.getElementById("memFrag").textContent = `${data.summary.total_internal_frag} KB`;

      // Render Table
      memResultsBody.innerHTML = "";
      data.allocations.forEach((a) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${a.pid}</strong></td>
          <td>${a.process_size} KB</td>
          <td>${
            a.allocated
              ? `<span class="badge bg-success">Allocated in ${a.block_id}</span>`
              : `<span class="badge bg-danger">Not Allocated</span>`
          }</td>
          <td>${a.block_initial_size ? `${a.block_initial_size} KB` : "-"}</td>
          <td>${a.allocated ? `${a.internal_frag} KB` : "-"}</td>
        `;
        memResultsBody.appendChild(tr);
      });
    } catch (err) {
      console.error(err);
    }
  }

  if (btnRunMemAlloc) {
    btnRunMemAlloc.addEventListener("click", runMemoryAllocation);
  }

  // ==========================================
  // 2. Page Replacement Controller
  // ==========================================
  const pageRefInput = document.getElementById("pageRefInput");
  const pageFramesInput = document.getElementById("pageFramesInput");
  const pageAlgoSelect = document.getElementById("pageAlgoSelect");
  const btnRunPageSim = document.getElementById("btnRunPageSim");
  const pageMatrixContainer = document.getElementById("pageMatrixContainer");
  let pageChartInstance = null;

  async function runPageReplacement() {
    const rawRef = pageRefInput.value.split(/[\s,]+/).filter(Boolean);
    const numFrames = parseInt(pageFramesInput.value, 10) || 3;
    const algo = pageAlgoSelect.value;

    try {
      const res = await fetch("/api/page-replacement", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reference_string: rawRef,
          num_frames: numFrames,
          algorithm: algo,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        alert(data.error || "Page replacement simulation failed.");
        return;
      }

      if (algo === "compare") {
        renderPageComparison(data);
      } else {
        renderPageMatrix(data);
      }
    } catch (err) {
      console.error(err);
    }
  }

  function renderPageMatrix(data) {
    document.getElementById("pageFaultsVal").textContent = data.summary.total_faults;
    document.getElementById("pageHitsVal").textContent = data.summary.total_hits;
    document.getElementById("pageHitRatioVal").textContent = `${data.summary.hit_ratio}%`;
    document.getElementById("pageFaultRatioVal").textContent = `${data.summary.fault_ratio}%`;

    let html = `
      <div class="table-responsive-custom">
        <table class="table table-bordered text-center text-white" style="border-color: #293750; background: #141E31;">
          <thead>
            <tr style="background: #101728;">
              <th style="color: #95A4BD;">Step</th>
              ${data.steps.map((s) => `<th>${s.page}</th>`).join("")}
            </tr>
          </thead>
          <tbody>`;

    for (let f = 0; f < data.num_frames; f++) {
      html += `<tr><td style="color: #82AAFF; font-weight: bold;">Frame ${f + 1}</td>`;
      data.steps.forEach((s) => {
        const val = s.frames[f] !== "-" ? s.frames[f] : "";
        html += `<td style="font-family: monospace;">${val}</td>`;
      });
      html += `</tr>`;
    }

    html += `<tr><td style="color: #95A4BD;">Status</td>`;
    data.steps.forEach((s) => {
      html += s.is_hit
        ? `<td style="background: rgba(105, 215, 176, 0.25); color: #69D7B0; font-weight: bold;">HIT</td>`
        : `<td style="background: rgba(255, 83, 112, 0.25); color: #FF5370; font-weight: bold;">FAULT</td>`;
    });
    html += `</tr></tbody></table></div>`;

    pageMatrixContainer.innerHTML = html;
  }

  function renderPageComparison(data) {
    const algos = data.algorithms;
    pageMatrixContainer.innerHTML = `
      <div class="alert alert-info py-2">
        Comparison across FIFO, LRU, and Optimal for <strong>${data.reference_string.length}</strong> page references.
      </div>
      <div class="chart-container-card" style="height: 280px;">
        <canvas id="pageCompCanvas"></canvas>
      </div>
    `;

    const ctx = document.getElementById("pageCompCanvas").getContext("2d");
    if (pageChartInstance) pageChartInstance.destroy();

    pageChartInstance = new window.Chart(ctx, {
      type: "bar",
      data: {
        labels: ["FIFO", "LRU", "Optimal"],
        datasets: [
          {
            label: "Page Faults",
            data: [
              algos.fifo.summary.total_faults,
              algos.lru.summary.total_faults,
              algos.optimal.summary.total_faults,
            ],
            backgroundColor: "rgba(255, 83, 112, 0.8)",
          },
          {
            label: "Page Hits",
            data: [
              algos.fifo.summary.total_hits,
              algos.lru.summary.total_hits,
              algos.optimal.summary.total_hits,
            ],
            backgroundColor: "rgba(105, 215, 176, 0.8)",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: "#EDF2FF" } },
          y: { beginAtZero: true, ticks: { color: "#EDF2FF" } },
        },
      },
    });
  }

  if (btnRunPageSim) {
    btnRunPageSim.addEventListener("click", runPageReplacement);
  }

  // ==========================================
  // 3. Deadlock (Banker's Algorithm) Controller
  // ==========================================
  const deadlockProcesses = ["P0", "P1", "P2", "P3", "P4"];
  const deadlockAvailable = [3, 3, 2];
  const deadlockMax = [
    [7, 5, 3],
    [3, 2, 2],
    [9, 0, 2],
    [2, 2, 2],
    [4, 3, 3],
  ];
  const deadlockAlloc = [
    [0, 1, 0],
    [2, 0, 0],
    [3, 0, 2],
    [2, 1, 1],
    [0, 0, 2],
  ];

  const btnCheckSafety = document.getElementById("btnCheckSafety");
  const btnTestRequest = document.getElementById("btnTestRequest");
  const deadlockStatusBanner = document.getElementById("deadlockStatusBanner");
  const deadlockStepsContainer = document.getElementById("deadlockStepsContainer");

  async function checkBankerSafety() {
    try {
      const res = await fetch("/api/deadlock/safety", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          processes: deadlockProcesses,
          available: deadlockAvailable,
          allocation: deadlockAlloc,
          max: deadlockMax,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        alert(data.error);
        return;
      }

      deadlockStatusBanner.className = data.is_safe
        ? "alert alert-success d-block py-2 mb-3"
        : "alert alert-danger d-block py-2 mb-3";
      deadlockStatusBanner.innerHTML = `<strong>${data.message}</strong>`;

      if (data.steps && data.steps.length > 0) {
        let stepsHtml = `<h6 class="text-secondary mt-3">Execution Sequence Steps:</h6><ol class="text-white">`;
        data.steps.forEach((s) => {
          stepsHtml += `<li>Process <strong>${s.pid}</strong> satisfied (Need: [${s.need}]) -> Releases resources -> New Work: [${s.new_work}]</li>`;
        });
        stepsHtml += `</ol>`;
        deadlockStepsContainer.innerHTML = stepsHtml;
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function testBankerRequest() {
    const reqPid = document.getElementById("deadlockReqPid").value;
    const rA = parseInt(document.getElementById("reqA").value, 10) || 0;
    const rB = parseInt(document.getElementById("reqB").value, 10) || 0;
    const rC = parseInt(document.getElementById("reqC").value, 10) || 0;

    try {
      const res = await fetch("/api/deadlock/request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          processes: deadlockProcesses,
          available: deadlockAvailable,
          allocation: deadlockAlloc,
          max: deadlockMax,
          request_pid: reqPid,
          request_vector: [rA, rB, rC],
        }),
      });
      const data = await res.json();
      deadlockStatusBanner.className = data.granted
        ? "alert alert-success d-block py-2 mb-3"
        : "alert alert-danger d-block py-2 mb-3";
      deadlockStatusBanner.innerHTML = `<strong>${data.message || data.error}</strong>`;
    } catch (err) {
      console.error(err);
    }
  }

  if (btnCheckSafety) btnCheckSafety.addEventListener("click", checkBankerSafety);
  if (btnTestRequest) btnTestRequest.addEventListener("click", testBankerRequest);

  // ==========================================
  // 4. Process States Controller
  // ==========================================
  const btnCreateStateProc = document.getElementById("btnCreateStateProc");
  const btnResetStateSim = document.getElementById("btnResetStateSim");
  const selectStateAction = document.getElementById("selectStateAction");
  const btnExecTransition = document.getElementById("btnExecTransition");
  const targetProcSelect = document.getElementById("targetProcSelect");
  const pcbTableBody = document.getElementById("pcbTableBody");

  async function fetchStateSnapshot() {
    try {
      const res = await fetch("/api/process-states/snapshot");
      const data = await res.json();
      updateStateVisuals(data);
    } catch (err) {
      console.error(err);
    }
  }

  function updateStateVisuals(data) {
    const queues = data.queues;
    ["NEW", "READY", "RUNNING", "WAITING", "TERMINATED"].forEach((state) => {
      const container = document.getElementById(`boxState_${state}`);
      if (container) {
        container.innerHTML = "";
        queues[state].forEach((p) => {
          const chip = document.createElement("div");
          chip.className = "process-state-chip";
          chip.innerHTML = `<strong>${p.pid}</strong> <small>(Prio: ${p.priority})</small>`;
          container.appendChild(chip);
        });
      }
    });

    // Populate Target Process Select
    if (targetProcSelect) {
      targetProcSelect.innerHTML = "";
      data.all_pcbs.forEach((p) => {
        const opt = document.createElement("option");
        opt.value = p.pid;
        opt.textContent = `${p.pid} (Current: ${p.state})`;
        targetProcSelect.appendChild(opt);
      });
    }

    // Populate PCB Table
    if (pcbTableBody) {
      pcbTableBody.innerHTML = "";
      data.all_pcbs.forEach((p) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${p.pid}</strong></td>
          <td><span class="badge state-badge-${p.state}">${p.state}</span></td>
          <td>${p.program_counter}</td>
          <td>${p.priority}</td>
          <td>${p.cpu_time_used}</td>
          <td>${p.memory_mb} MB</td>
          <td class="small text-secondary">${p.history[p.history.length - 1]}</td>
        `;
        pcbTableBody.appendChild(tr);
      });
    }
  }

  if (btnCreateStateProc) {
    btnCreateStateProc.addEventListener("click", async () => {
      await fetch("/api/process-states/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ priority: 1, memory_mb: 128 }),
      });
      fetchStateSnapshot();
    });
  }

  if (btnExecTransition) {
    btnExecTransition.addEventListener("click", async () => {
      const pid = targetProcSelect.value;
      const action = selectStateAction.value;
      const res = await fetch("/api/process-states/transition", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pid, action }),
      });
      const data = await res.json();
      if (!res.ok) {
        alert(data.error);
        return;
      }
      updateStateVisuals(data.snapshot);
    });
  }

  if (btnResetStateSim) {
    btnResetStateSim.addEventListener("click", async () => {
      const res = await fetch("/api/process-states/reset", { method: "POST" });
      const data = await res.json();
      updateStateVisuals(data);
    });
  }

  // Initial runs
  renderMemoryInputs();
  runMemoryAllocation();
  runPageReplacement();
  checkBankerSafety();
  fetchStateSnapshot();
});
