const apiBase = "/api/v1";
let lastDispatchResult = null;
let gridSize = 5;
let vehicleStart = [3, 0];
let incidentLocation = [0, 4];
let routePath = [];

const fields = {
  incidentId: document.getElementById("incidentId"),
  currentHour: document.getElementById("currentHour"),
  reportInput: document.getElementById("reportInput"),
  cameraImage: document.getElementById("cameraImage"),
};

const statusPanel = document.getElementById("statusPanel");
const resultSummary = document.getElementById("resultSummary");
const dispatchOutput = document.getElementById("dispatchOutput");
const riskLevel = document.getElementById("riskLevel");
const costValue = document.getElementById("costValue");
const incidentCount = document.getElementById("incidentCount");
const fleetCount = document.getElementById("fleetCount");

function setStatus(label, kind, message) {
  statusPanel.innerHTML = `
    <div class="status-pill ${kind}">${label}</div>
    <p>${message}</p>
  `;
}

function renderSummary(data) {
  const dispatch = data?.dispatch ?? {};
  const risk = data?.risk ?? {};

  incidentCount.textContent = dispatch?.incident_id ? "1" : "0";
  fleetCount.textContent = Array.isArray(dispatch?.vehicles) ? String(dispatch.vehicles.length) : "2";
  riskLevel.textContent = risk?.risk_level ?? "--";
  costValue.textContent = dispatch?.cost ?? "--";

  if (dispatch?.status === "SUCCESS") {
    resultSummary.innerHTML = `
      <p><strong>Assigned vehicle:</strong> ${dispatch.vehicle_assigned ?? "N/A"}</p>
      <p><strong>Route cost:</strong> ${dispatch.cost ?? "N/A"} units</p>
      <p><strong>Delay probability:</strong> ${risk?.delay_probability ? (risk.delay_probability * 100).toFixed(1) + "%" : "N/A"}</p>
    `;
    return;
  }

  resultSummary.innerHTML = "<p>No valid dispatch summary available.</p>";
}

function drawMap() {
  const canvas = document.getElementById("mapCanvas");
  if (!canvas) return;
  
  const ctx = canvas.getContext("2d");
  const cellSize = canvas.width / gridSize;
  const gridColor = "rgba(148, 163, 184, 0.1)";
  const gridLineColor = "rgba(148, 163, 184, 0.2)";

  // Clear canvas
  ctx.fillStyle = "rgba(10, 20, 35, 0.8)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Draw grid
  ctx.strokeStyle = gridLineColor;
  ctx.lineWidth = 1;
  for (let i = 0; i <= gridSize; i++) {
    const pos = i * cellSize;
    ctx.beginPath();
    ctx.moveTo(pos, 0);
    ctx.lineTo(pos, canvas.height);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, pos);
    ctx.lineTo(canvas.width, pos);
    ctx.stroke();
  }

  // Draw route path
  if (routePath.length > 0) {
    ctx.strokeStyle = "rgba(78, 161, 255, 0.6)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    const [startX, startY] = routePath[0];
    ctx.moveTo(startX * cellSize + cellSize / 2, startY * cellSize + cellSize / 2);
    for (let i = 1; i < routePath.length; i++) {
      const [x, y] = routePath[i];
      ctx.lineTo(x * cellSize + cellSize / 2, y * cellSize + cellSize / 2);
    }
    ctx.stroke();
  }

  // Draw waypoints
  if (routePath.length > 0) {
    ctx.fillStyle = "rgba(78, 161, 255, 0.3)";
    for (let i = 1; i < routePath.length - 1; i++) {
      const [x, y] = routePath[i];
      ctx.beginPath();
      ctx.arc(x * cellSize + cellSize / 2, y * cellSize + cellSize / 2, 6, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // Draw incident (red marker)
  ctx.fillStyle = "#ff6b7d";
  ctx.beginPath();
  ctx.arc(
    incidentLocation[0] * cellSize + cellSize / 2,
    incidentLocation[1] * cellSize + cellSize / 2,
    12,
    0,
    Math.PI * 2
  );
  ctx.fill();
  ctx.strokeStyle = "#ff6b7d";
  ctx.lineWidth = 2;
  ctx.stroke();

  // Draw vehicle (green marker with glow)
  ctx.fillStyle = "#37d39a";
  ctx.beginPath();
  ctx.arc(
    vehicleStart[0] * cellSize + cellSize / 2,
    vehicleStart[1] * cellSize + cellSize / 2,
    10,
    0,
    Math.PI * 2
  );
  ctx.fill();
  ctx.strokeStyle = "#37d39a";
  ctx.lineWidth = 2;
  ctx.stroke();
}

function renderRouteDetails() {
  const tbody = document.getElementById("routeDetails");
  if (!routePath || routePath.length === 0) {
    tbody.innerHTML = '<tr><td colspan="2" style="text-align:center; color: var(--muted);">No route calculated yet</td></tr>';
    return;
  }
  let html = `
    <tr><td><strong>Start Location</strong></td><td>${JSON.stringify(routePath[0])}</td></tr>
    <tr><td><strong>End Location</strong></td><td>${JSON.stringify(routePath[routePath.length - 1])}</td></tr>
    <tr><td><strong>Total Steps</strong></td><td>${routePath.length - 1}</td></tr>
    <tr><td><strong>Route Cost</strong></td><td>${lastDispatchResult?.data?.cost ?? "--"} units</td></tr>
  `;
  if (routePath.length <= 10) {
    html += `<tr><td colspan="2"><strong>Full Path:</strong> ${routePath.map(p => `[${p[0]},${p[1]}]`).join(" → ")}</td></tr>`;
  }
  tbody.innerHTML = html;
}

function renderFleetTable(dispatch) {
  const tbody = document.getElementById("fleetTable");
  const vehicles = dispatch?.vehicles ?? [];
  if (vehicles.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: var(--muted);">No vehicle data available</td></tr>';
    return;
  }
  let html = "";
  vehicles.forEach((v) => {
    html += `
      <tr>
        <td>${v.vehicle_id}</td>
        <td>[${v.location[0]},${v.location[1]}]</td>
        <td>${v.battery_level?.toFixed(1) ?? "--"}%</td>
        <td>${v.capacity?.toFixed(1) ?? "--"} u</td>
        <td>${v.vehicle_id === dispatch.vehicle_assigned ? '<span style="color: var(--green); font-weight: 600;">ASSIGNED</span>' : 'Available'}</td>
      </tr>
    `;
  });
  tbody.innerHTML = html;
}

function renderAssignedVehicle(dispatch) {
  const tbody = document.getElementById("assignedVehicleTable");
  if (!dispatch?.vehicle_assigned) {
    tbody.innerHTML = '<tr><td colspan="2" style="text-align:center; color: var(--muted);">No vehicle assigned yet</td></tr>';
    return;
  }
  const assigned = dispatch.vehicles?.find((v) => v.vehicle_id === dispatch.vehicle_assigned);
  if (!assigned) {
    tbody.innerHTML = `<tr><td>Vehicle ID</td><td>${dispatch.vehicle_assigned}</td></tr>`;
    return;
  }
  tbody.innerHTML = `
    <tr><td><strong>Vehicle ID</strong></td><td>${assigned.vehicle_id}</td></tr>
    <tr><td><strong>Current Location</strong></td><td>[${assigned.location[0]},${assigned.location[1]}]</td></tr>
    <tr><td><strong>Battery Level</strong></td><td>${assigned.battery_level?.toFixed(1) ?? "--"}%</td></tr>
    <tr><td><strong>Capacity</strong></td><td>${assigned.capacity?.toFixed(1) ?? "--"} units</td></tr>
  `;
}

function renderAnalytics(result) {
  const risk = result?.risk ?? {};
  const dispatch = result?.dispatch ?? {};

  // Risk bar
  const riskPercent = Math.min(100, Math.max(0, (risk.delay_probability || 0) * 100));
  const riskFill = document.getElementById("riskFill");
  if (riskFill) riskFill.style.width = riskPercent + "%";

  const riskText = document.getElementById("riskText");
  if (riskText) riskText.textContent = `${riskPercent.toFixed(1)}% (${risk.risk_level || "Unknown"})`;

  // Efficiency
  const efficiencyValue = document.getElementById("efficiencyValue");
  if (efficiencyValue) efficiencyValue.textContent = dispatch.cost ?? "--";

  // Probability gauge
  const probabilityGauge = document.getElementById("probabilityGauge");
  if (probabilityGauge) probabilityGauge.textContent = `${riskPercent.toFixed(1)}%`;

  // Weather impact
  const weatherImpact = document.getElementById("weatherImpact");
  if (weatherImpact) {
    weatherImpact.innerHTML = `
      <p><strong>Weather:</strong> ${risk.weather_condition || "Clear"}</p>
      <p><strong>Traffic:</strong> ${risk.traffic_condition || "Light"}</p>
      <p><strong>Base Delay Probability:</strong> ${(risk.delay_probability * 100).toFixed(1)}%</p>
    `;
  }
}

async function runDispatch() {
  const payload = {
    report: fields.reportInput.value,
    incident_id: fields.incidentId.value || "INC_001",
    camera_image_mock: fields.cameraImage.value || "camera_feed_accident_block.png",
    current_hour: Number(fields.currentHour.value || 14),
  };

  setStatus("Running", "idle", "Analyzing the incident and dispatching nearby vehicles...");

  try {
    const response = await fetch(`${apiBase}/dispatch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }

    const result = await response.json();
    const data = result.data || {};
    lastDispatchResult = result;

    dispatchOutput.textContent = JSON.stringify(result, null, 2);

    // Extract route path from dispatch data
    if (data.path && Array.isArray(data.path)) {
      routePath = data.path;
    }

    renderSummary({ dispatch: data, risk: {} });
    drawMap();
    renderRouteDetails();
    renderFleetTable(data);
    renderAssignedVehicle(data);

    if (data.status === "SUCCESS") {
      setStatus("Success", "success", "The nearest suitable vehicle is on route.");
    } else {
      setStatus("Alert", "error", "The dispatch pipeline returned a warning state.");
    }

    const riskResponse = await fetch(`${apiBase}/assess-risk`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ weather_severe: false, traffic_heavy: true }),
    });

    if (riskResponse.ok) {
      const riskResult = await riskResponse.json();
      const riskData = riskResult.data || {};
      riskLevel.textContent = riskData.risk_level || riskLevel.textContent;
      renderAnalytics({ dispatch: data, risk: riskData });
    }
  } catch (error) {
    console.error(error);
    setStatus("Error", "error", "Unable to complete the dispatch request.");
    dispatchOutput.textContent = JSON.stringify({ error: error.message }, null, 2);
  }
}

async function handleSubmit(event) {
  event.preventDefault();
  await runDispatch();
}

function initTabs() {
  document.querySelectorAll(".nav-item[data-tab]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const tabName = btn.dataset.tab;
      // Hide all tabs
      document.querySelectorAll(".tab-content").forEach((tab) => {
        tab.classList.remove("active");
      });
      // Show selected tab
      const selectedTab = document.getElementById(`${tabName}-tab`);
      if (selectedTab) {
        selectedTab.classList.add("active");
      }
      // Update nav active state
      document.querySelectorAll(".nav-item[data-tab]").forEach((n) => {
        n.classList.remove("active");
      });
      btn.classList.add("active");
      // Redraw map when map tab is shown
      if (tabName === "map") {
        setTimeout(() => drawMap(), 100);
      }
    });
  });
}

document.getElementById("runDispatchBtn").addEventListener("click", runDispatch);
document.getElementById("dispatchForm").addEventListener("submit", handleSubmit);

initTabs();
setStatus("Ready", "idle", "System ready for the next dispatch scenario.");
resultSummary.innerHTML = "<p>Load a scenario and trigger the dispatch run.</p>";
dispatchOutput.textContent = '{ "status": "idle" }';
drawMap();
