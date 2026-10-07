const photoInput = document.getElementById("photo");
const preview = document.getElementById("preview");
const previewWrap = document.getElementById("preview-wrap");
const analyzeBtn = document.getElementById("analyze-btn");
const statusEl = document.getElementById("status");
const resultPanel = document.getElementById("result-panel");
const resultContent = document.getElementById("result-content");
const saveBtn = document.getElementById("save-btn");
const againBtn = document.getElementById("again-btn");
const modeBanner = document.getElementById("mode-banner");
const statsPill = document.getElementById("stats-pill");

let current = null;

async function refreshStats() {
  try {
    const response = await fetch("/api/stats");
    if (!response.ok) return;
    const stats = await response.json();
    statsPill.textContent = `★ ${stats.total_xp} XP · Lv ${stats.level}`;
  } catch {}
}

async function refreshMode() {
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    if (data.mode === "demo") {
      modeBanner.textContent =
        "ONLINE DEMO MODE · Full Local AI runs with Ollama + Qwen3-VL 2B on your computer.";
    } else if (data.ollama?.connected && data.ollama?.model_ready) {
      modeBanner.textContent = "LOCAL AI READY · Ollama + Qwen3-VL 2B";
    } else {
      modeBanner.textContent =
        "LOCAL AI · Start Ollama to analyze photos with Qwen3-VL 2B.";
    }
  } catch {
    modeBanner.textContent = "Local-first AI · Ollama + Qwen3-VL 2B";
  }
}

function showPhoto(file) {
  if (!file) return;

  if (!file.type || !file.type.startsWith("image/")) {
    statusEl.textContent = "Please choose an image.";
    photoInput.value = "";
    analyzeBtn.disabled = true;
    return;
  }

  const objectUrl = URL.createObjectURL(file);
  preview.onload = () => URL.revokeObjectURL(objectUrl);
  preview.src = objectUrl;
  previewWrap.classList.remove("hidden");
  analyzeBtn.disabled = false;
  statusEl.textContent = "Photo ready. Click Analyze Discovery.";
  resultPanel.classList.add("hidden");
}

function showPhoto(file) {
  if (!file) return;

  if (file.type && !file.type.startsWith("image/")) {
    statusEl.textContent = "Please choose an image.";
    photoInput.value = "";
    analyzeBtn.disabled = true;
    return;
  }

  const objectUrl = URL.createObjectURL(file);
  preview.onload = () => URL.revokeObjectURL(objectUrl);
  preview.src = objectUrl;
  previewWrap.classList.remove("hidden");
  analyzeBtn.disabled = false;
  statusEl.textContent = "Photo ready. Click Analyze Discovery.";
  resultPanel.classList.add("hidden");
}

photoInput.addEventListener("change", () => {
  showPhoto(photoInput.files?.[0]);
});

document.getElementById("start-btn").addEventListener("click", () => {
  document.getElementById("explore").scrollIntoView({ behavior: "smooth" });
});

analyzeBtn.addEventListener("click", async () => {
  const file = photoInput.files?.[0];
  if (!file) {
    statusEl.textContent = "Take or choose a photo first.";
    return;
  }

  analyzeBtn.disabled = true;
  statusEl.classList.remove("error");
  statusEl.textContent =
    "Uploading your photo and looking closely at your discovery…";
  resultPanel.classList.add("hidden");

  const form = new FormData();
  form.append("file", file, file.name || "nature-photo.jpg");

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: form,
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Upload or analysis failed.");
    }

    current = data;
    renderResult(data);
    resultPanel.classList.remove("hidden");
    resultPanel.scrollIntoView({ behavior: "smooth" });
    statusEl.classList.remove("error");
    statusEl.textContent =
      data.mode === "demo"
        ? "Demo result generated. Full Local AI runs with Ollama + Qwen3-VL 2B on your computer."
        : "Photo analyzed successfully.";
  } catch (error) {
    const status = error && error.status;
    statusEl.classList.add("error");

    if (status === 422) {
      statusEl.textContent =
        "🌿 Not related to the environment. " +
        (error.message || "Please point the camera at a natural subject.");
    } else if (status === 503) {
      statusEl.textContent =
        "Local AI is unavailable. Start Ollama on the computer running TrailLens.";
    } else {
      statusEl.textContent =
        (error && error.message) || "Could not upload or analyze the photo.";
    }
  } finally {
    analyzeBtn.disabled = false;
  }
});

function renderResult(data) {
  const result = data.result || {};
  const facts = Array.isArray(result.facts) ? result.facts : [];
  const demoBadge =
    data.mode === "demo" ? '<span class="badge">DEMO</span>' : "";

  resultContent.innerHTML = `
    <div class="discovery-head">
      <span class="badge">${escapeHtml(result.category)}</span>
      <span class="badge confidence">${escapeHtml(result.confidence)}</span>
      ${demoBadge}
    </div>
    <h2 class="discovery-title">${escapeHtml(result.name)}</h2>
    <p class="muted">${escapeHtml(result.description)}</p>
    <h3>Interesting facts</h3>
    <ul class="fact-list">
      ${facts.map((fact) => `<li>${escapeHtml(fact)}</li>`).join("")}
    </ul>
    <div class="challenge">
      <strong>🎯 Your next outdoor challenge</strong>
      ${escapeHtml(result.outdoor_challenge)}
    </div>
    <div class="xp">+ ${Number(data.xp?.xp_awarded || 0)} XP</div>
  `;
}

saveBtn.addEventListener("click", async () => {
  if (!current) return;

  saveBtn.disabled = true;
  try {
    const response = await fetch("/api/discoveries", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        result: current.result,
        upload_path: current.upload_path,
        xp_awarded: current.xp?.xp_awarded,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Could not save discovery.");
    }

    statusEl.textContent =
      `Saved! +${data.xp_awarded} XP added to your journal.`;
    saveBtn.textContent = "Saved ✓";
    refreshStats();
  } catch (error) {
    statusEl.textContent = error.message || "Could not save discovery.";
  } finally {
    saveBtn.disabled = false;
  }
});

againBtn.addEventListener("click", () => {
  photoInput.value = "";
  preview.src = "";
  previewWrap.classList.add("hidden");
  resultPanel.classList.add("hidden");
  analyzeBtn.disabled = true;
  saveBtn.textContent = "Save Discovery";
  statusEl.textContent = "";
  current = null;
});

function escapeHtml(value) {
  const replacements = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  };
  return String(value ?? "").replace(/[&<>"']/g, (character) => replacements[character]);
}

refreshStats();
refreshMode();
