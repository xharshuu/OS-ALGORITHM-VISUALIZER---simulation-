# OS Algorithm Visualizer — Complete Operating Systems Suite

An interactive, modern desktop application built for Computer Science Operating Systems courses and projects. It provides visual insights, step-by-step playback, real-time Gantt charts, detailed process execution tables, performance metrics, and comparative analytics across core Operating System concepts.

---

## 6 Interactive Core Modules & Views

### 0. Executive Systems Dashboard
* **Unified Command Center**: High-level KPI status across all 5 operating system subsystems (CPU, Memory, Virtual Memory, Process Concurrency, Deadlock).
* **Interactive Launchpad**: Quick-launch overview cards for every module with direct navigation links.
* **Operating Systems Cheat Sheet**: Quick-reference guide summarizing core formulas ($TAT = CT - AT$, $WT = TAT - BT$, $Need = Max - Alloc$, $Hit\ Ratio$).

### 1. CPU Scheduling Simulator
* **Priority Scheduling (Non-preemptive)**: Highest priority ready process runs to completion.
* **Priority Scheduling (Preemptive)**: Immediately preempts when a strictly higher-priority process arrives ($P_{\text{new}} < P_{\text{curr}}$), preserving remaining burst time.
* **Round Robin (RR)**: Maintains a FIFO ready queue with configurable time quantum, correctly handling slice boundary queue order.
* *Priority Rule*: **Smaller integer represents higher priority** ($0 > 1 > 2$).
* *Metrics*: Completion Time ($CT$), Turnaround Time ($TAT = CT - AT$), Waiting Time ($WT = TAT - BT$), Response Time ($RT = \text{First Start} - AT$), CPU Utilization, and Throughput.
* *Visualizer*: Proportional Gantt chart with CPU idle tracking and step-by-step playback controller.

### 2. Contiguous Memory Allocation
* **First Fit**: Allocates the first free memory partition large enough.
* **Best Fit**: Allocates the smallest free block large enough (minimizes internal fragmentation).
* **Worst Fit**: Allocates the largest available block.
* *Visualizer*: Real-time horizontal partition map color-coding allocated space vs. internal fragmentation and free memory.

### 3. Virtual Memory Page Replacement
* **FIFO (First-In, First-Out)**: Replaces the oldest loaded page.
* **LRU (Least Recently Used)**: Replaces the page unreferenced for the longest time.
* **Optimal (OPT)**: Belady's algorithm; replaces the page not used for the longest future duration.
* *Visualizer*: Step-by-step frame allocation matrix highlighting page **Hits** (green) and **Faults** (red), with hit/fault ratios and comparison bar chart.

### 4. Process State Lifecycle & PCB Simulation
* **5-State Process Model**: `NEW`, `READY`, `RUNNING`, `WAITING`, and `TERMINATED`.
* **State Transitions**: Admit, Dispatch, Timeout (Preempt), I/O Request, I/O Complete, and Exit.
* *Visualizer*: Interactive state diagram displaying live process chips inside active queue boxes, plus Process Control Block (PCB) inspector (Program Counter, CPU time, priority, memory).

### 5. Deadlock Avoidance — Banker's Algorithm
* **Safety Algorithm**: Calculates Need matrix ($Need = Max - Allocation$) and determines safe sequences ($\langle P_1 \to P_3 \to \dots \rangle$) or unsafe deadlock states.
* **Resource Request Simulator**: Validates whether a resource request ($Request_i \le Need_i$ and $Request_i \le Available$) can be safely granted without triggering deadlock.

---

## Project Structure

```
d:/OS PROJECT/
├── algorithms/                    # Modular operating system algorithm engines
│   ├── __init__.py
│   ├── deadlock.py                # Banker's safety and resource request algorithms
│   ├── memory.py                  # First Fit, Best Fit, Worst Fit memory engines
│   ├── metrics.py                 # Timing formulas & aggregate calculations
│   ├── page_replacement.py       # FIFO, LRU, Optimal page replacement engines
│   ├── priority.py                # Non-preemptive & Preemptive Priority
│   ├── process_states.py          # 5-state lifecycle machine & PCB model
│   ├── round_robin.py             # Round Robin with queue order preservation
│   └── validation.py              # Input validation & schema checking
├── static/
│   ├── css/style.css              # Custom dark developer-tool dashboard theme
│   ├── js/
│   │   ├── app.js                 # CPU scheduling UI controller
│   │   ├── charts.js              # Chart.js analytics & comparison charts
│   │   ├── gantt.js               # Gantt chart rendering engine
│   │   ├── modules.js             # Memory, Page, Deadlock, and Process State UI controller
│   │   └── playback.js            # Step-by-step playback controller
│   └── vendor/                    # 100% offline local vendor assets
│       ├── bootstrap/
│       ├── bootstrap-icons/
│       └── chartjs/
├── templates/
│   └── index.html                 # Complete single-page multi-module dashboard
├── tests/                         # Comprehensive pytest test suite (46 tests)
│   ├── test_api.py
│   ├── test_deadlock.py
│   ├── test_desktop.py
│   ├── test_memory.py
│   ├── test_metrics.py
│   ├── test_page_replacement.py
│   ├── test_priority.py
│   ├── test_process_states.py
│   ├── test_round_robin.py
│   └── test_validation.py
├── app.py                         # Flask backend application & REST API
├── desktop.py                     # Desktop launcher (pywebview + Waitress WSGI)
├── os_visualizer.spec             # PyInstaller packaging configuration
├── requirements.txt               # Python package dependencies
├── run.bat                        # Windows Batch one-click launcher
├── run.ps1                        # Windows PowerShell one-click launcher
└── pytest.ini                     # Pytest configuration
```

---

## Quick Start Instructions

### 1. Launch Desktop Application
Double-click [`run.bat`](file:///d:/OS%20PROJECT/run.bat) or run:
```bash
python desktop.py
```

### 2. Run via PowerShell
```powershell
.\run.ps1
```

### 3. Run Web Server Mode
```bash
python app.py
```
Then open `http://127.0.0.1:5000` in any browser.

---

## Running Automated Tests

Run the full pytest suite (all 46 tests):
```bash
python -m pytest
```

Output:
```
============================= 46 passed in 1.66s ==============================
```
