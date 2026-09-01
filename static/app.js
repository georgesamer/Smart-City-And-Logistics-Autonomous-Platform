const apiBase = "/api/v1";

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
const etaValue = document.getElementById("etaValue");
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
  etaValue.textContent = dispatch?.eta_minutes ? `${dispatch.eta_minutes} min` : "--";

  if (dispatch?.status === "SUCCESS") {
    resultSummary.innerHTML = `
      <p><strong>Assigned vehicle:</strong> ${dispatch.vehicle_assigned ?? "N/A"}</p>
      <p><strong>Priority:</strong> ${dispatch.priority ?? "N/A"}</p>
      <p><strong>Distance:</strong> ${dispatch.distance_km ?? "N/A"} km</p>
    `;
    return;
  }

  resultSummary.innerHTML = "<p>No valid dispatch summary available.</p>";
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

    dispatchOutput.textContent = JSON.stringify(result, null, 2);
    renderSummary(data);

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

document.getElementById("runDispatchBtn").addEventListener("click", runDispatch);
document.getElementById("dispatchForm").addEventListener("submit", handleSubmit);

setStatus("Ready", "idle", "System ready for the next dispatch scenario.");
resultSummary.innerHTML = "<p>Load a scenario and trigger the dispatch run.</p>";
dispatchOutput.textContent = '{ "status": "idle" }';
