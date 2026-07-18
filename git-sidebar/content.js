console.log("🚀 GitHub Intel Sidebar: Script loaded!");

function initSidebar() {
        const match = window.location.pathname.match(/^\/([^\/]+)\/([^\/]+)\/?$/);
        if (!match) return;

        const owner = match[1];
        const repo = match[2];

        const host = document.createElement('div');
        host.id = 'github-intel-sidebar-host';
        host.style.cssText = 'position: fixed; right: 24px; top: 80px; z-index: 9999;';

        const shadow = host.attachShadow({ mode: 'open' });
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = chrome.runtime.getURL('content.css');
        shadow.appendChild(link); // Fixed typo here

        const container = document.createElement('div');
        container.className = 'sidebar-container';
        container.innerHTML = `
    <div class="sidebar-header">
      <span>🔍 Repo Intelligence</span>
      <span class="drag-icon" style="cursor:grab">⠿</span>
    </div>
    <div class="sidebar-content">
      <div class="tabs">
        <button class="tab-btn active" data-tab="overview">Overview</button>
        <button class="tab-btn" data-tab="analysis">Deep Dive</button>
        <button class="tab-btn" data-tab="explore">Explore</button>
      </div>
      
      <div id="tab-overview" class="tab-content active">
        <div class="card"><div class="card-title">📝 TL;DR Summary</div><div id="intel-readme" class="card-content loading">Thinking...</div></div>
        <div class="card"><div class="card-title">🏷️ Repository Type</div><div id="intel-type" class="card-content loading">Detecting...</div></div>
        <div class="card"><div class="card-title">💻 Platform Support</div><div id="intel-os" class="card-content loading">Scanning...</div></div>
      </div>

      <div id="tab-analysis" class="tab-content">
        <div class="card"><div class="card-title">🛠️ Tech Stack & Architecture</div><div id="intel-tech" class="card-content loading">Analyzing...</div></div>
        <div class="card"><div class="card-title">🚀 Deployment & Onboarding</div><div id="intel-stats" class="card-content loading">Calculating...</div></div>
      </div>

      <div id="tab-explore" class="tab-content">
        <div class="card"><div class="card-title">🔗 Similar Projects</div><div id="intel-related" class="card-content loading">Searching...</div></div>
      </div>
    </div>
  `;
        shadow.appendChild(container);
        document.body.appendChild(host);

        setupDraggable(host, shadow);
        setupTabs(shadow);
        fetchFromBackend(owner, repo, shadow);
}

function setupTabs(shadow) {
        const buttons = shadow.querySelectorAll('.tab-btn');
        const contents = shadow.querySelectorAll('.tab-content');
        buttons.forEach(btn => {
                btn.addEventListener('click', () => {
                        buttons.forEach(b => b.classList.remove('active'));
                        contents.forEach(c => c.classList.remove('active'));
                        btn.classList.add('active');
                        shadow.querySelector(`#tab-${btn.dataset.tab}`).classList.add('active');
                });
        });
}

function setupDraggable(host, shadow) {
        const header = shadow.querySelector('.sidebar-header');
        let isDragging = false, offsetX = 0, offsetY = 0;
        header.addEventListener('mousedown', (e) => {
                isDragging = true;
                const rect = host.getBoundingClientRect();
                offsetX = e.clientX - rect.left; offsetY = e.clientY - rect.top;
                host.style.right = 'auto'; host.style.left = rect.left + 'px'; host.style.top = rect.top + 'px';
        });
        document.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                host.style.left = (e.clientX - offsetX) + 'px'; host.style.top = (e.clientY - offsetY) + 'px';
        });
        document.addEventListener('mouseup', () => isDragging = false);
}

async function fetchFromBackend(owner, repo, shadow) {
        // Fetch BOTH keys from storage
        const { gh_token, groq_key } = await chrome.storage.local.get(['gh_token', 'groq_key']);

        try {
                const res = await fetch('http://localhost:5000/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ owner, repo, token: gh_token, groq_key: groq_key })
                });

                if (!res.ok) throw new Error("Backend error");
                const data = await res.json();
                if (data.error) throw new Error(data.error);

                // --- OVERVIEW TAB ---
                const summaryDiv = document.createElement('div');
                summaryDiv.className = 'readme-text';
                summaryDiv.textContent = data.summary || "No summary available";
                const summaryContainer = shadow.querySelector('#intel-readme');
                summaryContainer.innerHTML = '';
                summaryContainer.appendChild(summaryDiv);

                const tags = data.tags || [];
                shadow.querySelector('#intel-type').innerHTML = `<div class="type-tags">${tags.map(t => `<span class="type-tag">${t}</span>`).join('')}</div>`;

                const osList = data.os_support || [];
                const osIcons = { 'Linux': '🐧', 'macOS': '🍎', 'Windows': '🪟', 'Cross-platform': '🌐' };
                shadow.querySelector('#intel-os').innerHTML = `<div class="os-badges">${osList.map(os => `<span class="os-badge">${osIcons[os] || '💻'} ${os}</span>`).join('')}</div>`;

                // --- ANALYSIS TAB ---
                const frameworks = Array.isArray(data.frameworks) ? data.frameworks : [data.frameworks || "Unknown"];
                const architectures = Array.isArray(data.architecture) ? data.architecture : [data.architecture || "Standard"];
                const deployments = Array.isArray(data.deployment_targets) ? data.deployment_targets : [data.deployment_targets || "Standard"];
                const entryPoints = Array.isArray(data.entry_points) ? data.entry_points : [data.entry_points || "Standard"];

                const renderTags = (arr) => arr.length > 0 && arr[0] !== "Unknown" && arr[0] !== "Standard"
                        ? `<div class="type-tags">${arr.map(t => `<span class="type-tag">${t}</span>`).join('')}</div>`
                        : '<span class="stat-value" style="font-size:12px; color:#64748b;">Not explicitly detected</span>';

                shadow.querySelector('#intel-tech').innerHTML = `
      <div class="stat-row"><span class="stat-label">🛠️ Frameworks & Tools</span></div>
      ${renderTags(frameworks)}
      <div class="stat-row" style="margin-top: 12px;"><span class="stat-label">🏗️ Architecture</span></div>
      ${renderTags(architectures)}
      <div class="stat-row" style="margin-top: 12px;"><span class="stat-label">Setup Complexity</span>
        <span class="stat-value"><span class="complexity-badge ${data.setup_complexity?.toLowerCase() || 'medium'}">${data.setup_complexity || "Medium"}</span></span>
      </div>
    `;

                shadow.querySelector('#intel-stats').innerHTML = `
      <div class="stat-row"><span class="stat-label">🚀 Deployment Targets</span></div>
      ${renderTags(deployments)}
      <div class="stat-row" style="margin-top: 12px;"><span class="stat-label">🎯 Code Entry Points</span></div>
      ${entryPoints.length > 0 && entryPoints[0] !== "Standard"
                                ? `<div style="font-family: monospace; font-size: 12px; color: #0891b2; background: #ecfeff; padding: 8px; border-radius: 6px; margin-top: 4px; border: 1px solid #cffafe;">${entryPoints.join('<br>')}</div>`
                                : '<span class="stat-value" style="font-size:12px; color:#64748b;">Standard structure</span>'}
    `;

                // --- EXPLORE TAB ---
                const related = data.related_repos || [];
                if (related.length === 0) {
                        shadow.querySelector('#intel-related').innerHTML = '<div class="empty-state">No closely related repos found</div>';
                } else {
                        shadow.querySelector('#intel-related').innerHTML = `<div class="related-list">${related.map(r =>
                                `<a class="related-item" href="${r.url}" target="_blank"><div class="related-name">${r.name}</div><div class="related-stars">⭐ ${r.stars.toLocaleString()}</div></a>`
                        ).join('')}</div>`;
                }

        } catch (err) {
                console.error(err);
                shadow.querySelector('.sidebar-content').innerHTML = `
      <div class="error-card">
        <div class="error-title">⚠️ Connection Error</div>
        <div class="error-message">${err.message}</div>
        <div class="error-hint">Make sure Python backend is running on port 5000</div>
      </div>`;
        }
}

if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSidebar);
} else {
        initSidebar();
}