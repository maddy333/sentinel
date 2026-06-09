DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SentinelAI | Self-Healing Autonomous Ops</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #0b0f19;
            --bg-surface: rgba(17, 24, 39, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --primary: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.15);
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.1);
            --warning: #f59e0b;
            --warning-glow: rgba(245, 158, 11, 0.1);
            --critical: #ef4444;
            --critical-glow: rgba(239, 68, 68, 0.1);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            overflow-x: hidden;
            min-height: 100vh;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.1) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.05) 0px, transparent 50%);
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem 2rem;
            border-bottom: 1px solid var(--border-color);
            background: rgba(11, 15, 25, 0.8);
            backdrop-filter: blur(12px);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .logo-container {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .logo-icon {
            width: 2rem;
            height: 2rem;
            background: linear-gradient(135deg, var(--primary), #4f46e5);
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.2rem;
            box-shadow: 0 0 15px var(--primary-glow);
        }

        .logo-text {
            font-weight: 700;
            font-size: 1.25rem;
            letter-spacing: -0.5px;
            background: linear-gradient(to right, #ffffff, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .status-badge {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--success-glow);
            border: 1px solid rgba(16, 185, 129, 0.2);
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--success);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: var(--success);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.9); opacity: 0.6; }
            50% { transform: scale(1.2); opacity: 1; }
            100% { transform: scale(0.9); opacity: 0.6; }
        }

        main {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 1.5rem;
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
        }

        @media (min-width: 1024px) {
            main {
                grid-template-columns: 350px 1fr;
            }
        }

        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }

        .card {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(16px);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s, border-color 0.2s;
        }

        .card:hover {
            border-color: rgba(99, 102, 241, 0.25);
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1.25rem;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* Metrics Display */
        .metric-item {
            margin-bottom: 1.25rem;
        }

        .metric-item:last-child {
            margin-bottom: 0;
        }

        .metric-label-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
        }

        .metric-label {
            color: var(--text-muted);
            font-weight: 500;
        }

        .metric-value {
            font-weight: 600;
            color: #ffffff;
        }

        .progress-bar-bg {
            background: rgba(255, 255, 255, 0.05);
            height: 8px;
            border-radius: 9999px;
            overflow: hidden;
        }

        .progress-bar-fill {
            height: 100%;
            border-radius: 9999px;
            transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            background: var(--primary);
        }

        /* Inject Anomaly Buttons */
        .btn-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
        }

        .btn {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 0.75rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-family: inherit;
            font-weight: 500;
            font-size: 0.875rem;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .btn:hover {
            background: var(--primary);
            border-color: var(--primary);
            box-shadow: 0 0 10px var(--primary-glow);
            transform: translateY(-2px);
        }

        .btn-warning:hover {
            background: var(--warning);
            border-color: var(--warning);
            box-shadow: 0 0 10px var(--warning-glow);
        }

        .btn-critical:hover {
            background: var(--critical);
            border-color: var(--critical);
            box-shadow: 0 0 10px var(--critical-glow);
        }

        /* Telemetry Links */
        .telemetry-links {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .telemetry-link {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 1rem;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            text-decoration: none;
            color: var(--text-main);
            font-size: 0.875rem;
            transition: background 0.2s;
        }

        .telemetry-link:hover {
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.15);
        }

        /* Main Workflow Content */
        .workflows-container {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .workflow-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            animation: fadeIn 0.4s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .wf-header {
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .wf-title-grp {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .wf-id {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: var(--text-muted);
            background: rgba(255, 255, 255, 0.05);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
        }

        .wf-title {
            font-weight: 600;
            font-size: 1.05rem;
        }

        .wf-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge-detected { background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); }
        .badge-plan_formulated { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-executing { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
        .badge-success { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
        .badge-failed { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

        .wf-body {
            padding: 1.5rem;
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }

        @media (min-width: 768px) {
            .wf-body {
                grid-template-columns: 1fr 1fr;
            }
        }

        .wf-section-title {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .anomaly-info {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
        }

        .anomaly-desc {
            font-weight: 500;
            margin-bottom: 0.5rem;
        }

        .anomaly-meta {
            display: flex;
            gap: 1rem;
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        .script-block, .log-block {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            background: #070913;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            overflow-x: auto;
            max-height: 250px;
            white-space: pre-wrap;
        }

        .script-block {
            color: #a5b4fc;
        }

        .log-block {
            color: #d1d5db;
        }

        .no-workflows {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 5rem 2rem;
            text-align: center;
            color: var(--text-muted);
            border: 1px dashed var(--border-color);
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.01);
        }

        .no-wf-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.3;
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-container">
            <div class="logo-icon">S</div>
            <div class="logo-text">SentinelAI</div>
        </div>
        <div class="status-badge">
            <div class="status-dot"></div>
            <span>Self-Healing Engine Active</span>
        </div>
    </header>

    <main>
        <div class="sidebar">
            <!-- System Telemetry Metrics -->
            <div class="card">
                <div class="card-title">
                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                    Live Infrastructure Metrics
                </div>
                <div class="metric-item">
                    <div class="metric-label-container">
                        <span class="metric-label">CPU Utilization</span>
                        <span class="metric-value" id="cpu-val">0%</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" id="cpu-bar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="metric-item">
                    <div class="metric-label-container">
                        <span class="metric-label">Memory Usage</span>
                        <span class="metric-value" id="mem-val">0%</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" id="mem-bar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="metric-item">
                    <div class="metric-label-container">
                        <span class="metric-label">Disk Storage</span>
                        <span class="metric-value" id="disk-val">0%</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" id="disk-bar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="metric-item">
                    <div class="metric-label-container">
                        <span class="metric-label">Simulated Database Timeouts</span>
                        <span class="metric-value" id="db-val" style="color: var(--text-main);">0</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" id="db-bar" style="width: 0%; background: var(--warning)"></div>
                    </div>
                </div>
            </div>

            <!-- Inject Anomalies -->
            <div class="card">
                <div class="card-title">
                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                    Inject Simulated Anomaly
                </div>
                <div class="btn-grid">
                    <button class="btn btn-warning" onclick="inject('cpu')">High CPU</button>
                    <button class="btn btn-warning" onclick="inject('memory')">Memory Leak</button>
                    <button class="btn btn-critical" onclick="inject('disk')">Disk Full</button>
                    <button class="btn btn-critical" onclick="inject('db_errors')">DB Timeout</button>
                </div>
            </div>

            <!-- Health & Telemetry Links -->
            <div class="card">
                <div class="card-title">
                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/></svg>
                    Cloud Telemetry & Probes
                </div>
                <div class="telemetry-links">
                    <a href="/metrics" target="_blank" class="telemetry-link">
                        <span>Prometheus Metrics</span>
                        <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                    </a>
                    <a href="/healthz" target="_blank" class="telemetry-link">
                        <span>Liveness / Readiness Probe</span>
                        <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                    </a>
                </div>
            </div>
        </div>

        <div class="content-area">
            <h2 style="margin-bottom: 1.5rem; font-weight: 700; font-size: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 9.172V5L8 4z"/></svg>
                Self-Healing Remediations
            </h2>
            <div id="workflows-list" class="workflows-container">
                <!-- Dynamic Content Loaded via JS -->
                <div class="no-workflows">
                    <div class="no-wf-icon">✦</div>
                    <h3>All Systems Operational</h3>
                    <p style="margin-top: 0.5rem; max-width: 400px; font-size: 0.9rem;">No active anomalies or remediation workflows. Inject an anomaly in the sidebar to simulate self-healing.</p>
                </div>
            </div>
        </div>
    </main>

    <script>
        async function updateTelemetry() {
            try {
                // Fetch workflows
                const response = await fetch('/workflows');
                const workflows = await response.json();
                
                // Fetch telemetry stats to sync progress bars
                const statsResponse = await fetch('/stats');
                const stats = await statsResponse.json();

                // Update UI Metrics
                document.getElementById('cpu-val').innerText = `${Math.round(stats.cpu_usage * 100)}%`;
                document.getElementById('cpu-bar').style.width = `${stats.cpu_usage * 100}%`;
                if (stats.cpu_usage >= 0.90) {
                    document.getElementById('cpu-bar').style.backgroundColor = 'var(--critical)';
                } else if (stats.cpu_usage >= 0.75) {
                    document.getElementById('cpu-bar').style.backgroundColor = 'var(--warning)';
                } else {
                    document.getElementById('cpu-bar').style.backgroundColor = 'var(--primary)';
                }

                document.getElementById('mem-val').innerText = `${Math.round(stats.memory_usage * 100)}%`;
                document.getElementById('mem-bar').style.width = `${stats.memory_usage * 100}%`;
                if (stats.memory_usage >= 0.85) {
                    document.getElementById('mem-bar').style.backgroundColor = 'var(--critical)';
                } else {
                    document.getElementById('mem-bar').style.backgroundColor = 'var(--primary)';
                }

                document.getElementById('disk-val').innerText = `${Math.round(stats.disk_usage * 100)}%`;
                document.getElementById('disk-bar').style.width = `${stats.disk_usage * 100}%`;
                if (stats.disk_usage >= 0.80) {
                    document.getElementById('disk-bar').style.backgroundColor = 'var(--critical)';
                } else {
                    document.getElementById('disk-bar').style.backgroundColor = 'var(--primary)';
                }

                document.getElementById('db-val').innerText = stats.db_errors;
                document.getElementById('db-bar').style.width = `${Math.min(100, (stats.db_errors / 15) * 100)}%`;

                // Render Workflows
                const listContainer = document.getElementById('workflows-list');
                if (workflows.length === 0) {
                    listContainer.innerHTML = `
                        <div class="no-workflows">
                            <div class="no-wf-icon">✦</div>
                            <h3>All Systems Operational</h3>
                            <p style="margin-top: 0.5rem; max-width: 400px; font-size: 0.9rem;">No active anomalies or remediation workflows. Inject an anomaly in the sidebar to simulate self-healing.</p>
                        </div>
                    `;
                    return;
                }

                let html = '';
                workflows.forEach(w => {
                    const statusClass = `badge-${w.status.toLowerCase()}`;
                    const timeStr = new Date(w.updated_at * 1000).toLocaleTimeString();
                    
                    let planHtml = '';
                    if (w.plan) {
                        planHtml = `
                            <div>
                                <div class="wf-section-title">DevOps Remediation Script (Risk: ${w.plan.risk_level})</div>
                                <div class="script-block">${escapeHtml(w.plan.script)}</div>
                            </div>
                        `;
                    } else {
                        planHtml = `
                            <div>
                                <div class="wf-section-title">DevOps Remediation Script</div>
                                <div style="color: var(--text-muted); font-style: italic; padding: 1rem; border: 1px dashed var(--border-color); border-radius: 8px;">
                                    Waiting for agent formulation...
                                </div>
                            </div>
                        `;
                    }

                    let executionHtml = '';
                    if (w.result) {
                        executionHtml = `
                            <div>
                                <div class="wf-section-title">Execution Sandbox Output (Exit Code: ${w.result.exit_code})</div>
                                <div class="log-block">${escapeHtml(w.result.output)}</div>
                            </div>
                        `;
                    } else {
                        executionHtml = `
                            <div>
                                <div class="wf-section-title">Execution Sandbox Output</div>
                                <div style="color: var(--text-muted); font-style: italic; padding: 1rem; border: 1px dashed var(--border-color); border-radius: 8px;">
                                    Awaiting script dispatch...
                                </div>
                            </div>
                        `;
                    }

                    html += `
                        <div class="workflow-card">
                            <div class="wf-header">
                                <div class="wf-title-grp">
                                    <span class="wf-title">Self-Healing Event</span>
                                    <span class="wf-id">ID: ${w.workflow_id.substring(0, 8)}</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 0.75rem;">
                                    <span style="font-size: 0.8rem; color: var(--text-muted);">${timeStr}</span>
                                    <span class="wf-badge ${statusClass}">${w.status}</span>
                                </div>
                            </div>
                            <div class="wf-body">
                                <div style="grid-column: 1 / -1;">
                                    <div class="wf-section-title">Anomaly Flagged by SRE Agent</div>
                                    <div class="anomaly-info" style="border-left: 3px solid ${w.anomaly.severity === 'CRITICAL' ? 'var(--critical)' : 'var(--warning)'};">
                                        <div class="anomaly-desc">${w.anomaly.description}</div>
                                        <div class="anomaly-meta">
                                            <span>Metric: <strong>${w.anomaly.metric_name}</strong></span>
                                            <span>Value: <strong>${w.anomaly.current_value.toFixed(3)}</strong></span>
                                            <span>Threshold: <strong>${w.anomaly.threshold.toFixed(2)}</strong></span>
                                        </div>
                                    </div>
                                </div>
                                ${planHtml}
                                ${executionHtml}
                            </div>
                        </div>
                    `;
                });
                listContainer.innerHTML = html;

            } catch (err) {
                console.error("Error updates: ", err);
            }
        }

        async function inject(type) {
            try {
                const response = await fetch(`/inject?anomaly_type=${type}`, { method: 'POST' });
                const res = await response.json();
                if (res.status === 'ok') {
                    // Instantly trigger an update pulse
                    setTimeout(updateTelemetry, 300);
                }
            } catch (err) {
                console.error("Error injecting anomaly: ", err);
            }
        }

        function escapeHtml(str) {
            return str
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        // Poll every 1.5 seconds
        setInterval(updateTelemetry, 1500);
        updateTelemetry();
    </script>
</body>
</html>
"""
