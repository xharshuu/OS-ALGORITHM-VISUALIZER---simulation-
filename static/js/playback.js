/**
 * Simulation Playback Controller
 */

class SimulationPlayback {
  constructor(options = {}) {
    this.timeline = [];
    this.totalTime = 0;
    this.currentStep = -1;
    this.isPlaying = false;
    this.timer = null;
    this.baseIntervalMs = 800; // 1x speed
    this.speedMultiplier = 1.0;

    // UI elements
    this.clockEl = document.getElementById(options.clockId || "simClock");
    this.runningProcEl = document.getElementById(options.runningProcId || "runningProcessChip");
    this.containerId = options.containerId || "ganttContainer";
    this.playBtn = document.getElementById(options.playBtnId || "btnPlayPause");
    this.prevBtn = document.getElementById(options.prevBtnId || "btnPrevStep");
    this.nextBtn = document.getElementById(options.nextBtnId || "btnNextStep");
    this.resetBtn = document.getElementById(options.resetBtnId || "btnResetPlay");
    this.completeBtn = document.getElementById(options.completeBtnId || "btnShowComplete");
    this.speedSelect = document.getElementById(options.speedSelectId || "playbackSpeedSelect");

    this._bindEvents();
  }

  _bindEvents() {
    if (this.playBtn) {
      this.playBtn.addEventListener("click", () => this.togglePlay());
    }
    if (this.nextBtn) {
      this.nextBtn.addEventListener("click", () => this.stepForward());
    }
    if (this.prevBtn) {
      this.prevBtn.addEventListener("click", () => this.stepBackward());
    }
    if (this.resetBtn) {
      this.resetBtn.addEventListener("click", () => this.reset());
    }
    if (this.completeBtn) {
      this.completeBtn.addEventListener("click", () => this.showComplete());
    }
    if (this.speedSelect) {
      this.speedSelect.addEventListener("change", (e) => {
        this.speedMultiplier = parseFloat(e.target.value) || 1.0;
        if (this.isPlaying) {
          this.pause();
          this.play();
        }
      });
    }
  }

  loadData(timeline, totalTime) {
    this.pause();
    this.timeline = timeline || [];
    this.totalTime = totalTime || 0;
    this.currentStep = -1;
    this.showComplete();
  }

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  play() {
    if (!this.timeline.length) return;
    this.isPlaying = true;
    this._updatePlayButton();

    if (this.currentStep >= this.timeline.length - 1) {
      this.currentStep = -1;
    }

    const interval = Math.max(100, Math.floor(this.baseIntervalMs / this.speedMultiplier));
    this.timer = setInterval(() => {
      if (this.currentStep < this.timeline.length - 1) {
        this.currentStep++;
        this._updateUI();
      } else {
        this.pause();
      }
    }, interval);
  }

  pause() {
    this.isPlaying = false;
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this._updatePlayButton();
  }

  stepForward() {
    this.pause();
    if (this.currentStep < this.timeline.length - 1) {
      this.currentStep++;
      this._updateUI();
    }
  }

  stepBackward() {
    this.pause();
    if (this.currentStep > 0) {
      this.currentStep--;
      this._updateUI();
    } else if (this.currentStep === 0) {
      this.currentStep = -1;
      this._updateUI();
    }
  }

  reset() {
    this.pause();
    this.currentStep = -1;
    this._updateUI();
  }

  showComplete() {
    this.pause();
    this.currentStep = this.timeline.length - 1;
    this._updateUI(true);
  }

  _updatePlayButton() {
    if (!this.playBtn) return;
    if (this.isPlaying) {
      this.playBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
      this.playBtn.classList.add("active-play");
      this.playBtn.title = "Pause Simulation";
    } else {
      this.playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
      this.playBtn.classList.remove("active-play");
      this.playBtn.title = "Play Simulation";
    }
  }

  _updateUI(isComplete = false) {
    if (this.currentStep < 0) {
      if (this.clockEl) this.clockEl.textContent = "0";
      if (this.runningProcEl) {
        this.runningProcEl.innerHTML = `<span class="badge bg-secondary">Idle (Ready)</span>`;
      }
      window.GanttVisualizer.renderGantt(this.containerId, this.timeline, this.totalTime, -1);
      return;
    }

    const currentSeg = this.timeline[this.currentStep];
    const isIdle = currentSeg.is_idle || currentSeg.pid === "IDLE";

    if (this.clockEl) {
      this.clockEl.textContent = currentSeg.end;
    }

    if (this.runningProcEl) {
      if (isComplete) {
        this.runningProcEl.innerHTML = `<span class="badge bg-success"><i class="bi bi-check-circle"></i> Complete</span>`;
      } else if (isIdle) {
        this.runningProcEl.innerHTML = `<span class="badge bg-secondary">CPU IDLE [${currentSeg.start} → ${currentSeg.end}]</span>`;
      } else {
        const color = window.GanttVisualizer.getProcessColor(currentSeg.pid);
        this.runningProcEl.innerHTML = `
          <span class="process-badge" style="background-color: ${color.bg};">
            ${currentSeg.pid}
          </span>
          <span style="font-size: 0.8rem; color: #EDF2FF; margin-left: 0.35rem;">
            [${currentSeg.start} → ${currentSeg.end}]
          </span>`;
      }
    }

    window.GanttVisualizer.renderGantt(
      this.containerId,
      this.timeline,
      this.totalTime,
      isComplete ? -1 : this.currentStep
    );
  }
}

window.SimulationPlayback = SimulationPlayback;
