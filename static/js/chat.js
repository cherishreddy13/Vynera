/**
 * static/js/chat.js  — VYNERA AI
 * Complete rewrite fixing:
 *   - WebSocket reconnect loop (was reconnecting every 3s even when tab active)
 *   - Conversation not loaded on page open (was creating new conv every time)
 *   - conv_id from URL param ?conv=... not being read
 *   - New conversation button broken
 *   - Sidebar memories/goals not loading
 *   - Feedback submitting wrong user_message/bot_response pair
 *   - Typing indicator not hiding on error
 *   - Mode tabs not updating placeholder
 */

const API   = "";
const token = localStorage.getItem("vynera_token");
const user  = JSON.parse(localStorage.getItem("vynera_user") || "{}");

// ── State ─────────────────────────────────────────────────────────────────────
let ws            = null;
let currentConvId = null;
let currentMode   = "chat";
let lastUserMsg   = "";
let lastBotMsg    = "";
let wsConnected   = false;
let reconnectTimer = null;

// ── DOM refs ──────────────────────────────────────────────────────────────────
const messagesEl      = () => document.getElementById("messages");
const inputEl         = () => document.getElementById("messageInput");
const sendBtnEl       = () => document.getElementById("sendBtn");
const typingEl        = () => document.getElementById("typingIndicator");
const emotionBadgeEl  = () => document.getElementById("emotionBadge");
const connStatusEl    = () => document.getElementById("connStatus");
const sidebarMemEl    = () => document.getElementById("sidebarMemories");
const sidebarGoalsEl  = () => document.getElementById("sidebarGoals");

// ── Boot ──────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  if (!token) { window.location.href = "/login"; return; }
  setupModeTabs();
  setupInput();
  setupNewChatBtn();
  init();
});

async function init() {
  // Check URL for a specific conversation id (?conv=...)
  const params = new URLSearchParams(window.location.search);
  const convParam = params.get("conv");

  if (convParam) {
    currentConvId = convParam;
    await loadConversationMessages(currentConvId);
  } else {
    // Load most recent conversation or create new
    const convs = await apiGet("/api/conversations");
    if (convs && convs.length > 0) {
      currentConvId = convs[0]._id;
      await loadConversationMessages(currentConvId);
    } else {
      currentConvId = await createNewConv();
      appendSystem("Welcome. I'm VYNERA — your companion. Share what's on your mind.");
    }
  }

  connectWS();
  loadSidebar();
}

// ── API helpers ───────────────────────────────────────────────────────────────
async function apiGet(path) {
  try {
    const r = await fetch(API + path, { headers: { Authorization: "Bearer " + token } });
    if (r.status === 401) { window.location.href = "/login"; return null; }
    return await r.json();
  } catch { return null; }
}

async function apiPost(path, body) {
  try {
    const r = await fetch(API + path, {
      method: "POST",
      headers: { Authorization: "Bearer " + token, "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (r.status === 401) { window.location.href = "/login"; return null; }
    return await r.json();
  } catch { return null; }
}

async function createNewConv() {
  const data = await apiPost("/api/conversations", {});
  return data ? data.conv_id : null;
}

// ── Load existing messages ────────────────────────────────────────────────────
async function loadConversationMessages(convId) {
  const conv = await apiGet(`/api/conversations/${convId}`);
  if (!conv || !conv.messages) return;
  const msgs = conv.messages;
  if (msgs.length === 0) {
    appendSystem("Welcome back. What's on your mind?");
    return;
  }
  msgs.forEach(msg => {
    if (msg.role === "user") appendUserBubble(msg.content, false);
    else if (msg.role === "assistant") appendBotBubble(msg.content, null, false);
  });
  scrollBottom();
}

// ── WebSocket ─────────────────────────────────────────────────────────────────
function connectWS() {
  if (!currentConvId || !token) return;
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;

  clearTimeout(reconnectTimer);
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws/chat/${currentConvId}?token=${encodeURIComponent(token)}`);

  ws.onopen = () => {
    wsConnected = true;
    setStatus(true);
  };

  ws.onmessage = (evt) => {
    let data;
    try { data = JSON.parse(evt.data); } catch { return; }

    if (data.type === "typing") {
      showTyping(data.value);
    } else if (data.type === "response") {
      showTyping(false);
      appendBotBubble(data.message, data.emotion, true);
      if (data.emotion) updateEmotionBadge(data.emotion);
      if (data.new_memories && data.new_memories.length) loadSidebar();
      enableInput(true);
    } else if (data.type === "error") {
      showTyping(false);
      appendSystem("⚠ " + (data.message || "An error occurred."));
      enableInput(true);
    }
  };

  ws.onclose = () => {
    wsConnected = false;
    setStatus(false);
    // Reconnect after 4 seconds if page still visible
    reconnectTimer = setTimeout(() => {
      if (document.visibilityState !== "hidden") connectWS();
    }, 4000);
  };

  ws.onerror = () => {
    wsConnected = false;
    setStatus(false);
  };
}

// ── Send message ──────────────────────────────────────────────────────────────
function sendMessage() {
  const inp = inputEl();
  const text = inp.value.trim();
  if (!text) return;

  if (!wsConnected || !ws || ws.readyState !== WebSocket.OPEN) {
    appendSystem("Reconnecting... please wait a moment and try again.");
    connectWS();
    return;
  }

  lastUserMsg = text;
  appendUserBubble(text, true);
  inp.value = "";
  inp.style.height = "auto";
  enableInput(false);
  showTyping(true);

  ws.send(JSON.stringify({ message: text, mode: currentMode }));
}

// ── New conversation ──────────────────────────────────────────────────────────
function setupNewChatBtn() {
  const btn = document.getElementById("newChatBtn");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    // Close current WS
    if (ws) { ws.onclose = null; ws.close(); ws = null; }
    clearTimeout(reconnectTimer);
    wsConnected = false;

    // Clear messages
    const el = messagesEl();
    if (el) el.innerHTML = "";

    // Create new conversation
    currentConvId = await createNewConv();
    if (!currentConvId) { appendSystem("Failed to create conversation."); return; }

    // Update URL without reloading
    window.history.pushState({}, "", "/chat");

    appendSystem("New conversation started. I'm here — what's on your mind?");
    connectWS();
  });
}

// ── Render messages ───────────────────────────────────────────────────────────
function appendUserBubble(text, scroll = true) {
  const el = messagesEl();
  if (!el) return;
  const div = document.createElement("div");
  div.className = "msg-row user";
  div.innerHTML = `
    <div class="avatar user">${escHtml((user.name || "U")[0].toUpperCase())}</div>
    <div class="bubble user">${escHtml(text)}</div>`;
  el.appendChild(div);
  if (scroll) scrollBottom();
}

function appendBotBubble(text, emotion, scroll = true) {
  lastBotMsg = text;
  const el = messagesEl();
  if (!el) return;
  const emotionLabel = emotion ? emotion.emotion : "";
  const div = document.createElement("div");
  div.className = "msg-row bot";
  div.innerHTML = `
    <div class="avatar bot">V</div>
    <div>
      <div class="bubble bot">${renderMd(text)}</div>
      <div class="feedback-row">
        <button class="fb-btn up" onclick="sendFeedback(this,1)" title="Helpful">👍</button>
        <button class="fb-btn down" onclick="sendFeedback(this,-1)" title="Not helpful">👎</button>
        ${emotionLabel ? `<span style="font-size:10px;color:var(--muted);margin-left:4px;font-family:'JetBrains Mono',monospace">${emotionLabel}</span>` : ""}
      </div>
    </div>`;
  el.appendChild(div);
  if (scroll) scrollBottom();
}

function appendSystem(text) {
  const el = messagesEl();
  if (!el) return;
  const div = document.createElement("div");
  div.style.cssText = "text-align:center;padding:8px 0;font-size:12px;color:var(--muted);font-family:'JetBrains Mono',monospace;";
  div.textContent = text;
  el.appendChild(div);
  scrollBottom();
}

// ── Markdown (bold + italic + newlines) ───────────────────────────────────────
function renderMd(text) {
  return escHtml(text)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");
}

function escHtml(s) {
  return String(s)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

// ── Feedback ──────────────────────────────────────────────────────────────────
async function sendFeedback(btn, rating) {
  const row = btn.closest(".feedback-row");
  row.querySelectorAll(".fb-btn").forEach(b => { b.disabled = true; b.style.opacity = "0.4"; });
  btn.style.opacity = "1";
  btn.classList.add(rating === 1 ? "voted-up" : "voted-down");

  await apiPost("/api/feedback", {
    conv_id:      currentConvId,
    user_message: lastUserMsg,
    bot_response: lastBotMsg,
    rating,
  });
}

// ── Emotion badge ─────────────────────────────────────────────────────────────
function updateEmotionBadge(emotion) {
  const el = emotionBadgeEl();
  if (!el || !emotion) return;
  const icons = { happiness:"✦", sadness:"◈", anxiety:"◉", anger:"◆", neutral:"○" };
  el.textContent = `${icons[emotion.emotion] || "○"} ${emotion.emotion}`;
}

// ── Status ────────────────────────────────────────────────────────────────────
function setStatus(connected) {
  const el = connStatusEl();
  if (el) el.textContent = connected ? "Connected · VYNERA is ready" : "Reconnecting...";
}

// ── Typing indicator ──────────────────────────────────────────────────────────
function showTyping(show) {
  const el = typingEl();
  if (!el) return;
  el.classList.toggle("show", show);
  if (show) scrollBottom();
}

// ── Enable/disable input ──────────────────────────────────────────────────────
function enableInput(enabled) {
  const inp = inputEl();
  const btn = sendBtnEl();
  if (inp) inp.disabled = !enabled;
  if (btn) btn.disabled = !enabled;
}

// ── Mode tabs ─────────────────────────────────────────────────────────────────
function setupModeTabs() {
  const placeholders = {
    chat:    "Say anything...",
    journal: "Write freely. This is your space...",
    goals:   "Tell me about a goal you want to work on...",
    reason:  "Describe the decision or problem to think through...",
  };
  document.querySelectorAll(".mode-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".mode-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      currentMode = tab.dataset.mode;
      const inp = inputEl();
      if (inp) inp.placeholder = placeholders[currentMode] || "Say anything...";
    });
  });
}

// ── Input setup ───────────────────────────────────────────────────────────────
function setupInput() {
  const btn = sendBtnEl();
  if (btn) btn.addEventListener("click", sendMessage);

  const inp = inputEl();
  if (!inp) return;

  inp.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });
  inp.addEventListener("input", () => {
    inp.style.height = "auto";
    inp.style.height = Math.min(inp.scrollHeight, 140) + "px";
  });
}

// ── Sidebar ───────────────────────────────────────────────────────────────────
async function loadSidebar() {
  // Memories
  const memEl = sidebarMemEl();
  if (memEl) {
    const mems = await apiGet("/api/memories");
    if (mems && mems.length) {
      memEl.innerHTML = mems.slice(0, 5).map(m => `
        <div class="mem-chip">
          <div class="mem-k">${escHtml((m.key || "").replace(/_/g," "))}</div>
          <div class="mem-v">${escHtml(m.value)}</div>
        </div>`).join("");
    } else {
      memEl.innerHTML = `<div style="color:var(--muted);font-size:11px">Chat to build memories.</div>`;
    }
  }

  // Goals
  const goalEl = sidebarGoalsEl();
  if (goalEl) {
    const goals = await apiGet("/api/goals?status=active");
    if (goals && goals.length) {
      goalEl.innerHTML = goals.slice(0, 4).map(g => `
        <div class="goal-mini">
          <div class="goal-mini-name" style="font-size:11px;color:var(--text);margin-bottom:4px">${escHtml(g.title)}</div>
          <div class="mini-bar"><div class="mini-fill" style="width:${g.progress}%"></div></div>
          <div style="font-size:10px;color:var(--muted);margin-top:3px">${g.progress}%</div>
        </div>`).join("");
    } else {
      goalEl.innerHTML = `<div style="color:var(--muted);font-size:11px">No active goals.</div>`;
    }
  }
}

// ── Scroll ────────────────────────────────────────────────────────────────────
function scrollBottom() {
  const el = messagesEl();
  if (el) el.scrollTop = el.scrollHeight;
}