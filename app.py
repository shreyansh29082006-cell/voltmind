"""
app.py — CRAG Electrical Engineering Assistant
Perplexity-inspired Streamlit UI
"""

import streamlit as st
import time
import os

st.set_page_config(
    page_title="VoltMind — EE Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

    from rag_backend import crag_answer, AVAILABLE_MODELS
    BACKEND_AVAILABLE = True
    BACKEND_ERROR = ""
except Exception as e:
    BACKEND_AVAILABLE = False
    BACKEND_ERROR = str(e)


st.markdown("""
<style>
/* ── Google Font Import ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Root Variables ── */
:root {
    --bg-base:       #0a0b0d;
    --bg-surface:    #111318;
    --bg-elevated:   #181c24;
    --bg-input:      #1a1e28;
    --border:        #252a36;
    --border-focus:  #3d6aff;
    --accent:        #3d6aff;
    --accent-glow:   rgba(61, 106, 255, 0.18);
    --accent-soft:   rgba(61, 106, 255, 0.10);
    --text-primary:  #e8eaf0;
    --text-secondary:#8891a8;
    --text-muted:    #525a70;
    --user-bubble:   #1e2640;
    --ai-bubble:     #131720;
    --green:         #22c55e;
    --yellow:        #eab308;
    --red:           #ef4444;
    --font-display:  'Syne', sans-serif;
    --font-body:     'DM Sans', sans-serif;
    --font-mono:     'DM Mono', monospace;
    --radius:        12px;
    --radius-lg:     18px;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
}

/* Remove default Streamlit chrome — keep header only for sidebar toggle */
#MainMenu, footer { display: none !important; }

/* Hide Deploy button and stop/running indicator */
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
button[kind="header"] { display: none !important; }

/* Keep header just tall enough to hold the toggle, nothing else visible */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 48px !important;
    min-height: 48px !important;
    display: flex !important;
    align-items: center !important;
    padding: 0 !important;
    pointer-events: none !important;
}

/* Sidebar toggle — pushed down 48px so it clears the invisible header strip */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarExpandButton"] {
    pointer-events: all !important;
    position: fixed !important;
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-secondary) !important;
    width: 32px !important;
    height: 32px !important;
    top: 48px !important;
    left: 14px !important;
    z-index: 9999 !important;
    transition: all 0.15s ease !important;
}

[data-testid="stSidebarCollapseButton"]:hover,
[data-testid="stSidebarExpandButton"]:hover {
    background: var(--bg-surface) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 12px var(--accent-glow) !important;
}

[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarExpandButton"] svg {
    fill: var(--text-secondary) !important;
    stroke: var(--text-secondary) !important;
}

/* ── App Container ── */
.stApp {
    background-color: var(--bg-base) !important;
    max-width: 100vw;
}

/* ── Main block container ── */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 20px 14px !important;
    height: 100vh;
    display: flex;
    flex-direction: column;
    gap: 0;
}

[data-testid="stSidebar"] .stButton > button {
    font-family: var(--font-body) !important;
}

/* ── Sidebar Logo ── */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 4px 20px 4px;
    margin-bottom: 4px;
    border-bottom: 1px solid var(--border);
}

.sidebar-logo-icon {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #3d6aff, #6b42ff);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}

.sidebar-logo-text {
    font-family: var(--font-display) !important;
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.3px;
}

/* ── New Chat Button ── */
[data-testid="stSidebar"] .stButton:first-of-type > button {
    background: linear-gradient(135deg, var(--accent), #6b42ff) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 16px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 24px var(--accent-glow) !important;
    margin-bottom: 4px !important;
}

[data-testid="stSidebar"] .stButton:first-of-type > button:hover {
    box-shadow: 0 0 32px rgba(61, 106, 255, 0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── Sidebar Section Labels ── */
.sidebar-section-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 16px 4px 8px 4px;
}

/* ── History Buttons ── */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    padding: 8px 10px !important;
    text-align: left !important;
    width: 100% !important;
    font-weight: 400 !important;
    transition: all 0.15s !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--bg-elevated) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
}

/* ── Empty State (Hero) ── */
.hero-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    padding: 40px 20px 160px 20px;
    text-align: center;
    gap: 8px;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--accent-soft);
    border: 1px solid rgba(61, 106, 255, 0.25);
    border-radius: 100px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: 500;
    color: #7a9fff;
    letter-spacing: 0.3px;
    margin-bottom: 12px;
}

.hero-title {
    font-family: var(--font-display) !important;
    font-size: clamp(36px, 5vw, 58px);
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -1.5px;
    background: linear-gradient(135deg, #e8eaf0 30%, #7a9fff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}

.hero-subtitle {
    font-size: 16px;
    color: var(--text-secondary);
    max-width: 460px;
    line-height: 1.6;
    margin: 8px 0 24px 0;
    font-weight: 300;
}

/* ── Suggestion Chips ── */
.chip-grid {
    display: flex;
    gap: 8px;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 80px;
}

.suggestion-chip {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 9px 16px;
    font-size: 12px;
    color: var(--text-secondary);
    font-family: var(--font-mono);
    cursor: pointer;
    transition: all 0.15s ease;
    user-select: none;
}

.suggestion-chip:hover {
    background: var(--accent-soft);
    border-color: rgba(61,106,255,0.35);
    color: #7a9fff;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(61,106,255,0.12);
}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

.msg-bubble {
    border-radius: var(--radius-lg);
    padding: 14px 18px;
    font-size: 15px;
    line-height: 1.65;
    position: relative;
}

.msg-bubble.user-bubble {
    background: var(--user-bubble);
    border: 1px solid rgba(61,106,255,0.2);
    border-bottom-right-radius: 4px;
    color: var(--text-primary);
    max-width: 640px;
    margin-left: auto;
}

.msg-bubble.ai-bubble {
    background: var(--ai-bubble);
    border: 1px solid var(--border);
    border-bottom-left-radius: 4px;
    color: var(--text-primary);
}

/* ── Route Badge ── */
.route-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    font-family: var(--font-mono);
    font-weight: 500;
    border-radius: 100px;
    padding: 3px 10px;
    margin-bottom: 10px;
    letter-spacing: 0.2px;
}

.route-local  { background: rgba(34,197,94,0.12);  border: 1px solid rgba(34,197,94,0.25);  color: #4ade80; }
.route-web    { background: rgba(234,179,8,0.12);   border: 1px solid rgba(234,179,8,0.25);  color: #fbbf24; }
.route-hybrid { background: rgba(61,106,255,0.12);  border: 1px solid rgba(61,106,255,0.25); color: #7a9fff; }

/* ── Message Meta Row (timestamp + copy) ── */
.msg-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 6px;
    padding: 0 2px;
}

.msg-timestamp {
    font-size: 10px;
    color: var(--text-muted);
    font-family: var(--font-mono);
}

.copy-btn {
    font-size: 11px;
    color: var(--text-muted);
    font-family: var(--font-mono);
    cursor: pointer;
    padding: 2px 7px;
    border-radius: 5px;
    border: 1px solid transparent;
    background: transparent;
    transition: all 0.15s;
    user-select: none;
}

.copy-btn:hover {
    color: var(--text-secondary);
    border-color: var(--border);
    background: var(--bg-elevated);
}

/* ── Standalone question pill ── */
.interpreted-as {
    font-size: 11px;
    font-family: var(--font-mono);
    color: var(--text-muted);
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 4px 10px;
    margin-bottom: 10px;
    display: inline-block;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.interpreted-as span {
    color: var(--text-secondary);
}

/* ── Source chips ── */
.source-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 3px 9px;
    font-size: 11px;
    font-family: var(--font-mono);
    color: var(--text-secondary);
    margin: 3px 3px 0 0;
}

.source-chip.correct   { border-color: rgba(34,197,94,0.3);  color: #4ade80; }
.source-chip.ambiguous { border-color: rgba(234,179,8,0.3);  color: #fbbf24; }
.source-chip.incorrect { border-color: rgba(239,68,68,0.3);  color: #f87171; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

[data-testid="stExpander"] summary {
    color: var(--text-secondary) !important;
    font-size: 13px !important;
    font-family: var(--font-mono) !important;
}

/* ── Thinking Indicator ── */
.thinking-dots {
    display: inline-flex;
    gap: 4px;
    align-items: center;
    padding: 4px 0;
}

.thinking-dots span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent);
    animation: blink 1.2s ease-in-out infinite;
}

.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
    0%, 80%, 100% { opacity: 0.2; transform: scale(0.85); }
    40%            { opacity: 1;   transform: scale(1);    }
}

/* ── Selectbox (model picker) ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: 13px !important;
}

[data-testid="stSelectbox"] label {
    color: var(--text-muted) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

[data-testid="stChatInput"] > div {
    background: transparent !important;
    border: none !important;
}

[data-testid="stChatInputTextField"] {
    background: transparent !important;
    border: none !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: 15px !important;
    padding: 10px 12px !important;
}

[data-testid="stChatInputTextField"]::placeholder {
    color: var(--text-muted) !important;
}

[data-testid="stChatInputSubmitButton"] {
    background: var(--accent) !important;
    border-radius: 8px !important;
    border: none !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 4px 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* ── Status bar ── */
.status-bar {
    font-size: 11px;
    color: var(--text-muted);
    font-family: var(--font-mono);
    text-align: center;
    padding: 4px 0 0 0;
}

/* ── Notification banner ── */
.info-banner {
    background: var(--accent-soft);
    border: 1px solid rgba(61,106,255,0.25);
    border-radius: var(--radius);
    padding: 10px 16px;
    font-size: 13px;
    color: #7a9fff;
    margin-bottom: 8px;
    font-family: var(--font-mono);
}

/* ── Input hint ── */
.input-hint {
    font-size: 11px;
    color: var(--text-muted);
    font-family: var(--font-mono);
    text-align: center;
    padding: 4px 0 0 0;
}

/* ── Delete button in history ── */
.del-btn > button {
    background: transparent !important;
    border: none !important;
    color: var(--text-muted) !important;
    font-size: 12px !important;
    padding: 4px 6px !important;
    min-height: unset !important;
    height: 28px !important;
    width: 28px !important;
    transition: color 0.15s !important;
}

.del-btn > button:hover {
    color: #f87171 !important;
    background: rgba(239,68,68,0.08) !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

# ── JS: copy-to-clipboard + chip click + auto-scroll ─────────
st.markdown("""
<script>
// Copy to clipboard
function copyText(text, btnId) {
    navigator.clipboard.writeText(text).then(function() {
        const btn = document.getElementById(btnId);
        if (btn) {
            const orig = btn.innerText;
            btn.innerText = '✓ copied';
            btn.style.color = '#4ade80';
            setTimeout(() => { btn.innerText = orig; btn.style.color = ''; }, 1800);
        }
    });
}

// Auto-scroll to bottom of chat
function scrollToBottom() {
    const sections = window.parent.document.querySelectorAll('section[data-testid="stMain"]');
    sections.forEach(el => { el.scrollTop = el.scrollHeight; });
}

// Chip click → fill input and submit
function fillInput(text) {
    const inputs = window.parent.document.querySelectorAll('textarea[data-testid="stChatInputTextField"]');
    if (inputs.length > 0) {
        const nativeInput = inputs[0];
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, 'value').set;
        nativeInputValueSetter.call(nativeInput, text);
        nativeInput.dispatchEvent(new Event('input', { bubbles: true }));
        nativeInput.focus();
    }
}

// Run scroll on load and after any DOM change
document.addEventListener('DOMContentLoaded', scrollToBottom);
setTimeout(scrollToBottom, 400);
setTimeout(scrollToBottom, 900);
</script>
""", unsafe_allow_html=True)


if "conversations" not in st.session_state:
    st.session_state.conversations = []   

if "active_conv" not in st.session_state:
    st.session_state.active_conv = None  

if "model_key" not in st.session_state:
    if BACKEND_AVAILABLE:
        st.session_state.model_key = list(AVAILABLE_MODELS.keys())[0]
    else:
        st.session_state.model_key = "Demo Mode"

if "pending_chip" not in st.session_state:
    st.session_state.pending_chip = ""    

def current_messages() -> list:
    if st.session_state.active_conv is None:
        return []
    return st.session_state.conversations[st.session_state.active_conv]["messages"]


def start_new_chat():
    st.session_state.active_conv = None
    st.session_state.pending_chip = ""


def derive_title(question: str) -> str:
    words = question.strip().split()
    title = " ".join(words[:6])
    return title + ("…" if len(words) > 6 else "")


def delete_conversation(idx: int):
    st.session_state.conversations.pop(idx)
    if st.session_state.active_conv == idx:
        st.session_state.active_conv = None
    elif st.session_state.active_conv is not None and st.session_state.active_conv > idx:
        st.session_state.active_conv -= 1




with st.sidebar:
    # Logo
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">⚡</div>
        <span class="sidebar-logo-text">VoltMind</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("＋  New Chat", key="new_chat_btn", use_container_width=True):
        start_new_chat()
        st.rerun()


    st.markdown('<div class="sidebar-section-label">Model</div>', unsafe_allow_html=True)
    model_options = list(AVAILABLE_MODELS.keys()) if BACKEND_AVAILABLE else ["Demo Mode"]
    selected_model = st.selectbox(
        label="model_select",
        options=model_options,
        index=0,
        label_visibility="collapsed",
        key="model_select"
    )
    st.session_state.model_key = selected_model

    st.markdown('<div class="sidebar-section-label">History</div>', unsafe_allow_html=True)

    if not st.session_state.conversations:
        st.markdown(
            '<p style="font-size:12px;color:var(--text-muted);padding:4px 4px;">No conversations yet</p>',
            unsafe_allow_html=True
        )
    else:
        
        for i, conv in enumerate(reversed(st.session_state.conversations)):
            real_idx = len(st.session_state.conversations) - 1 - i
            is_active = st.session_state.active_conv == real_idx

            col_title, col_del = st.columns([5, 1])
            with col_title:
                label = ("💬 " if is_active else "○  ") + conv["title"]
                if st.button(label, key=f"hist_{real_idx}", use_container_width=True):
                    st.session_state.active_conv = real_idx
                    st.rerun()
            with col_del:
                st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                if st.button("✕", key=f"del_{real_idx}"):
                    delete_conversation(real_idx)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    
    st.markdown("---")
    backend_status = "🟢 Backend ready" if BACKEND_AVAILABLE else "🔴 Backend offline"
    st.markdown(f'<div class="status-bar">{backend_status}</div>', unsafe_allow_html=True)

    last_route = ""
    if st.session_state.active_conv is not None:
        last_route = st.session_state.conversations[st.session_state.active_conv].get("last_route", "")
    route_map = {"local": "📂 Local Docs", "web": "🌐 Web Search", "hybrid": "🔀 Hybrid"}
    pipeline_label = route_map.get(last_route, "CRAG + Hybrid Search")
    st.markdown(f'<div class="status-bar">{pipeline_label}</div>', unsafe_allow_html=True)


messages = current_messages()
is_empty = len(messages) == 0

if not BACKEND_AVAILABLE and BACKEND_ERROR:
    st.markdown(
        f'<div class="info-banner">⚠️ Backend not loaded — '
        f'<code>{BACKEND_ERROR[:80]}</code>. Running in demo mode.</div>',
        unsafe_allow_html=True
    )

if is_empty:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">⚡ Electrical Engineering RAG</div>
        <h1 class="hero-title">What do you want<br>to understand?</h1>
        <p class="hero-subtitle">Ask anything about circuits, power systems, signal processing,
        or electrical standards — powered by your documents and the web.</p>
    </div>
    """, unsafe_allow_html=True)


    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    CHIPS = [
        "⚡ Three-phase transformer losses",
        "📡 5G antenna beamforming",
        "🔋 Battery management systems",
        "📊 PID controller design",
        "🔌 Power factor correction",
        "📐 Bode plot analysis",
    ]

    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        chip_cols = st.columns(3)
        for idx, chip_text in enumerate(CHIPS):
            with chip_cols[idx % 3]:
            
                btn_key = f"chip_{idx}"
                st.markdown(
                    f'<div class="suggestion-chip" onclick="fillInput(\'{chip_text}\')">'
                    f'{chip_text}</div>',
                    unsafe_allow_html=True
                )
        
        
        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
        btn_row1 = st.columns(3)
        for idx, chip_text in enumerate(CHIPS):
            with btn_row1[idx % 3]:
                if st.button(chip_text, key=f"chipbtn_{idx}", use_container_width=True):
                    st.session_state.pending_chip = chip_text
                    st.rerun()

    st.markdown('<div style="height:80px"></div>', unsafe_allow_html=True)


else:
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    for msg_idx, msg in enumerate(messages):
        if msg["role"] == "user":
            with st.chat_message("user"):
                ts = msg.get("timestamp", "")
                content = msg["content"]
                copy_id = f"copy_u_{msg_idx}"
                st.markdown(
                    f'<div class="msg-bubble user-bubble">{content}</div>'
                    f'<div class="msg-meta" style="justify-content:flex-end;">'
                    f'  <span class="msg-timestamp">{ts}</span>'
                    f'  <button class="copy-btn" id="{copy_id}" '
                    f'    onclick="copyText(`{content.replace(chr(96), chr(39))}`, \'{copy_id}\')">'
                    f'    ⎘ copy</button>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        else:
            with st.chat_message("assistant"):
                route          = msg.get("route", "local")
                standalone_q   = msg.get("standalone_q", "")
                evaluations    = msg.get("evaluations", [])
                ts             = msg.get("timestamp", "")
                content        = msg["content"]
                copy_id        = f"copy_a_{msg_idx}"

                route_icons  = {"local": "📂", "web": "🌐", "hybrid": "🔀"}
                route_labels = {"local": "Local Docs", "web": "Web Search", "hybrid": "Hybrid"}


                st.markdown(
                    f'<span class="route-badge route-{route}">'
                    f'{route_icons.get(route,"⚡")} {route_labels.get(route, route.title())}'
                    f'</span>',
                    unsafe_allow_html=True
                )

                
                if standalone_q and standalone_q.strip() != msg.get("original_q", "").strip():
                    safe_q = standalone_q[:120] + ("…" if len(standalone_q) > 120 else "")
                    st.markdown(
                        f'<div class="interpreted-as">🔍 interpreted as: <span>{safe_q}</span></div>',
                        unsafe_allow_html=True
                    )

        
                st.markdown(content)

            
                safe_content = content.replace("`", "'").replace("\n", " ")[:300]
                st.markdown(
                    f'<div class="msg-meta">'
                    f'  <span class="msg-timestamp">{ts}</span>'
                    f'  <button class="copy-btn" id="{copy_id}" '
                    f'    onclick="copyText(`{safe_content}`, \'{copy_id}\')">'
                    f'    ⎘ copy</button>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        
                if evaluations:
                    correct_n   = sum(1 for e in evaluations if e["label"] == "correct")
                    ambiguous_n = sum(1 for e in evaluations if e["label"] == "ambiguous")
                    incorrect_n = sum(1 for e in evaluations if e["label"] == "incorrect")
                    with st.expander(
                        f"📎 {len(evaluations)} sources — "
                        f"✓{correct_n} ~{ambiguous_n} ✗{incorrect_n}",
                        expanded=False
                    ):
                        seen = set()
                        for item in evaluations:
                            doc    = item["doc"]
                            label  = item["label"]
                            score  = item.get("score", 0)
                            source = os.path.basename(doc.metadata.get("source", "unknown"))
                            page   = doc.metadata.get("page", "?")
                            key    = f"{source}|{page}"
                            if key not in seen:
                                seen.add(key)
                                icon = {"correct": "✓", "ambiguous": "~", "incorrect": "✗"}.get(label, "?")
                                st.markdown(
                                    f'<span class="source-chip {label}">'
                                    f'{icon} {source} p.{page} ({score:.2f})</span>',
                                    unsafe_allow_html=True
                                )

    
    st.markdown("<div style='height:110px'></div>", unsafe_allow_html=True)


    st.markdown(
        "<script>setTimeout(function(){"
        "var el=window.parent.document.querySelector('[data-testid=\"stMain\"]');"
        "if(el){el.scrollTop=el.scrollHeight;}},200);</script>",
        unsafe_allow_html=True
    )




col_left, col_mid, col_right = st.columns([1, 4, 1])
with col_mid:
    st.markdown(
        f'<div style="text-align:center;font-size:11px;color:var(--text-muted);'
        f'font-family:var(--font-mono);margin-bottom:-8px;">'
        f'model: {st.session_state.model_key}</div>',
        unsafe_allow_html=True
    )


chat_input_value = st.session_state.get("pending_chip", "")

question = st.chat_input(
    placeholder="Ask anything about electrical engineering…  (Shift+Enter for newline)",
    key="main_input"
)

if st.session_state.pending_chip:
    
    question = st.session_state.pending_chip
    st.session_state.pending_chip = ""

col_l2, col_m2, col_r2 = st.columns([1, 4, 1])
with col_m2:
    st.markdown(
        '<div class="input-hint">Shift+Enter for newline · Enter to send</div>',
        unsafe_allow_html=True
    )



if question and question.strip():
    import datetime
    ts_now = datetime.datetime.now().strftime("%H:%M")

    
    if st.session_state.active_conv is None:
        new_conv = {
            "title"      : derive_title(question),
            "messages"   : [],
            "last_route" : "",
        }
        st.session_state.conversations.append(new_conv)
        st.session_state.active_conv = len(st.session_state.conversations) - 1

    messages = current_messages()

    
    messages.append({
        "role"      : "user",
        "content"   : question,
        "timestamp" : ts_now,
    })

    
    with st.chat_message("user"):
        copy_id = f"copy_u_live"
        st.markdown(
            f'<div class="msg-bubble user-bubble">{question}</div>'
            f'<div class="msg-meta" style="justify-content:flex-end;">'
            f'  <span class="msg-timestamp">{ts_now}</span>'
            f'  <button class="copy-btn" id="{copy_id}" '
            f'    onclick="copyText(`{question.replace(chr(96), chr(39))}`, \'{copy_id}\')">'
            f'    ⎘ copy</button>'
            f'</div>',
            unsafe_allow_html=True
        )


    with st.chat_message("assistant"):
        thinking_slot = st.empty()
        thinking_slot.markdown(
            '<div class="msg-bubble ai-bubble" style="display:inline-block;">'
            '<div class="thinking-dots"><span></span><span></span><span></span></div>'
            '</div>',
            unsafe_allow_html=True
        )

        
        if BACKEND_AVAILABLE:
            try:
                model_name = AVAILABLE_MODELS[st.session_state.model_key]
                result = crag_answer(
                    raw_question=question,
                    chat_history=messages[:-1],
                    model_name=model_name,
                )
                answer       = result["answer"]
                route        = result["route"]
                evaluations  = result["evaluations"]
                standalone_q = result["standalone_q"]
            except Exception as e:
                answer       = f"⚠️ Error calling backend: `{e}`"
                route        = "local"
                evaluations  = []
                standalone_q = question
        else:
            time.sleep(0.8)
            answer = (
                "**Demo mode** — backend not loaded.\n\n"
                "This is where your CRAG answer would appear. "
                "Connect your `rag_backend.py` to see real results."
            )
            route        = "local"
            evaluations  = []
            standalone_q = question

        thinking_slot.empty()


    messages.append({
        "role"        : "assistant",
        "content"     : answer,
        "route"       : route,
        "evaluations" : evaluations,
        "standalone_q": standalone_q,
        "original_q"  : question,
        "timestamp"   : ts_now,
    })

    conv = st.session_state.conversations[st.session_state.active_conv]
    conv["last_route"] = route
    
    if len(messages) == 2:
        conv["title"] = derive_title(question)

    st.rerun()
