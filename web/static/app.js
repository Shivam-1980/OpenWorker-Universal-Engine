/* ============================================================
   DOM Elements & Initialization
============================================================ */
const terminal = document.getElementById("terminal");
const miniTerminal = document.getElementById("mini-terminal");
const codeEditor = document.getElementById("code-editor");
const taskInput = document.getElementById("task-input");
const sendBtn = document.getElementById("send-btn");
const buildStatus = document.getElementById("build-status");
const activeFileName = document.getElementById("active-file-name");
const clearBtn = document.getElementById("clear-term-btn");
const livePreview = document.getElementById("live-preview");
const runCodeBtn = document.getElementById("run-code-btn");
const zipUpload = document.getElementById("zip-upload");
const downloadBtn = document.getElementById("download-btn");

// Generate unique session ID and bind globally for sidebar synchronization
const sessionId = "session_" + Math.random().toString(36).substring(2, 9);
window.currentSessionId = sessionId;

// Dynamically determine whether to use wss:// (secure) or ws:// (insecure)
const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const wsUrl = `${protocol}${window.location.host}/ws/engineer`;
const ws = new WebSocket(wsUrl);

/* ============================================================
   Activity Log & Terminal Handlers
============================================================ */
function log(text, type = "system") {
    if (!terminal) return;
    const div = document.createElement("div");
    div.className = `log-entry log-${type}`;
    div.textContent = text;
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}

function termPrint(text, type = "output") {
    if (!miniTerminal) return;
    const line = document.createElement("div");

    switch (type) {
        case "cmd": line.className = "term-line-cmd"; break;
        case "err": line.className = "term-line-err"; break;
        case "info": line.className = "term-line-info"; break;
        case "success": line.className = "term-line-success"; break;
        case "warning": line.className = "term-line-warning"; break;
        default: line.className = "term-line"; break;
    }

    line.textContent = text;
    miniTerminal.appendChild(line);
    miniTerminal.scrollTop = miniTerminal.scrollHeight;
}

if (clearBtn) {
    clearBtn.addEventListener("click", () => {
        if (miniTerminal) miniTerminal.innerHTML = "";
    });
}

/* ============================================================
   WebSocket Lifecycle & Message Switchboard
============================================================ */
ws.onopen = () => {
    log("Engine Socket Connected. Ready for directives.", "success");
    termPrint(`Connected to OpenWorker Engine [Session: ${sessionId}]`, "success");
    refreshFileExplorer();
};

const telemetryScript = `
<script>
    window.onerror = function(msg, url, line) {
        window.parent.postMessage({type: 'iframe_err', msg: 'Line ' + line + ': ' + msg}, '*');
    };
    const originalConsoleError = console.error;
    console.error = function(msg) {
        window.parent.postMessage({type: 'iframe_err', msg: msg}, '*');
        originalConsoleError.apply(console, arguments);
    };
    const originalConsoleLog = console.log;
    console.log = function(msg) {
        window.parent.postMessage({type: 'iframe_log', msg: msg}, '*');
        originalConsoleLog.apply(console, arguments);
    };
</script>
`;

window.addEventListener('message', (e) => {
    if (e.data.type === 'iframe_err') {
        termPrint(`[Web Preview Error] ${e.data.msg}`, 'err');
    } else if (e.data.type === 'iframe_log') {
        termPrint(`[Web Preview Log] ${e.data.msg}`, 'info');
    }
});

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.action === "refresh_tree") {
        refreshFileExplorer();
    }

    if (data.log) {
        log(data.log, data.type || "system");
    }

    if (data.command) {
        termPrint(`$ ${data.command}`, 'cmd');
    }

    if (data.stdout) {
        let formattedOutput = data.stdout.replace(
            /<thinking>(.*?)<\/thinking>/gs, 
            '<details class="ai-thinking"><summary>AI Architecture Reasoning</summary><p>$1</p></details>'
        );
        const line = document.createElement('div');
        line.innerHTML = formattedOutput;
        line.className = 'term-line-output';
        if (miniTerminal) {
            miniTerminal.appendChild(line);
            miniTerminal.scrollTop = miniTerminal.scrollHeight;
        }
    }

    if (data.stderr) termPrint(data.stderr, 'err');
    if (data.info) termPrint(data.info, 'info');

    if (data.code_update) {
        if (codeEditor) codeEditor.value = data.code_update.content;
        if (activeFileName) activeFileName.textContent = data.code_update.filename;
        
        if (livePreview && data.code_update.filename.endsWith('.html')) {
            livePreview.srcdoc = telemetryScript + data.code_update.content;
        }
        refreshFileExplorer();
    }

    if (data.status_update && buildStatus) {
        buildStatus.textContent = data.status_update;
        switch (data.status_update) {
            case "THINKING":
            case "BUILDING":
            case "DIAGNOSING":
                buildStatus.style.color = "#e5c07b";
                break;
            case "SUCCESS":
                buildStatus.style.color = "#57ab5a";
                break;
            case "FAILED":
                buildStatus.style.color = "#e5534b";
                break;
            default:
                buildStatus.style.color = "#768390";
                break;
        }
    }
};

/* ============================================================
   Task Dispatching & Build Triggers
============================================================ */
function sendDirective() {
    if (!taskInput) return;
    const task = taskInput.value.trim();
    if (!task) return;

    const modeEl = document.querySelector('input[name="mode"]:checked');
    const mode = modeEl ? modeEl.value : "autonomous";

    ws.send(JSON.stringify({ task, mode, session_id: sessionId }));

    log(`> ${task}`, "cmd");
    termPrint(`$ openworker "${task}"`, "cmd");
    taskInput.value = "";
}

if (sendBtn) sendBtn.addEventListener("click", sendDirective);
if (taskInput) {
    taskInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendDirective();
    });
}

if (runCodeBtn) {
    runCodeBtn.addEventListener('click', () => {
        if (!activeFileName) return;
        const filename = activeFileName.textContent;
        if (filename.endsWith('.html')) {
            termPrint("Info: HTML files render automatically in Live Web Preview.", "info");
            return;
        }
        termPrint(`$ initiating build sequence for ${filename}...`, "cmd");
        ws.send(JSON.stringify({ action: "execute", filename, session_id: sessionId }));
    });
}

/* ============================================================
   Tab Switching Logic
============================================================ */
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        e.target.classList.add('active');
        const targetContent = document.getElementById(e.target.dataset.target);
        if (targetContent) targetContent.classList.add('active');

        if (e.target.dataset.target === 'preview-view' && activeFileName && activeFileName.textContent.endsWith('.html')) {
            if (livePreview && codeEditor) {
                livePreview.srcdoc = telemetryScript + codeEditor.value;
            }
        }
    });
});

/* ============================================================
   ZIP Ingestion & Export
============================================================ */
if (zipUpload) {
    zipUpload.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);
        termPrint(`$ upload ${file.name}...`, "cmd");

        try {
            const res = await fetch(`/api/upload/${sessionId}`, { method: 'POST', body: formData });
            const data = await res.json();
            termPrint(data.message, "info");
            refreshFileExplorer();
        } catch (err) {
            termPrint(`Upload failed: ${err.message}`, "err");
        }
    });
}

if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
        termPrint(`$ export zip requested...`, "cmd");
        window.location.href = `/api/download/${sessionId}`;
    });
}

/* ============================================================
   Unified File Explorer Sidebar & Click-to-Open
============================================================ */
async function refreshFileExplorer() {
    const activeSession = window.currentSessionId || sessionId;
    
    // Target both legacy tree containers and new explorers for maximum compatibility
    const containers = [
        document.getElementById('file-tree'),
        document.querySelector('.explorer'),
        document.getElementById('explorer')
    ].filter(Boolean);

    if (containers.length === 0) return;

    try {
        const res = await fetch(`/api/workspace/${activeSession}/files`);
        if (!res.ok) return;
        const data = await res.json();
        
        const fileList = Array.isArray(data) ? data : (data.files || []);

        containers.forEach(container => {
            container.innerHTML = '';

            if (fileList.length === 0) {
                container.innerHTML = '<div style="padding: 10px; color: #888; font-size: 12px;">No files yet</div>';
                return;
            }

            fileList.forEach(filePath => {
                const item = document.createElement('div');
                item.className = 'file-item';
                item.style.padding = "6px 12px";
                item.style.cursor = "pointer";
                item.style.fontSize = "13px";
                item.style.color = "#ccc";
                item.style.whiteSpace = "nowrap";
                item.style.overflow = "hidden";
                item.style.textOverflow = "ellipsis";
                item.textContent = filePath;

                if (activeFileName && filePath === activeFileName.textContent) {
                    item.classList.add('active');
                    item.style.backgroundColor = "#2a2d2e";
                }

                item.addEventListener('click', async () => {
                    try {
                        const codeRes = await fetch(`/api/workspace/${activeSession}/read?file=${encodeURIComponent(filePath)}`);
                        if (!codeRes.ok) return;
                        const code = await codeRes.text();
                        
                        if (codeEditor) codeEditor.value = code;
                        if (activeFileName) activeFileName.textContent = filePath;
                        
                        if (livePreview && filePath.endsWith('.html')) {
                            livePreview.srcdoc = telemetryScript + code;
                        }
                        refreshFileExplorer();
                    } catch (readErr) {
                        termPrint(`Failed to read file ${filePath}: ${readErr.message}`, 'err');
                    }
                });

                container.appendChild(item);
            });
        });
    } catch (e) {
        console.error("Error refreshing file tree:", e);
    }
}

// Poll every 2 seconds to keep sidebar fully synced with D drive workspace
setInterval(refreshFileExplorer, 2000);
