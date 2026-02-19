/**
 * MedAnalyze AI — Frontend Application
 * Vanilla JavaScript, Fetch API, no frameworks
 * Production-grade with error handling and async patterns
 */

'use strict';

// ── Configuration ────────────────────────────────────────────────
const API_BASE = window.location.origin;
let currentReportId = null;
let historyPage = 1;
const PER_PAGE = 20;

// ── DOM Ready ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  init3DTiltEffect();
  initUploadZone();
  initSidebar();
  checkSystemHealth();
  loadHistory();
});

// ── Navigation ────────────────────────────────────────────────────
function initNavigation() {
  const SECTION_TITLES = {
    upload:  ['Upload Medical Report', 'AI-powered entity extraction · Non-diagnostic'],
    results: ['Analysis Results', 'Structured medical insights · Non-diagnostic'],
    history: ['Analysis History', 'All previously analyzed reports'],
    docs:    ['API Documentation', 'Endpoints and cURL examples'],
  };

  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      const section = btn.dataset.section;
      switchSection(section);

      // Close sidebar on mobile
      if (window.innerWidth <= 768) {
        document.getElementById('sidebar').classList.remove('open');
      }
    });
  });
}

function switchSection(name) {
  // Update nav items
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.section === name);
  });

  // Show section
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  const target = document.getElementById(`section-${name}`);
  if (target) target.classList.add('active');

  // Update header text
  const titles = {
    upload:  ['Upload Medical Report', 'AI-powered entity extraction · Non-diagnostic'],
    results: ['Analysis Results', 'Structured medical insights · Non-diagnostic'],
    history: ['Analysis History', 'All previously analyzed reports'],
    docs:    ['API Documentation', 'Endpoints and cURL examples'],
  };
  if (titles[name]) {
    document.getElementById('pageTitle').textContent = titles[name][0];
    document.getElementById('pageSubtitle').textContent = titles[name][1];
  }

  // Load history on switch
  if (name === 'history') loadHistory();
}

// Make available globally for inline onclick
window.switchSection = switchSection;

// ── Mobile Sidebar ─────────────────────────────────────────────
function initSidebar() {
  const hamburger = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  hamburger?.addEventListener('click', () => sidebar.classList.toggle('open'));
  document.addEventListener('click', e => {
    if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });
}

// ── 3D Tilt Effect ─────────────────────────────────────────────
function init3DTiltEffect() {
  const applyTilt = (el) => {
    el.addEventListener('mousemove', (e) => {
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const cx = rect.width / 2;
      const cy = rect.height / 2;
      const rotateY = ((x - cx) / cx) * 8;
      const rotateX = -((y - cy) / cy) * 8;
      el.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
    });
    el.addEventListener('mouseleave', () => {
      el.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg) scale(1)';
    });
  };

  document.querySelectorAll('.tilt-card').forEach(applyTilt);

  // Observe new tilt cards added dynamically
  const observer = new MutationObserver((mutations) => {
    mutations.forEach(m => {
      m.addedNodes.forEach(node => {
        if (node.nodeType === 1) {
          if (node.classList?.contains('tilt-card')) applyTilt(node);
          node.querySelectorAll?.('.tilt-card').forEach(applyTilt);
        }
      });
    });
  });
  observer.observe(document.body, { childList: true, subtree: true });
}

// ── Upload Zone ─────────────────────────────────────────────────
function initUploadZone() {
  const dropZone    = document.getElementById('dropZone');
  const fileInput   = document.getElementById('fileInput');
  const browseBtn   = document.getElementById('browseBtn');
  const filePreview = document.getElementById('filePreview');
  const analyzeBtn  = document.getElementById('analyzeBtn');
  const removeBtn   = document.getElementById('fileRemoveBtn');

  let selectedFile = null;

  // Browse button
  browseBtn.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('click', (e) => {
    if (!e.target.closest('.btn')) fileInput.click();
  });

  // File input change
  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) handleFileSelect(fileInput.files[0]);
  });

  // Drag & Drop
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragging');
  });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragging'));
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragging');
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  });

  // Remove file
  removeBtn.addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    dropZone.hidden = false;
    filePreview.hidden = true;
  });

  // Analyze
  analyzeBtn.addEventListener('click', () => {
    if (selectedFile) analyzeFile(selectedFile);
  });

  function handleFileSelect(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['txt', 'pdf'].includes(ext)) {
      showToast('Only .txt and .pdf files are supported', 'error');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      showToast('File exceeds 10MB limit', 'error');
      return;
    }

    selectedFile = file;
    document.getElementById('previewFileName').textContent = file.name;
    document.getElementById('previewFileSize').textContent = formatBytes(file.size);
    document.getElementById('fileIconType').textContent = ext === 'pdf' ? '📕' : '📄';

    dropZone.hidden = true;
    filePreview.hidden = false;
  }
}

// ── Analyze File ────────────────────────────────────────────────
async function analyzeFile(file) {
  const progressContainer = document.getElementById('progressContainer');
  const analyzeBtn = document.getElementById('analyzeBtn');

  // Show progress
  progressContainer.hidden = false;
  analyzeBtn.disabled = true;
  analyzeBtn.innerHTML = '<div class="spinner"></div> Analyzing...';

  setProgress(10, 'Reading file...', 'step1');
  await delay(400);
  setProgress(25, 'Sending to AI...', 'step2');

  const formData = new FormData();
  formData.append('file', file);

  try {
    setProgress(40, 'AI is analyzing the transcription...', 'step2');

    const res = await fetch(`${API_BASE}/api/v1/reports/upload`, {
      method: 'POST',
      body: formData,
    });

    setProgress(80, 'Processing response...', 'step2');
    await delay(300);

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Server error ${res.status}`);
    }

    const data = await res.json();
    setProgress(95, 'Saving results...', 'step3');
    await delay(300);
    setProgress(100, 'Complete!', 'step3');
    await delay(400);

    currentReportId = data.id;
    renderResults(data);
    switchSection('results');
    showToast('Analysis complete!', 'success');

  } catch (err) {
    showToast(`Analysis failed: ${err.message}`, 'error');
    console.error('Analysis error:', err);
  } finally {
    progressContainer.hidden = true;
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = `
      <svg viewBox="0 0 20 20" fill="currentColor"><path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z"/></svg>
      Analyze with AI`;
    resetProgress();
  }
}

// ── Render Results ───────────────────────────────────────────────
function renderResults(data) {
  const resultsEmpty   = document.getElementById('resultsEmpty');
  const resultsContent = document.getElementById('resultsContent');

  resultsEmpty.hidden   = true;
  resultsContent.hidden = false;

  // Stats Row
  const statsRow = document.getElementById('statsRow');
  statsRow.innerHTML = '';

  const stats = [
    { label: 'Specialty', value: data.specialty_classification || 'N/A', delay: 0 },
    { label: 'Confidence', value: formatConfidence(data.confidence_score), delay: 1 },
    { label: 'Risk Flags', value: (data.risk_flags?.length || 0), delay: 2 },
    { label: 'Entities Found', value: countEntities(data), delay: 3 },
    { label: 'Processing', value: data.cached ? '⚡ Cached' : `${Math.round(data.processing_time_ms || 0)}ms`, delay: 4 },
  ];

  stats.forEach((s, i) => {
    const card = document.createElement('div');
    card.className = 'glass-card stat-card tilt-card';
    card.style.animationDelay = `${i * 0.08}s`;
    card.innerHTML = `
      <div class="stat-label">${s.label}</div>
      <div class="stat-value">${s.value}</div>
    `;
    statsRow.appendChild(card);
  });

  // Confidence bar special card
  if (data.confidence_score != null) {
    const confCard = statsRow.querySelector('.stat-card:nth-child(2)');
    if (confCard) {
      const pct = Math.round((data.confidence_score || 0) * 100);
      confCard.innerHTML += `
        <div class="confidence-bar-wrap">
          <div class="confidence-track">
            <div class="confidence-fill" style="width: 0%" data-target="${pct}%"></div>
          </div>
          <span class="confidence-label">${pct}%</span>
        </div>`;
      // Animate after render
      setTimeout(() => {
        const fill = confCard.querySelector('.confidence-fill');
        if (fill) fill.style.width = fill.dataset.target;
      }, 100);
    }
  }

  // Risk Flags
  const riskContainer = document.getElementById('riskContainer');
  const riskFlags     = document.getElementById('riskFlags');
  if (data.risk_flags?.length > 0) {
    riskContainer.hidden = false;
    riskFlags.innerHTML = data.risk_flags.map(f =>
      `<span class="risk-flag">⚠ ${escapeHtml(f)}</span>`
    ).join('');
  } else {
    riskContainer.hidden = true;
  }

  // Entity Grid
  const entityGrid = document.getElementById('entityGrid');
  entityGrid.innerHTML = '';

  const entities = [
    { icon: '🤒', title: 'Symptoms',       items: data.symptoms },
    { icon: '💊', title: 'Medications',    items: data.medications },
    { icon: '🔬', title: 'Procedures',     items: data.procedures },
    { icon: '🧪', title: 'Lab Values',     items: data.lab_values },
    { icon: '🫀', title: 'Body Parts',     items: data.body_parts },
    { icon: '👤', title: 'Patient Info',   items: null, custom: renderPatientInfo(data) },
    { icon: '🏥', title: 'Clinical Impression', items: null, text: data.clinical_impression },
  ];

  entities.forEach((e, i) => {
    const card = document.createElement('div');
    card.className = 'glass-card entity-card tilt-card';
    card.style.animationDelay = `${i * 0.05}s`;

    let content = '';
    if (e.custom) {
      content = e.custom;
    } else if (e.text) {
      content = `<p class="entity-text">${escapeHtml(e.text || 'Not specified')}</p>`;
    } else if (e.items?.length > 0) {
      content = `<div class="entity-tags">${
        e.items.map(item => `<span class="entity-tag">${escapeHtml(item)}</span>`).join('')
      }</div>`;
    } else {
      content = '<p class="entity-empty">Not identified in report</p>';
    }

    card.innerHTML = `
      <div class="entity-card-header">
        <div class="entity-icon">${e.icon}</div>
        <span class="entity-title">${e.title}</span>
      </div>
      ${content}
    `;
    entityGrid.appendChild(card);
  });

  // Summary Grid
  const summaryGrid = document.getElementById('summaryGrid');
  summaryGrid.innerHTML = `
    <div class="glass-card summary-card summary-professional tilt-card">
      <h3 class="card-title">🩺 Professional Summary</h3>
      <p class="summary-text">${escapeHtml(data.professional_summary || 'No professional summary available.')}</p>
    </div>
    <div class="glass-card summary-card summary-friendly tilt-card">
      <h3 class="card-title">💬 Patient-Friendly Explanation</h3>
      <p class="summary-text">${escapeHtml(data.patient_friendly_summary || 'No patient explanation available.')}</p>
    </div>
  `;

  // Export button
  const exportBtn = document.getElementById('exportBtn');
  exportBtn.onclick = () => exportReport(data.id);

  // New analysis button
  document.getElementById('newAnalysisBtn').onclick = () => {
    switchSection('upload');
    document.getElementById('dropZone').hidden = false;
    document.getElementById('filePreview').hidden = true;
    document.getElementById('fileInput').value = '';
  };
}

function renderPatientInfo(data) {
  const age    = data.patient_age    || 'Unknown';
  const gender = data.patient_gender || 'Unknown';
  return `
    <div class="entity-tags">
      <span class="entity-tag">Age: ${escapeHtml(age)}</span>
      <span class="entity-tag">Gender: ${escapeHtml(gender)}</span>
    </div>
  `;
}

// ── Export Report ────────────────────────────────────────────────
async function exportReport(reportId) {
  try {
    const res = await fetch(`${API_BASE}/api/v1/reports/${reportId}/export`);
    if (!res.ok) throw new Error(`Export failed: ${res.status}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `medical_analysis_${reportId.slice(0, 8)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Analysis exported as JSON', 'success');
  } catch (err) {
    showToast(`Export failed: ${err.message}`, 'error');
  }
}

// ── History ──────────────────────────────────────────────────────
async function loadHistory(page = 1) {
  historyPage = page;
  const tbody = document.getElementById('historyBody');
  tbody.innerHTML = '<tr><td colspan="7" class="table-empty">Loading...</td></tr>';

  try {
    const res = await fetch(`${API_BASE}/api/v1/reports?page=${page}&per_page=${PER_PAGE}`);
    if (!res.ok) throw new Error(`Failed to load history: ${res.status}`);
    const data = await res.json();

    if (data.items.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="table-empty">No reports analyzed yet. Upload one to get started!</td></tr>';
      document.getElementById('pagination').innerHTML = '';
      return;
    }

    tbody.innerHTML = data.items.map(r => `
      <tr data-id="${r.id}" onclick="viewReport('${r.id}')">
        <td style="font-weight:500;color:var(--text-primary)">${escapeHtml(r.filename)}</td>
        <td>${r.specialty_classification ? `<span style="color:var(--accent-cyan)">${escapeHtml(r.specialty_classification)}</span>` : '<span style="color:var(--text-muted)">—</span>'}</td>
        <td><span class="badge badge-${r.status}">${r.status}</span></td>
        <td>
          <div style="display:flex;align-items:center;gap:0.5rem">
            <div class="confidence-track" style="width:60px">
              <div class="confidence-fill" style="width:${Math.round((r.confidence_score||0)*100)}%"></div>
            </div>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:var(--accent-emerald)">
              ${Math.round((r.confidence_score || 0) * 100)}%
            </span>
          </div>
        </td>
        <td>${r.risk_flags?.length > 0 
          ? `<span style="color:var(--accent-rose);font-weight:600">⚠ ${r.risk_flags.length} flag${r.risk_flags.length > 1 ? 's' : ''}</span>`
          : '<span style="color:var(--accent-emerald)">✓ Clear</span>'
        }</td>
        <td style="color:var(--text-muted);font-size:0.8rem">${formatDate(r.created_at)}</td>
        <td>
          <div style="display:flex;gap:0.5rem">
            <button class="btn btn-sm btn-outline" onclick="event.stopPropagation();viewReport('${r.id}')">View</button>
            <button class="btn btn-sm btn-outline" onclick="event.stopPropagation();exportReport('${r.id}')" style="color:var(--accent-amber);border-color:rgba(245,158,11,0.3)">Export</button>
          </div>
        </td>
      </tr>
    `).join('');

    // Pagination
    renderPagination(data.page, data.pages);

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="table-empty" style="color:var(--accent-rose)">Error: ${escapeHtml(err.message)}</td></tr>`;
  }
}

window.viewReport = async (reportId) => {
  try {
    showToast('Loading report...', 'info');
    const res = await fetch(`${API_BASE}/api/v1/reports/${reportId}`);
    if (!res.ok) throw new Error(`Failed to load report ${reportId}`);
    const data = await res.json();
    currentReportId = data.id;
    renderResults(data);
    switchSection('results');
  } catch (err) {
    showToast(`Failed to load report: ${err.message}`, 'error');
  }
};

function renderPagination(page, pages) {
  const pag = document.getElementById('pagination');
  if (pages <= 1) { pag.innerHTML = ''; return; }

  let html = '';
  for (let p = 1; p <= pages; p++) {
    html += `<button class="page-btn ${p === page ? 'active' : ''}" onclick="loadHistory(${p})">${p}</button>`;
  }
  pag.innerHTML = html;
}

document.getElementById('refreshHistoryBtn')?.addEventListener('click', () => loadHistory(historyPage));

// ── System Health ─────────────────────────────────────────────────
async function checkSystemHealth() {
  const statusEl = document.getElementById('systemStatus');
  try {
    const res = await fetch(`${API_BASE}/api/v1/health`);
    const data = res.ok ? await res.json() : null;
    const healthy = data?.status === 'healthy';
    statusEl.querySelector('.status-dot').className = `status-dot ${healthy ? 'healthy' : 'unhealthy'}`;
    statusEl.querySelector('span').textContent = healthy ? 'System Healthy' : 'Degraded';
  } catch {
    statusEl.querySelector('.status-dot').className = 'status-dot unhealthy';
    statusEl.querySelector('span').textContent = 'Offline';
  }

  // Recheck every 60s
  setTimeout(checkSystemHealth, 60000);
}

// ── Progress Helpers ─────────────────────────────────────────────
function setProgress(pct, label, activeStep) {
  document.getElementById('progressBar').style.width = `${pct}%`;
  document.getElementById('progressPercent').textContent = `${pct}%`;
  document.getElementById('progressLabel').textContent = label;

  ['step1', 'step2', 'step3'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const idx = ['step1', 'step2', 'step3'].indexOf(id);
    const activeIdx = ['step1', 'step2', 'step3'].indexOf(activeStep);
    el.className = 'step' + (idx < activeIdx ? ' done' : idx === activeIdx ? ' active' : '');
  });
}

function resetProgress() {
  document.getElementById('progressBar').style.width = '0%';
  document.getElementById('progressPercent').textContent = '0%';
  document.getElementById('progressLabel').textContent = 'Extracting text...';
  ['step1', 'step2', 'step3'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.className = 'step';
  });
}

// ── Toast Notifications ───────────────────────────────────────────
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span> ${escapeHtml(message)}`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('toast-out');
    toast.addEventListener('animationend', () => toast.remove());
  }, 4000);
}

// ── Utility Functions ─────────────────────────────────────────────
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function formatDate(isoStr) {
  if (!isoStr) return '—';
  const d = new Date(isoStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    + ' ' + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function formatConfidence(score) {
  if (score == null || score === undefined) return 'N/A';
  return `${Math.round(score * 100)}%`;
}

function countEntities(data) {
  const lists = ['symptoms', 'medications', 'procedures', 'lab_values', 'body_parts'];
  return lists.reduce((sum, k) => sum + (data[k]?.length || 0), 0);
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Make functions accessible globally
window.exportReport = exportReport;
window.loadHistory = loadHistory;
