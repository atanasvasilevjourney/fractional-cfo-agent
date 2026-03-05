"""
CFO Agent — Web Dashboard (Flask)
Run: python dashboard.py
Then open: http://localhost:5000
"""

import os
import sys
import json
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, send_file

sys.path.insert(0, str(Path(__file__).parent))

from agent.orchestrator import run_agent
from agent.llm_caller import get_total_spend
from agent.drive_connector import check_gws_installed, setup_drive_folders

app = Flask(__name__)

# Store running job status
job_status = {"running": False, "log": [], "last_result": None}


def run_job_async(task, period, source, use_drive):
    """Run agent in background thread."""
    job_status["running"] = True
    job_status["log"] = []
    job_status["last_result"] = None

    import io
    from contextlib import redirect_stdout

    f = io.StringIO()
    try:
        with redirect_stdout(f):
            result = run_agent(task=task, source_dir=source,
                               period=period, use_drive=use_drive)
        job_status["last_result"] = result
        job_status["log"] = f.getvalue().split("\n")
    except Exception as e:
        job_status["log"] = [f"ERROR: {str(e)}"]
    finally:
        job_status["running"] = False


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CFO Agent Dashboard</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap" rel="stylesheet">
  <style>
    :root {
      --navy:    #1B3A6B;
      --teal:    #0D7377;
      --sky:     #D6E4F0;
      --mint:    #D0EFEF;
      --cream:   #FAFAF8;
      --ink:     #1A1A2E;
      --muted:   #6B7280;
      --green:   #16A34A;
      --amber:   #D97706;
      --red:     #DC2626;
      --border:  #E5E7EB;
      --card-bg: #FFFFFF;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'DM Sans', sans-serif;
      background: var(--cream);
      color: var(--ink);
      min-height: 100vh;
    }

    /* ── HEADER ── */
    header {
      background: var(--navy);
      padding: 0 2.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 64px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .logo { display: flex; align-items: center; gap: 0.75rem; }
    .logo-icon {
      width: 36px; height: 36px;
      background: var(--teal);
      border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.1rem;
    }
    .logo-text {
      font-family: 'DM Serif Display', serif;
      font-size: 1.25rem;
      color: #fff;
      letter-spacing: 0.01em;
    }
    .logo-sub { font-size: 0.75rem; color: #94A3B8; }

    .cost-badge {
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.2);
      border-radius: 20px;
      padding: 0.35rem 1rem;
      font-size: 0.8rem;
      color: #E2E8F0;
      display: flex; align-items: center; gap: 0.5rem;
      cursor: pointer;
      transition: background 0.2s;
    }
    .cost-badge:hover { background: rgba(255,255,255,0.18); }

    /* ── LAYOUT ── */
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem 2.5rem;
    }

    .grid { display: grid; grid-template-columns: 340px 1fr; gap: 1.5rem; }

    /* ── CARDS ── */
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .card-title {
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      margin-bottom: 1rem;
    }

    /* ── STAT CARDS ── */
    .stats { display: grid; grid-template-columns: repeat(4,1fr); gap: 1rem; margin-bottom: 1.5rem; }
    .stat-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
    }
    .stat-label { font-size: 0.72rem; color: var(--muted); font-weight: 500; margin-bottom: 0.35rem; }
    .stat-value { font-family: 'DM Serif Display', serif; font-size: 1.8rem; color: var(--navy); }
    .stat-sub { font-size: 0.75rem; color: var(--muted); margin-top: 0.2rem; }
    .stat-green .stat-value { color: var(--green); }
    .stat-amber .stat-value { color: var(--amber); }

    /* ── FORM ── */
    .form-group { margin-bottom: 1rem; }
    label {
      display: block;
      font-size: 0.78rem;
      font-weight: 500;
      color: var(--ink);
      margin-bottom: 0.4rem;
    }
    select, input[type="text"], input[type="month"] {
      width: 100%;
      padding: 0.6rem 0.85rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-family: 'DM Sans', sans-serif;
      font-size: 0.88rem;
      color: var(--ink);
      background: #fff;
      transition: border-color 0.2s;
      appearance: none;
    }
    select:focus, input:focus {
      outline: none;
      border-color: var(--teal);
      box-shadow: 0 0 0 3px rgba(13,115,119,0.1);
    }

    .btn {
      display: flex; align-items: center; justify-content: center; gap: 0.5rem;
      width: 100%;
      padding: 0.75rem;
      border: none;
      border-radius: 8px;
      font-family: 'DM Sans', sans-serif;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-primary {
      background: var(--navy);
      color: #fff;
    }
    .btn-primary:hover { background: #152d54; }
    .btn-primary:disabled { background: var(--muted); cursor: not-allowed; }
    .btn-teal { background: var(--teal); color: #fff; }
    .btn-teal:hover { background: #0a5c60; }

    /* ── TASK PILLS ── */
    .task-pills { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1.25rem; }
    .task-pill {
      display: flex; align-items: center; gap: 0.75rem;
      padding: 0.65rem 0.9rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      cursor: pointer;
      font-size: 0.85rem;
      transition: all 0.15s;
      background: #fff;
    }
    .task-pill:hover { border-color: var(--teal); background: var(--mint); }
    .task-pill.selected { border-color: var(--navy); background: var(--sky); font-weight: 600; }
    .pill-icon { font-size: 1.1rem; }
    .pill-desc { font-size: 0.72rem; color: var(--muted); }
    .pill-cost { margin-left: auto; font-size: 0.72rem; color: var(--teal); font-family: 'DM Mono', monospace; }

    /* ── LOG ── */
    .log-box {
      background: #0F172A;
      border-radius: 10px;
      padding: 1rem 1.25rem;
      font-family: 'DM Mono', monospace;
      font-size: 0.78rem;
      color: #94A3B8;
      min-height: 180px;
      max-height: 220px;
      overflow-y: auto;
      line-height: 1.6;
    }
    .log-box .ok   { color: #4ADE80; }
    .log-box .err  { color: #F87171; }
    .log-box .info { color: #60A5FA; }
    .log-box .warn { color: #FBBF24; }

    /* ── REPORTS LIST ── */
    .report-item {
      display: flex; align-items: center; gap: 0.75rem;
      padding: 0.75rem 0;
      border-bottom: 1px solid var(--border);
    }
    .report-item:last-child { border-bottom: none; }
    .report-icon {
      width: 36px; height: 36px;
      border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1rem;
      flex-shrink: 0;
    }
    .ri-report { background: var(--sky); }
    .ri-memo   { background: var(--mint); }
    .ri-var    { background: #FEF3C7; }
    .ri-cash   { background: #DCFCE7; }
    .report-name { font-size: 0.85rem; font-weight: 500; }
    .report-meta { font-size: 0.72rem; color: var(--muted); }
    .report-dl {
      margin-left: auto;
      font-size: 0.75rem;
      color: var(--teal);
      text-decoration: none;
      font-weight: 600;
      padding: 0.3rem 0.6rem;
      border: 1px solid var(--teal);
      border-radius: 6px;
      transition: all 0.15s;
    }
    .report-dl:hover { background: var(--teal); color: #fff; }

    /* ── SPINNER ── */
    .spinner {
      display: inline-block; width: 16px; height: 16px;
      border: 2px solid rgba(255,255,255,0.3);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 0.7s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ── FOLDER HINT ── */
    .folder-hint {
      background: linear-gradient(135deg, var(--sky), var(--mint));
      border-radius: 10px;
      padding: 1rem 1.25rem;
      font-size: 0.82rem;
      line-height: 1.6;
      margin-bottom: 1rem;
    }
    .folder-hint strong { color: var(--navy); }
    .folder-path {
      font-family: 'DM Mono', monospace;
      background: rgba(255,255,255,0.7);
      padding: 0.15rem 0.4rem;
      border-radius: 4px;
      font-size: 0.78rem;
      color: var(--navy);
    }

    /* ── PROGRESS BAR ── */
    .progress-wrap { background: var(--border); border-radius: 4px; height: 6px; margin: 0.75rem 0; overflow: hidden; }
    .progress-bar  { height: 100%; background: linear-gradient(90deg, var(--navy), var(--teal)); border-radius: 4px; transition: width 0.4s; }

    /* ── MODALS ── */
    .modal-overlay {
      display: none; position: fixed; inset: 0;
      background: rgba(0,0,0,0.5); backdrop-filter: blur(4px);
      z-index: 100; align-items: center; justify-content: center;
    }
    .modal-overlay.open { display: flex; }
    .modal {
      background: #fff; border-radius: 16px;
      padding: 2rem; width: 90%; max-width: 480px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.2);
    }
    .modal h3 { font-family: 'DM Serif Display', serif; font-size: 1.4rem; color: var(--navy); margin-bottom: 1rem; }
    .cost-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border); font-size: 0.88rem; }
    .cost-row:last-child { border: none; font-weight: 600; font-size: 1rem; }
    .close-btn { background: none; border: none; cursor: pointer; float: right; font-size: 1.2rem; color: var(--muted); }

    @media (max-width: 800px) {
      .grid { grid-template-columns: 1fr; }
      .stats { grid-template-columns: repeat(2,1fr); }
    }
  </style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-icon">💼</div>
    <div>
      <div class="logo-text">CFO Agent</div>
      <div class="logo-sub">AI-Powered Financial Intelligence</div>
    </div>
  </div>
  <div class="cost-badge" onclick="openCostModal()">
    💰 <span id="header-spend">Loading...</span> spent of $20.00
  </div>
</header>

<div class="container">

  <!-- Stats Row -->
  <div class="stats">
    <div class="stat-card">
      <div class="stat-label">Reports Generated</div>
      <div class="stat-value" id="stat-reports">—</div>
      <div class="stat-sub">all time</div>
    </div>
    <div class="stat-card stat-green">
      <div class="stat-label">Budget Remaining</div>
      <div class="stat-value" id="stat-remaining">$20.00</div>
      <div class="stat-sub">of $20.00 OpenAI credit</div>
    </div>
    <div class="stat-card stat-amber">
      <div class="stat-label">Total Spent</div>
      <div class="stat-value" id="stat-spent">$0.00</div>
      <div class="stat-sub">OpenAI API usage</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Est. Months Left</div>
      <div class="stat-value" id="stat-months">—</div>
      <div class="stat-sub">at current run rate</div>
    </div>
  </div>

  <div class="grid">

    <!-- LEFT: Control Panel -->
    <div>
      <div class="card" style="margin-bottom:1rem">
        <div class="card-title">📂 Drop Your Files Here</div>
        <div class="folder-hint">
          Save your Excel exports into:<br>
          <span class="folder-path">drop-files-here/</span><br><br>
          Accepts: <strong>trial_balance.xlsx</strong>, <strong>budget.xlsx</strong>,
          <strong>ar_aging.xlsx</strong>, <strong>ap_schedule.xlsx</strong>
        </div>
      </div>

      <div class="card">
        <div class="card-title">🚀 Run Agent</div>

        <div class="task-pills" id="task-pills">
          <div class="task-pill selected" data-task="monthly-report" onclick="selectTask(this)">
            <span class="pill-icon">📊</span>
            <div>
              <div>Monthly Financial Report</div>
              <div class="pill-desc">P&L, margins, variance commentary</div>
            </div>
            <span class="pill-cost">~$0.01</span>
          </div>
          <div class="task-pill" data-task="budget-variance" onclick="selectTask(this)">
            <span class="pill-icon">🎯</span>
            <div>
              <div>Budget vs Actuals</div>
              <div class="pill-desc">Variance flags and root causes</div>
            </div>
            <span class="pill-cost">~$0.01</span>
          </div>
          <div class="task-pill" data-task="cashflow-forecast" onclick="selectTask(this)">
            <span class="pill-icon">💧</span>
            <div>
              <div>Cash Flow Forecast</div>
              <div class="pill-desc">13-week rolling, 3 scenarios</div>
            </div>
            <span class="pill-cost">~$0.01</span>
          </div>
          <div class="task-pill" data-task="board-memo" onclick="selectTask(this)">
            <span class="pill-icon">📝</span>
            <div>
              <div>Board / Investor Memo</div>
              <div class="pill-desc">Executive narrative draft</div>
            </div>
            <span class="pill-cost">~$0.02</span>
          </div>
          <div class="task-pill" data-task="full-suite" onclick="selectTask(this)">
            <span class="pill-icon">⚡</span>
            <div>
              <div>Full Suite (all 4 reports)</div>
              <div class="pill-desc">Run everything at once</div>
            </div>
            <span class="pill-cost">~$0.05</span>
          </div>
        </div>

        <div class="form-group">
          <label>Period</label>
          <input type="month" id="period-input" value="">
        </div>

        <div class="form-group">
          <label>Data Source</label>
          <div id="drive-toggle" style="display:flex;gap:0.5rem">
            <button id="btn-drive" onclick="setSource('drive')" style="
              flex:1;padding:0.55rem;border-radius:8px;font-size:0.82rem;font-weight:600;
              cursor:pointer;transition:all 0.15s;border:2px solid var(--teal);
              background:var(--teal);color:#fff">
              ☁️ Google Drive
            </button>
            <button id="btn-local" onclick="setSource('local')" style="
              flex:1;padding:0.55rem;border-radius:8px;font-size:0.82rem;font-weight:600;
              cursor:pointer;transition:all 0.15s;border:2px solid var(--border);
              background:#fff;color:var(--muted)">
              📂 Local Folder
            </button>
          </div>
          <div id="drive-status" style="font-size:0.72rem;margin-top:0.4rem;color:var(--muted)">
            Checking gws...
          </div>
        </div>

        <div id="progress-wrap" class="progress-wrap" style="display:none">
          <div class="progress-bar" id="progress-bar" style="width:0%"></div>
        </div>

        <button class="btn btn-primary" id="run-btn" onclick="runAgent()">
          ▶ Run Agent
        </button>
      </div>

      <div class="card" style="margin-top:1rem">
        <div class="card-title">📟 Agent Log</div>
        <div class="log-box" id="log-box">
          <span class="info">Waiting for job...</span>
        </div>
      </div>
    </div>

    <!-- RIGHT: Reports & Output -->
    <div>
      <div class="card" style="margin-bottom:1rem">
        <div class="card-title">📁 Recent Reports</div>
        <div id="reports-list">
          <div style="color:var(--muted);font-size:0.85rem;padding:1rem 0;text-align:center">
            No reports yet — run the agent to generate your first report
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">📄 Report Preview</div>
        <div id="report-preview" style="
          font-size:0.85rem; line-height:1.7; color:var(--ink);
          max-height:520px; overflow-y:auto;
          font-family:'DM Sans',sans-serif;
        ">
          <div style="color:var(--muted);padding:2rem;text-align:center">
            Select a report above to preview it here
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Cost Modal -->
<div class="modal-overlay" id="cost-modal">
  <div class="modal">
    <button class="close-btn" onclick="closeCostModal()">✕</button>
    <h3>💰 OpenAI Spend Tracker</h3>
    <div id="cost-detail">Loading...</div>
    <br>
    <button class="btn btn-teal" onclick="closeCostModal()">Close</button>
  </div>
</div>

<script>
  // ── State ──
  let selectedTask = "monthly-report";
  let useDrive = null; // null=auto, true=drive, false=local
  let polling = null;

  // ── Set default period ──
  const now = new Date();
  document.getElementById("period-input").value =
    `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,"0")}`;

  // ── Check Drive/gws status ──
  async function checkDriveStatus() {
    try {
      const res = await fetch("/api/drive-status");
      const data = await res.json();
      const statusEl = document.getElementById("drive-status");
      if (data.gws_installed) {
        statusEl.innerHTML = `<span style="color:var(--green)">✅ gws installed — Google Drive ready</span>`;
        setSource('drive');
      } else {
        statusEl.innerHTML = `<span style="color:var(--amber)">⚠️ gws not installed — using local folder. <a href="https://github.com/googleworkspace/cli" target="_blank" style="color:var(--teal)">Install gws</a></span>`;
        setSource('local');
      }
    } catch(e) {
      setSource('local');
    }
  }

  function setSource(mode) {
    const btnDrive = document.getElementById("btn-drive");
    const btnLocal = document.getElementById("btn-local");
    if (mode === 'drive') {
      useDrive = true;
      btnDrive.style.cssText += ";background:var(--teal);color:#fff;border-color:var(--teal)";
      btnLocal.style.cssText += ";background:#fff;color:var(--muted);border-color:var(--border)";
    } else {
      useDrive = false;
      btnLocal.style.cssText += ";background:var(--navy);color:#fff;border-color:var(--navy)";
      btnDrive.style.cssText += ";background:#fff;color:var(--muted);border-color:var(--border)";
    }
  }

  // ── Task selection ──
  function selectTask(el) {
    document.querySelectorAll(".task-pill").forEach(p => p.classList.remove("selected"));
    el.classList.add("selected");
    selectedTask = el.dataset.task;
  }

  // ── Run agent ──
  async function runAgent() {
    const btn = document.getElementById("run-btn");
    const period = document.getElementById("period-input").value;
    if (!period) { alert("Please select a period"); return; }

    btn.disabled = true;
    btn.innerHTML = '<div class="spinner"></div> Running...';
    document.getElementById("log-box").innerHTML = '<span class="info">Starting agent...</span>';
    document.getElementById("progress-wrap").style.display = "block";
    animateProgress();

    try {
      const res = await fetch("/api/run", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ task: selectedTask, period, use_drive: useDrive })
      });
      const data = await res.json();
      if (data.job_id) {
        polling = setInterval(() => pollStatus(), 2000);
      }
    } catch(e) {
      logLine("ERROR: " + e.message, "err");
      resetBtn();
    }
  }

  let progressVal = 0;
  function animateProgress() {
    progressVal = 0;
    const bar = document.getElementById("progress-bar");
    const iv = setInterval(() => {
      if (progressVal >= 90) { clearInterval(iv); return; }
      progressVal += Math.random() * 8;
      bar.style.width = Math.min(progressVal, 90) + "%";
    }, 600);
  }

  async function pollStatus() {
    try {
      const res = await fetch("/api/status");
      const data = await res.json();

      // Update log
      if (data.log && data.log.length) {
        const box = document.getElementById("log-box");
        box.innerHTML = data.log.map(line => formatLogLine(line)).join("<br>");
        box.scrollTop = box.scrollHeight;
      }

      if (!data.running) {
        clearInterval(polling);
        document.getElementById("progress-bar").style.width = "100%";
        setTimeout(() => {
          document.getElementById("progress-wrap").style.display = "none";
          resetBtn();
          loadReports();
          loadCostStats();
        }, 800);
      }
    } catch(e) { /* ignore poll errors */ }
  }

  function formatLogLine(line) {
    if (!line.trim()) return "";
    if (line.includes("✅") || line.includes("Done")) return `<span class="ok">${line}</span>`;
    if (line.includes("❌") || line.includes("ERROR")) return `<span class="err">${line}</span>`;
    if (line.includes("🤖") || line.includes("Running")) return `<span class="info">${line}</span>`;
    if (line.includes("⚠") || line.includes("Warning")) return `<span class="warn">${line}</span>`;
    return line;
  }

  function logLine(text, cls = "") {
    const box = document.getElementById("log-box");
    box.innerHTML += `<br><span class="${cls}">${text}</span>`;
  }

  function resetBtn() {
    const btn = document.getElementById("run-btn");
    btn.disabled = false;
    btn.innerHTML = "▶ Run Agent";
  }

  // ── Load reports list ──
  async function loadReports() {
    const res = await fetch("/api/reports");
    const data = await res.json();
    const list = document.getElementById("reports-list");

    if (!data.reports || !data.reports.length) {
      list.innerHTML = `<div style="color:var(--muted);font-size:0.85rem;padding:1rem 0;text-align:center">No reports yet</div>`;
      return;
    }

    const icons = {
      "monthly-report":   {icon:"📊", bg:"ri-report"},
      "budget-variance":  {icon:"🎯", bg:"ri-var"},
      "cashflow-forecast":{icon:"💧", bg:"ri-cash"},
      "board-memo":       {icon:"📝", bg:"ri-memo"},
    };

    list.innerHTML = data.reports.slice(0, 8).map(r => {
      const ic = icons[r.task] || {icon:"📄", bg:"ri-report"};
      const driveLink = r.drive_url
        ? `<a class="report-dl" href="${r.drive_url}" target="_blank" style="margin-right:0.3rem;background:var(--teal);color:#fff;border-color:var(--teal)">☁️ Drive</a>`
        : "";
      return `
        <div class="report-item">
          <div class="report-icon ${ic.bg}">${ic.icon}</div>
          <div>
            <div class="report-name">${r.task} — ${r.period}</div>
            <div class="report-meta">${r.modified}</div>
          </div>
          ${driveLink}
          <a class="report-dl" href="/api/download/${encodeURIComponent(r.path)}" download>⬇ Local</a>
          <button style="margin-left:0.5rem;background:none;border:1px solid var(--border);border-radius:6px;padding:0.3rem 0.6rem;cursor:pointer;font-size:0.75rem;color:var(--navy)" onclick="previewReport('${r.path}')">👁 View</button>
        </div>`;
    }).join("");
  }

  // ── Preview report ──
  async function previewReport(path) {
    const res = await fetch("/api/preview/" + encodeURIComponent(path));
    const data = await res.json();
    const preview = document.getElementById("report-preview");
    // Simple markdown to HTML (basic)
    let html = data.content
      .replace(/^# (.+)$/gm, '<h2 style="font-family:DM Serif Display,serif;color:#1B3A6B;margin:1rem 0 0.5rem;font-size:1.3rem">$1</h2>')
      .replace(/^## (.+)$/gm, '<h3 style="font-family:DM Serif Display,serif;color:#0D7377;margin:0.8rem 0 0.4rem;font-size:1.1rem">$1</h3>')
      .replace(/^### (.+)$/gm, '<h4 style="font-weight:600;color:#1A1A2E;margin:0.6rem 0 0.3rem">$1</h4>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`(.+?)`/g, '<code style="background:#F1F5F9;padding:0.1rem 0.3rem;border-radius:3px;font-family:DM Mono,monospace;font-size:0.82rem">$1</code>')
      .replace(/^- (.+)$/gm, '<li style="margin:0.2rem 0 0.2rem 1rem">$1</li>')
      .replace(/^\d+\. (.+)$/gm, '<li style="margin:0.2rem 0 0.2rem 1rem;list-style:decimal">$1</li>')
      .replace(/^---$/gm, '<hr style="border:none;border-top:1px solid #E5E7EB;margin:1rem 0">')
      .replace(/\n\n/g, '</p><p style="margin-bottom:0.5rem">')
      .replace(/^\|(.+)\|$/gm, (m) => {
        // Simple table row styling
        if (m.includes("---")) return '<tr style="background:#F8FAFC"><td></td></tr>';
        const cells = m.split("|").filter(c => c.trim());
        return '<tr>' + cells.map(c => `<td style="padding:0.4rem 0.6rem;border:1px solid #E5E7EB;font-size:0.82rem">${c.trim()}</td>`).join('') + '</tr>';
      });

    // Wrap tables
    html = html.replace(/(<tr>.*<\/tr>\s*)+/gs, (m) =>
      `<table style="border-collapse:collapse;width:100%;margin:0.75rem 0;font-size:0.83rem">${m}</table>`);

    preview.innerHTML = `<div style="padding:0.5rem">${html}</div>`;
  }

  // ── Cost stats ──
  async function loadCostStats() {
    const res = await fetch("/api/cost");
    const data = await res.json();
    document.getElementById("stat-spent").textContent = `$${data.total_usd.toFixed(4)}`;
    document.getElementById("stat-remaining").textContent = `$${data.remaining_from_20.toFixed(2)}`;
    document.getElementById("stat-reports").textContent = data.calls;
    document.getElementById("header-spend").textContent = `$${data.total_usd.toFixed(4)}`;

    const avgCost = data.calls > 0 ? data.total_usd / data.calls : 0;
    const callsLeft = avgCost > 0 ? Math.floor(data.remaining_from_20 / avgCost) : "∞";
    document.getElementById("stat-months").textContent =
      data.calls > 0 ? `~${Math.floor(callsLeft / 4)}` : "∞";

    // Cost modal detail
    let detail = `
      <div class="cost-row"><span>Total spent</span><span>$${data.total_usd.toFixed(4)}</span></div>
      <div class="cost-row"><span>API calls made</span><span>${data.calls}</span></div>
      <div class="cost-row"><span>Avg cost per report</span><span>$${avgCost.toFixed(4)}</span></div>
      <div class="cost-row"><span>Remaining budget</span><span>$${data.remaining_from_20.toFixed(4)}</span></div>
      <div class="cost-row"><span>Est. reports remaining</span><span>${callsLeft}</span></div>
    `;
    if (data.entries && data.entries.length) {
      detail += `<br><div style="font-size:0.78rem;color:var(--muted);margin-bottom:0.5rem">RECENT CALLS</div>`;
      detail += data.entries.slice(-5).reverse().map(e =>
        `<div class="cost-row"><span>${e.timestamp.slice(0,16)}</span><span>$${e.cost_usd.toFixed(5)}</span></div>`
      ).join("");
    }
    document.getElementById("cost-detail").innerHTML = detail;
  }

  function openCostModal()  { document.getElementById("cost-modal").classList.add("open"); }
  function closeCostModal() { document.getElementById("cost-modal").classList.remove("open"); }

  // ── Init ──
  loadReports();
  loadCostStats();
  checkDriveStatus();
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)


@app.route("/api/drive-status")
def api_drive_status():
    gws = check_gws_installed()
    return jsonify({"gws_installed": gws})


@app.route("/api/run", methods=["POST"])
def api_run():
    if job_status["running"]:
        return jsonify({"error": "A job is already running"}), 400

    body = request.get_json()
    task      = body.get("task", "monthly-report")
    period    = body.get("period")
    source    = body.get("source", "drop-files-here")
    use_drive = body.get("use_drive", None)  # None = auto

    thread = threading.Thread(
        target=run_job_async,
        args=(task, period, source, use_drive),
        daemon=True
    )
    thread.start()

    return jsonify({"job_id": "running", "status": "started"})


@app.route("/api/status")
def api_status():
    return jsonify({
        "running": job_status["running"],
        "log": job_status["log"],
        "has_result": job_status["last_result"] is not None,
    })


@app.route("/api/reports")
def api_reports():
    reports = []
    outputs_dir = Path("outputs")

    # Load summary JSONs to get Drive URLs
    drive_urls = {}
    if outputs_dir.exists():
        for summary_file in outputs_dir.rglob("*_summary.json"):
            try:
                with open(summary_file) as f:
                    summary = json.load(f)
                period = summary.get("period", "")
                for task, result in summary.get("results", {}).items():
                    key = f"{period}_{task}"
                    drive_urls[key] = result.get("drive_url")
            except Exception:
                pass

    if outputs_dir.exists():
        for md_file in sorted(outputs_dir.rglob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True):
            name = md_file.stem
            parts = name.split("_", 1)
            period = parts[0] if parts else ""
            task   = parts[1] if len(parts) > 1 else name
            mtime  = datetime.fromtimestamp(md_file.stat().st_mtime)
            reports.append({
                "path":      str(md_file),
                "period":    period,
                "task":      task,
                "modified":  mtime.strftime("%d %b %Y, %H:%M"),
                "drive_url": drive_urls.get(f"{period}_{task}"),
            })

    return jsonify({"reports": reports[:20]})


@app.route("/api/preview/<path:filepath>")
def api_preview(filepath):
    fp = Path(filepath)
    if not fp.exists() or fp.suffix != ".md":
        return jsonify({"error": "File not found"}), 404
    content = fp.read_text(encoding="utf-8")
    return jsonify({"content": content})


@app.route("/api/download/<path:filepath>")
def api_download(filepath):
    fp = Path(filepath)
    if not fp.exists():
        return "File not found", 404
    return send_file(fp.absolute(), as_attachment=True)


@app.route("/api/cost")
def api_cost():
    return jsonify(get_total_spend())


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  💼 CFO Agent Dashboard")
    print("  Open in browser: http://localhost:5000")
    print("="*55 + "\n")
    app.run(debug=False, port=5000)
