/**
 * Chart.js Visualization Module
 */

const AppCharts = (() => {
  let processMetricsChart = null;
  let comparisonChart = null;

  const THEME = {
    textColor: "#EDF2FF",
    secondaryTextColor: "#95A4BD",
    gridColor: "rgba(41, 55, 80, 0.6)",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  };

  function renderProcessChart(canvasId, processes) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !window.Chart) return;

    if (processMetricsChart) {
      processMetricsChart.destroy();
      processMetricsChart = null;
    }

    if (!processes || processes.length === 0) return;

    const labels = processes.map((p) => p.pid);
    const waitingTimes = processes.map((p) => p.waiting_time);
    const turnaroundTimes = processes.map((p) => p.turnaround_time);
    const responseTimes = processes.map((p) => p.response_time);

    const ctx = canvas.getContext("2d");
    processMetricsChart = new window.Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Waiting Time (WT)",
            data: waitingTimes,
            backgroundColor: "rgba(130, 170, 255, 0.8)",
            borderColor: "#82AAFF",
            borderWidth: 1,
            borderRadius: 4,
          },
          {
            label: "Turnaround Time (TAT)",
            data: turnaroundTimes,
            backgroundColor: "rgba(105, 215, 176, 0.8)",
            borderColor: "#69D7B0",
            borderWidth: 1,
            borderRadius: 4,
          },
          {
            label: "Response Time (RT)",
            data: responseTimes,
            backgroundColor: "rgba(255, 203, 107, 0.8)",
            borderColor: "#FFCB6B",
            borderWidth: 1,
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: THEME.textColor,
              font: { family: THEME.fontFamily, size: 12 },
            },
          },
          tooltip: {
            backgroundColor: "#101728",
            titleColor: THEME.textColor,
            bodyColor: THEME.textColor,
            borderColor: "#293750",
            borderWidth: 1,
          },
        },
        scales: {
          x: {
            grid: { color: THEME.gridColor },
            ticks: { color: THEME.secondaryTextColor, font: { family: THEME.fontFamily } },
          },
          y: {
            beginAtZero: true,
            grid: { color: THEME.gridColor },
            ticks: { color: THEME.secondaryTextColor, font: { family: THEME.fontFamily } },
            title: {
              display: true,
              text: "Time Units",
              color: THEME.secondaryTextColor,
            },
          },
        },
      },
    });
  }

  function renderComparisonChart(canvasId, comparisonData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !window.Chart) return;

    if (comparisonChart) {
      comparisonChart.destroy();
      comparisonChart = null;
    }

    if (!comparisonData || !comparisonData.algorithms) return;

    const algos = comparisonData.algorithms;
    const algoKeys = Object.keys(algos);
    const labels = algoKeys.map((k) => algos[k].name);

    const avgWT = algoKeys.map((k) => algos[k].metrics.average_waiting_time);
    const avgTAT = algoKeys.map((k) => algos[k].metrics.average_turnaround_time);
    const avgRT = algoKeys.map((k) => algos[k].metrics.average_response_time);
    const cpuUtil = algoKeys.map((k) => algos[k].metrics.cpu_utilization);

    const ctx = canvas.getContext("2d");
    comparisonChart = new window.Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Avg Waiting Time",
            data: avgWT,
            backgroundColor: "rgba(130, 170, 255, 0.8)",
            borderColor: "#82AAFF",
            borderWidth: 1,
            borderRadius: 4,
          },
          {
            label: "Avg Turnaround Time",
            data: avgTAT,
            backgroundColor: "rgba(105, 215, 176, 0.8)",
            borderColor: "#69D7B0",
            borderWidth: 1,
            borderRadius: 4,
          },
          {
            label: "Avg Response Time",
            data: avgRT,
            backgroundColor: "rgba(255, 203, 107, 0.8)",
            borderColor: "#FFCB6B",
            borderWidth: 1,
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: THEME.textColor,
              font: { family: THEME.fontFamily, size: 12 },
            },
          },
          tooltip: {
            backgroundColor: "#101728",
            titleColor: THEME.textColor,
            bodyColor: THEME.textColor,
            borderColor: "#293750",
            borderWidth: 1,
            callbacks: {
              afterBody: (context) => {
                const dataIndex = context[0].dataIndex;
                return `CPU Utilization: ${cpuUtil[dataIndex]}%`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: { color: THEME.gridColor },
            ticks: { color: THEME.secondaryTextColor, font: { family: THEME.fontFamily } },
          },
          y: {
            beginAtZero: true,
            grid: { color: THEME.gridColor },
            ticks: { color: THEME.secondaryTextColor, font: { family: THEME.fontFamily } },
            title: {
              display: true,
              text: "Average Time Units",
              color: THEME.secondaryTextColor,
            },
          },
        },
      },
    });
  }

  return {
    renderProcessChart,
    renderComparisonChart,
  };
})();

window.AppCharts = AppCharts;
