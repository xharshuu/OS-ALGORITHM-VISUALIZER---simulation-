/**
 * Gantt Chart Visualization Engine
 */

const GanttVisualizer = (() => {
  // Curated accessible color palette for processes
  const PROCESS_COLORS = [
    { bg: "#4C6EF5", border: "#748FFC" }, // Indigo
    { bg: "#15AABF", border: "#3BC9DB" }, // Cyan
    { bg: "#12B886", border: "#38D9A9" }, // Teal/Emerald
    { bg: "#FAB005", border: "#FFD43B" }, // Amber
    { bg: "#FA5252", border: "#FF8787" }, // Rose
    { bg: "#7950F2", border: "#9775FA" }, // Violet
    { bg: "#E64980", border: "#F783AC" }, // Pink
    { bg: "#FD7E14", border: "#FFA94D" }, // Orange
    { bg: "#40C057", border: "#69DB7C" }, // Green
    { bg: "#228BE6", border: "#4DABF7" }, // Blue
  ];

  const colorCache = new Map();

  function getProcessColor(pid) {
    if (pid === "IDLE") {
      return { bg: "#1E2A3E", border: "#293750" };
    }
    if (!colorCache.has(pid)) {
      const idx = colorCache.size % PROCESS_COLORS.length;
      colorCache.set(pid, PROCESS_COLORS[idx]);
    }
    return colorCache.get(pid);
  }

  function renderGantt(containerId, timeline, totalTime, activeStepIndex = -1) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!timeline || timeline.length === 0 || totalTime <= 0) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="bi bi-clock-history empty-state-icon"></i>
          <div>No timeline data available. Run simulation to view Gantt chart.</div>
        </div>`;
      return;
    }

    let trackHtml = '<div class="gantt-track" id="ganttTrack">';
    let timeTicksHtml = '<div class="gantt-time-scale">';

    // Track unique time boundaries for scale ticks
    const timeBoundaries = new Set([0]);

    timeline.forEach((seg, idx) => {
      const duration = seg.end - seg.start;
      const widthPct = (duration / totalTime) * 100;
      timeBoundaries.add(seg.start);
      timeBoundaries.add(seg.end);

      const isIdle = seg.is_idle || seg.pid === "IDLE";
      const color = getProcessColor(seg.pid);

      let classes = "gantt-segment";
      let inlineStyle = `width: ${widthPct.toFixed(3)}%;`;

      if (isIdle) {
        classes += " idle-segment";
      } else {
        inlineStyle += ` background-color: ${color.bg}; border-color: ${color.border};`;
      }

      // If active step is specified for playback
      if (activeStepIndex >= 0) {
        if (idx === activeStepIndex) {
          classes += " segment-active";
        } else if (idx > activeStepIndex) {
          classes += " segment-dimmed";
        }
      }

      const tooltipText = isIdle
        ? `CPU IDLE: [${seg.start} → ${seg.end}] (${duration} units)`
        : `Process ${seg.pid}: [${seg.start} → ${seg.end}] (${duration} units)`;

      trackHtml += `
        <div class="${classes}" 
             style="${inlineStyle}" 
             data-index="${idx}"
             data-pid="${seg.pid}"
             data-start="${seg.start}"
             data-end="${seg.end}"
             title="${tooltipText}">
          <span>${seg.pid}</span>
        </div>`;
    });

    trackHtml += "</div>";

    // Generate time ticks
    const sortedBoundaries = Array.from(timeBoundaries).sort((a, b) => a - b);
    sortedBoundaries.forEach((timeVal) => {
      const posPct = (timeVal / totalTime) * 100;
      timeTicksHtml += `
        <div class="time-tick" style="left: ${posPct.toFixed(3)}%;">
          <div class="time-tick-line"></div>
          <span>${timeVal}</span>
        </div>`;
    });

    timeTicksHtml += "</div>";

    container.innerHTML = `
      <div class="gantt-chart-wrapper">
        ${trackHtml}
        ${timeTicksHtml}
      </div>`;
  }

  return {
    renderGantt,
    getProcessColor,
  };
})();

window.GanttVisualizer = GanttVisualizer;
