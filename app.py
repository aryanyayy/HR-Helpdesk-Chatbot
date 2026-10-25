import csv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="HR Helpdesk",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# THEME
# ============================================================

st.markdown("""
<style>
:root {
    --bg: #07111f;
    --bg-2: #0b1728;
    --panel: rgba(15, 29, 49, 0.78);
    --panel-strong: rgba(18, 36, 59, 0.94);
    --panel-soft: rgba(20, 39, 63, 0.55);
    --line: rgba(154, 193, 228, 0.17);
    --line-bright: rgba(109, 231, 245, 0.32);
    --text: #eef7ff;
    --muted: #9bb1c8;
    --muted-2: #71879e;
    --cyan: #6de7f5;
    --purple: #9a8cff;
    --green: #6ee7b7;
    --yellow: #f7d774;
    --orange: #ffad70;
    --red: #ff7d8d;
}

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background:
        radial-gradient(circle at 7% 15%, rgba(30, 133, 165, .17), transparent 27%),
        radial-gradient(circle at 88% 20%, rgba(104, 77, 191, .16), transparent 28%),
        radial-gradient(circle at 65% 92%, rgba(31, 115, 151, .09), transparent 28%),
        linear-gradient(145deg, #06101d 0%, #091625 52%, #0b1223 100%) !important;
    min-height: 100vh;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu, footer {
    visibility: hidden;
}

.block-container {
    max-width: 1380px;
    padding: 1.2rem 4.2% 5rem;
}

.stApp h1, .stApp h2, .stApp h3,
.stApp p, .stApp span, .stApp label {
    color: var(--text);
}

[data-testid="stMarkdownContainer"] p {
    color: inherit;
}

/* ---------- top navigation ---------- */

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 0 20px;
    border-bottom: 1px solid var(--line);
    margin-bottom: 25px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-icon {
    width: 42px;
    height: 42px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #06101d;
    background: linear-gradient(135deg, var(--cyan), #79bfff);
    box-shadow: 0 0 28px rgba(109, 231, 245, .24);
    font-size: 20px;
    font-weight: 900;
}

.brand-name {
    font-size: 18px;
    font-weight: 800;
}

/* ---------- hero ---------- */

.hero {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--line-bright);
    border-radius: 24px;
    padding: 31px 34px 30px;
    background:
        radial-gradient(circle at 90% 5%, rgba(109,231,245,.13), transparent 30%),
        linear-gradient(125deg, rgba(25,35,77,.88), rgba(8,29,45,.92));
    box-shadow: 0 24px 70px rgba(0,0,0,.25);
}

.hero-kicker {
    color: var(--cyan);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2.2px;
    text-transform: uppercase;
}

.hero h1 {
    margin: 9px 0 8px;
    font-size: clamp(35px, 4.2vw, 58px);
    line-height: 1;
    letter-spacing: -2.5px;
}

.hero h1 span {
    color: var(--cyan);
}

.hero p {
    color: #b5c8dc !important;
    max-width: 720px;
    font-size: 15px;
    line-height: 1.65;
    margin-bottom: 19px;
}

.pills {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.pill {
    border: 1px solid rgba(154,140,255,.28);
    background: rgba(154,140,255,.09);
    color: #cbd2ff;
    padding: 7px 11px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
}

/* ---------- access / stats ---------- */

.access-card, .stat-card, .info-card, .chat-shell {
    border: 1px solid var(--line);
    background: var(--panel);
    border-radius: 18px;
    box-shadow: 0 16px 45px rgba(0,0,0,.16);
    backdrop-filter: blur(14px);
}

.access-card {
    padding: 20px;
    margin-top: 18px;
}

.access-title {
    color: var(--muted-2);
    text-transform: uppercase;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.2px;
}

.access-name {
    font-size: 19px;
    font-weight: 800;
    margin-top: 6px;
}

.access-meta {
    color: var(--muted) !important;
    font-size: 12px;
    margin-top: 5px;
}

.role-pill {
    display: inline-block;
    margin-top: 12px;
    padding: 6px 10px;
    border-radius: 999px;
    color: var(--cyan) !important;
    background: rgba(109,231,245,.08);
    border: 1px solid rgba(109,231,245,.25);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .7px;
    text-transform: uppercase;
}

.stat-card {
    padding: 18px 19px;
    min-height: 105px;
}

.stat-label {
    color: var(--muted) !important;
    font-size: 11px;
}

.stat-number {
    font-size: 30px;
    font-weight: 800;
    margin-top: 7px;
    letter-spacing: -1px;
}

.stat-caption {
    color: var(--muted-2) !important;
    font-size: 10px;
    margin-top: 2px;
}

/* ---------- sections ---------- */

.section-title {
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -.7px;
    margin: 27px 0 13px;
}

.section-subtitle {
    color: var(--muted) !important;
    font-size: 13px;
    margin-top: -6px;
    margin-bottom: 13px;
}

/* Quick question buttons */
.stButton > button {
    width: 100%;
    min-height: 48px;
    color: #eaf6ff !important;
    background: linear-gradient(145deg, rgba(21,34,53,.92), rgba(12,24,41,.92));
    border: 1px solid rgba(154,193,228,.19);
    border-radius: 13px;
    font-weight: 650;
    text-align: left;
    padding: 0 15px;
    transition: transform .15s ease, border-color .15s ease, background .15s ease;
}

.stButton > button:hover {
    color: white !important;
    border-color: rgba(109,231,245,.45);
    background: linear-gradient(145deg, rgba(25,47,70,.98), rgba(13,29,47,.98));
    transform: translateY(-1px);
}

.logout-btn button {
    min-height: 40px !important;
    color: #07111f !important;
    background: linear-gradient(100deg, var(--cyan), #a69aff) !important;
    border: 0 !important;
    text-align: center !important;
}

/* ---------- how it works ---------- */

.info-card {
    padding: 19px 21px;
    height: 100%;
}

.step {
    display: flex;
    gap: 13px;
    margin: 13px 0;
}

.step-num {
    min-width: 28px;
    height: 28px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(109,231,245,.1);
    border: 1px solid rgba(109,231,245,.24);
    color: var(--cyan);
    font-weight: 800;
    font-size: 12px;
}

.step-text {
    padding-top: 3px;
    font-size: 13px;
    color: #d7e5f2;
}

/* ---------- chat ---------- */

.chat-shell {
    padding: 9px;
    margin-top: 20px;
}

[data-testid="stChatMessage"] {
    background: rgba(14,28,47,.86) !important;
    border: 1px solid var(--line) !important;
    border-radius: 15px !important;
    margin: 8px 0 !important;
}

[data-testid="stChatMessage"] * {
    color: var(--text) !important;
}

[data-testid="stChatInput"] {
    background: rgba(15,29,49,.94) !important;
    border: 1px solid rgba(154,193,228,.22) !important;
    border-radius: 15px !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: rgba(109,231,245,.62) !important;
    box-shadow: 0 0 0 3px rgba(109,231,245,.08) !important;
}

[data-testid="stChatInput"] textarea {
    color: var(--text) !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #71869e !important;
}

/* confidence */
.confidence {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    margin-top: 10px;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .25px;
}

.conf-high {
    color: var(--green);
    background: rgba(110,231,183,.08);
    border: 1px solid rgba(110,231,183,.25);
}

.conf-medium {
    color: var(--yellow);
    background: rgba(247,215,116,.08);
    border: 1px solid rgba(247,215,116,.25);
}

.conf-low {
    color: var(--orange);
    background: rgba(255,173,112,.08);
    border: 1px solid rgba(255,173,112,.25);
}

.conf-very-low {
    color: var(--red);
    background: rgba(255,125,141,.08);
    border: 1px solid rgba(255,125,141,.25);
}

.sources-label {
    color: var(--muted-2) !important;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 800;
    margin-top: 11px;
}

.source-box {
    margin-top: 6px;
    padding: 9px 11px;
    border-radius: 10px;
    background: rgba(8,18,31,.75);
    border: 1px solid var(--line);
    color: #afc2d5 !important;
    font-size: 11px;
    line-height: 1.45;
}

/* welcome card */
.welcome-card {
    border: 1px solid rgba(109,231,245,.17);
    background: linear-gradient(135deg, rgba(20,45,65,.65), rgba(13,25,44,.55));
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 10px;
}

.welcome-title {
    font-size: 16px;
    font-weight: 750;
}

.welcome-copy {
    color: var(--muted) !important;
    font-size: 12px;
    margin-top: 4px;
}

/* divider */
hr {
    border-color: var(--line) !important;
}

/* login-specific */
.login-card {
    border: 1px solid rgba(159,202,237,.22);
    border-radius: 22px;
    padding: 28px;
    background: linear-gradient(145deg, rgba(21,41,67,.88), rgba(13,27,46,.82));
    box-shadow: 0 24px 70px rgba(0,0,0,.28);
}

.stTextInput label {
    color: #bdcee0 !important;
    font-size: 12px;
}

div[data-baseweb="input"] {
    background: rgba(7,17,31,.7) !important;
    border: 1px solid rgba(154,193,228,.2) !important;
    border-radius: 11px !important;
}

div[data-baseweb="input"] input {
    color: var(--text) !important;
}

div[data-baseweb="input"] input::placeholder {
    color: #71869e !important;
}

.login-submit button {
    color: #07111f !important;
    background: linear-gradient(100deg, var(--cyan), #a69aff) !important;
    border: 0 !important;
    text-align: center !important;
}

@media (max-width: 900px) {
    .hero { padding: 25px; }
    .hero h1 { font-size: 38px; }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# STATE
# ============================================================

@st.cache_resource
def get_chat_executor():
    # Keep a small worker pool alive across Streamlit reruns.
    # The worker performs the slow HTTP request while the UI remains responsive.
    return ThreadPoolExecutor(max_workers=2)

CHAT_EXECUTOR = get_chat_executor()

def clear_session():
    pending = st.session_state.get("pending_job")
    if pending is not None and not pending.done():
        pending.cancel()

    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.employee_id = None
    st.session_state.name = None
    st.session_state.token = None
    st.session_state.messages = []
    st.session_state.pending_job = None

for key, default in {
    "logged_in": False,
    "role": None,
    "employee_id": None,
    "name": None,
    "token": None,
    "messages": [],
    "pending_job": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================
# HELPERS
# ============================================================

def kb_counts():
    """Read the current KB counts when the CSVs are available."""
    base = Path(__file__).resolve().parent
    backend = base / "backend"

    def count_rows(filename):
        path = backend / filename
        if not path.exists():
            return "—"
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as f:
                return max(sum(1 for _ in csv.DictReader(f)), 0)
        except Exception:
            return "—"

    return {
        "policies": count_rows("policies_approved.csv"),
        "faqs": count_rows("hr_faq_approved_final.csv"),
        "rbac": count_rows("rbac_rules.csv"),
    }

def confidence_html(confidence, label):
    if confidence is None or label in (None, "", "Not applicable"):
        return ""

    try:
        score = int(confidence)
    except (TypeError, ValueError):
        return ""

    label = str(label)

    if score >= 85:
        cls = "conf-high"
        icon = "●"
    elif score >= 70:
        cls = "conf-medium"
        icon = "●"
    elif score >= 50:
        cls = "conf-low"
        icon = "●"
    else:
        cls = "conf-very-low"
        icon = "●"

    return (
        f'<div class="confidence {cls}">'
        f'{icon} Confidence {score}% · {label}'
        f'</div>'
    )

def display_sources(sources):
    if not sources:
        return

    st.markdown(
        '<div class="sources-label">Evidence & sources</div>',
        unsafe_allow_html=True,
    )

    for source in sources:
        source_type = source.get("type", "source")
        if source_type == "rbac":
            title = (
                f'{source.get("rule_id", "RBAC")} · '
                f'{source.get("data_or_action", "Access rule")}'
            )
            subtitle = source.get("citation", "")
        elif source_type == "contact":
            title = source.get("citation", "HR Contact Directory")
            subtitle = source.get("contact_id", "")
        elif source_type == "faq":
            title = source.get("citation", "HR FAQ")
            subtitle = source.get("section", "")
        else:
            title = source.get("citation", "HR Policy")
            subtitle = source.get("section", "")

        st.markdown(
            f'<div class="source-box">'
            f'<b>{title}</b>'
            f'{"<br><span style=\"color:#71879e;\">" + subtitle + "</span>" if subtitle else ""}'
            f'</div>',
            unsafe_allow_html=True,
        )

def render_message(message):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        status = message.get("status")
        if status == "thinking":
            st.markdown(
                '<div style="color:#9bb1c8;font-size:12px;margin-top:4px;">'
                '<span style="display:inline-block;animation:hrpulse 1.2s infinite;">'
                '● ● ●'
                '</span> Retrieving authorized evidence and preparing your answer…'
                '</div>'
                '<style>@keyframes hrpulse{0%,100%{opacity:.3}50%{opacity:1}}</style>',
                unsafe_allow_html=True,
            )
            return

        if status == "error":
            st.markdown(
                '<div class="confidence conf-low">'
                '⚠ Request could not be completed'
                '</div>',
                unsafe_allow_html=True,
            )
            return

        if status == "escalated":
            st.markdown(
                '<div class="confidence conf-medium">'
                '↗ Human HR escalation · retrieval and Gemini bypassed'
                '</div>',
                unsafe_allow_html=True,
            )

        topics = message.get("sensitive_topics") or []
        if topics:
            topic_text = ", ".join(str(topic).title() for topic in topics)
            st.markdown(
                f'<div class="confidence conf-medium">'
                f'⚠ Sensitive topic · {topic_text}'
                f'</div>',
                unsafe_allow_html=True,
            )

        confidence = confidence_html(
            message.get("confidence"),
            message.get("confidence_label"),
        )
        if confidence:
            st.markdown(confidence, unsafe_allow_html=True)

        display_sources(message.get("sources", []))

def _chat_request_worker(question, history, token):
    """Run the slow FastAPI request outside the Streamlit UI thread."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "question": question,
                "history": history,
            },
            timeout=45,
        )

        if response.status_code == 200:
            return {
                "ok": True,
                "data": response.json(),
            }

        try:
            detail = response.json().get(
                "detail",
                f"Backend error ({response.status_code}).",
            )
        except Exception:
            detail = f"Backend error ({response.status_code})."

        return {
            "ok": False,
            "status_code": response.status_code,
            "detail": detail,
        }

    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "status_code": None,
            "detail": (
                "Cannot connect to the HR backend. "
                "Make sure FastAPI is running on port 8001."
            ),
        }

    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "status_code": None,
            "detail": "The HR backend took too long to respond.",
        }

    except Exception as exc:
        return {
            "ok": False,
            "status_code": None,
            "detail": f"Chat error: {exc}",
        }

def queue_question(question):
    """Immediately put the user message on screen and start the backend job."""
    question = (question or "").strip()
    if not question:
        return False

    pending_job = st.session_state.get("pending_job")
    if pending_job is not None and not pending_job.done():
        return False

    # Capture history BEFORE adding the new question.
    history = [
        {"role": item.get("role"), "content": item.get("content", "")}
        for item in st.session_state.messages[-6:]
        if item.get("role") in {"user", "assistant"}
        and item.get("status") != "thinking"
    ]

    # This is rendered immediately in the current Streamlit run.
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    # Show an assistant placeholder while Gemini/backend work happens.
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "Thinking…",
            "status": "thinking",
        }
    )

    st.session_state.pending_job = CHAT_EXECUTOR.submit(
        _chat_request_worker,
        question,
        history,
        st.session_state.token,
    )

    return True

def finish_pending_question():
    """Collect a completed background job and replace the thinking placeholder."""
    job = st.session_state.get("pending_job")
    if job is None or not job.done():
        return

    try:
        result = job.result()
    except Exception as exc:
        result = {
            "ok": False,
            "status_code": None,
            "detail": f"Chat error: {exc}",
        }

    # Remove the completed job before any rerun/session transition.
    st.session_state.pending_job = None

    # Find the current thinking placeholder.
    thinking_index = None
    for index in range(len(st.session_state.messages) - 1, -1, -1):
        message = st.session_state.messages[index]
        if message.get("role") == "assistant" and message.get("status") == "thinking":
            thinking_index = index
            break

    if thinking_index is None:
        return

    if result.get("ok"):
        data = result.get("data", {})
        st.session_state.messages[thinking_index] = {
            "role": "assistant",
            "content": data.get(
                "answer",
                "The HR backend returned no answer.",
            ),
            "confidence": data.get("confidence"),
            "confidence_label": data.get("confidence_label"),
            "sources": data.get("sources", []),
            "status": data.get("status"),
            "sensitive_topics": data.get("sensitive_topics", []),
            "contact_id": data.get("contact_id"),
        }
        return

    status_code = result.get("status_code")
    detail = result.get("detail", "The HR backend could not answer the request.")

    if status_code == 401:
        st.session_state.messages[thinking_index] = {
            "role": "assistant",
            "content": "Your session has expired. Please sign in again.",
            "status": "error",
        }
        st.session_state._session_expired = True
        return

    st.session_state.messages[thinking_index] = {
        "role": "assistant",
        "content": detail,
        "status": "error",
    }

def render_conversation_fragment():
    """Poll the background job without blocking the main Streamlit page."""
    finish_pending_question()

    with st.container(height=520, border=True):
        if not st.session_state.messages:
            st.markdown(
                '<div class="welcome-card">'
                '<div class="welcome-title">👋 Welcome, '
                f'{st.session_state.name.split()[0]}.</div>'
                '<div class="welcome-copy">'
                'Your HR assistant is ready. Ask a policy question below '
                'and I will retrieve the authorized evidence for your role.'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

        for message in st.session_state.messages:
            render_message(message)

@st.fragment(run_every="1s")
def conversation_fragment():
    render_conversation_fragment()

def fetch_admin_metrics():
    if st.session_state.role != "hr":
        return None

    try:
        response = requests.get(
            f"{BACKEND_URL}/admin/metrics",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=8,
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    return None

# ============================================================
# LOGIN
# ============================================================

if not st.session_state.logged_in:
    left, right = st.columns([1.12, 0.88], gap="large")

    with left:
        st.markdown(
            '<div class="brand">'
            '<div class="brand-icon">✦</div>'
            '<div class="brand-name">HR Helpdesk</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<span class="pill">A smarter workplace assistant</span>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="hero-title" style="margin-top:24px;">'
            'Your policies,<br>'
            '<span style="color:#6DE7F5;">made simple.</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="color:#9BB1C8;max-width:560px;font-size:15px;'
            'line-height:1.75;">'
            'Ask questions about workplace policies, benefits, leave, '
            'and HR procedures. Get the information you need quickly, '
            'securely, and according to your role.'
            '</div>',
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            '<div class="login-card">'
            '<div style="color:#6DE7F5;font-size:10px;font-weight:800;'
            'letter-spacing:1px;">SECURE EMPLOYEE ACCESS</div>'
            '<div style="font-size:28px;font-weight:800;margin-top:17px;">'
            'Welcome back</div>'
            '<div style="color:#9BB1C8;font-size:13px;margin-top:7px;">'
            'Sign in to continue to HR Helpdesk.</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        employee_id = st.text_input(
            "Employee ID",
            placeholder="Enter your employee ID",
        )
        password = st.text_input(
            "Password",
            placeholder="Enter your password",
            type="password",
        )

        st.markdown('<div class="login-submit">', unsafe_allow_html=True)
        sign_in = st.button("Sign in", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if sign_in:
            if not employee_id.strip() or not password.strip():
                st.error("Please enter your Employee ID and password.")
            else:
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/login",
                        json={
                            "employee_id": employee_id.strip(),
                            "password": password,
                        },
                        timeout=10,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.logged_in = True
                        st.session_state.employee_id = data["employee_id"]
                        st.session_state.name = data["name"]
                        st.session_state.role = data["role"]
                        st.session_state.token = data["token"]
                        st.session_state.messages = []
                        st.rerun()
                    else:
                        try:
                            detail = response.json().get(
                                "detail",
                                "Invalid Employee ID or password.",
                            )
                        except Exception:
                            detail = "Invalid Employee ID or password."
                        st.error(detail)

                except requests.exceptions.ConnectionError:
                    st.error(
                        "Cannot connect to the HR backend. "
                        "Make sure FastAPI is running on port 8001."
                    )
                except requests.exceptions.Timeout:
                    st.error("The HR backend took too long to respond.")
                except Exception as exc:
                    st.error(f"Login error: {exc}")

        st.markdown(
            '<div style="text-align:center;color:#71879E;font-size:10px;'
            'line-height:1.6;margin-top:15px;">'
            '🔒 Secure access<br>'
            'Your role determines the information you can access.'
            '</div>',
            unsafe_allow_html=True,
        )

# ============================================================
# DASHBOARD / CHAT
# ============================================================

else:
    if st.session_state.pop("_session_expired", False):
        clear_session()
        st.rerun()

    counts = kb_counts()

    # Top bar
    top_left, top_right = st.columns([5, 1])

    with top_left:
        st.markdown(
            '<div class="topbar">'
            '<div class="brand">'
            '<div class="brand-icon">✦</div>'
            '<div class="brand-name">HR Helpdesk</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with top_right:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        logout = st.button("Logout", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if logout:
            clear_session()
            st.rerun()

    # Hero
    st.markdown(
        '<div class="hero">'
        '<div class="hero-kicker">NEXAHR · KNOWLEDGE GROUNDED AI</div>'
        '<h1>HR Helpdesk <span>RAG</span></h1>'
        '<p>Ask natural-language HR questions. The system retrieves '
        'authorized policy evidence first, then answers only from '
        'that evidence.</p>'
        '<div class="pills">'
        '<span class="pill">Role-aware</span>'
        '<span class="pill">Region-aware</span>'
        '<span class="pill">Approved KB only</span>'
        '<span class="pill">Evidence-based confidence</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Access + knowledge base
    st.markdown('<div class="section-title">Your access</div>',
                unsafe_allow_html=True)

    access_cols = st.columns([1.15, 1.15, 1.15, 1.15, 1.15, 1.15])

    access_items = [
        ("Employee", st.session_state.name),
        ("Employee ID", st.session_state.employee_id),
        ("Role", st.session_state.role),
        ("Policy chunks", counts["policies"]),
        ("FAQs", counts["faqs"]),
        ("RBAC rules", counts["rbac"]),
    ]

    for col, (label, value) in zip(access_cols, access_items):
        with col:
            st.markdown(
                f'<div class="stat-card">'
                f'<div class="stat-label">{label}</div>'
                f'<div class="stat-number" style="font-size:{22 if label in ("Employee","Role") else 30}px;">'
                f'{value}</div>'
                f'<div class="stat-caption">Authorized context</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Quick questions + how it works
    pending_job = st.session_state.get("pending_job")
    chat_busy = pending_job is not None and not pending_job.done()

    quick_col, how_col = st.columns([1.35, 1], gap="large")

    with quick_col:
        st.markdown(
            '<div class="section-title">Start with a question</div>'
            '<div class="section-subtitle">'
            'Try a common HR question or ask anything about the approved policy base.'
            '</div>',
            unsafe_allow_html=True,
        )

        q1, q2 = st.columns(2)
        with q1:
            if st.button(
                "How many annual leave days do I get?",
                key="q1",
                use_container_width=True,
                disabled=chat_busy,
            ):
                queue_question("How many annual leave days do I get?")
        with q2:
            if st.button(
                "Can I carry forward unused annual leave?",
                key="q2",
                use_container_width=True,
                disabled=chat_busy,
            ):
                queue_question("Can I carry forward unused annual leave?")

        q3, q4 = st.columns(2)
        with q3:
            if st.button(
                "Who is authorized to approve my leave?",
                key="q3",
                use_container_width=True,
                disabled=chat_busy,
            ):
                queue_question("Who is authorized to approve my leave?")
        with q4:
            if st.button(
                "What is the sick leave policy?",
                key="q4",
                use_container_width=True,
                disabled=chat_busy,
            ):
                queue_question("What is the sick leave policy?")

    with how_col:
        st.markdown(
            '<div class="section-title">How it works</div>'
            '<div class="info-card">'
            '<div class="step"><div class="step-num">1</div>'
            '<div class="step-text"><b>Retrieve authorized evidence</b><br>'
            '<span style="color:#8fa6bd;">Only policy and FAQ data your role can access.</span></div></div>'
            '<div class="step"><div class="step-num">2</div>'
            '<div class="step-text"><b>Rank the strongest sources</b><br>'
            '<span style="color:#8fa6bd;">Local vector search + keyword reranking finds the strongest evidence.</span></div></div>'
            '<div class="step"><div class="step-num">3</div>'
            '<div class="step-text"><b>Generate a grounded answer</b><br>'
            '<span style="color:#8fa6bd;">Gemini answers using the authorized context.</span></div></div>'
            '<div class="step"><div class="step-num">4</div>'
            '<div class="step-text"><b>Show confidence + sources</b><br>'
            '<span style="color:#8fa6bd;">You can see how strongly the retrieved evidence supports the answer.</span></div></div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # Chat
    st.markdown(
        '<div class="section-title">Conversation</div>',
        unsafe_allow_html=True,
    )

    # The conversation is a fragment so it can refresh independently while
    # the backend/Gemini request runs in a worker thread.
    conversation_fragment()

    # Real chat input. Disable it while a request is running so one click
    # cannot accidentally create several simultaneous requests.
    question = st.chat_input(
        "Ask an HR policy question...",
        disabled=chat_busy,
    )

    if question and not chat_busy:
        queue_question(question)

    # Quick-question buttons use the same queue and are disabled while busy.
    # The page response is returned immediately with the user's message and
    # a "Thinking…" placeholder; the fragment polls for the final answer.

# ============================================================
# HR ADMIN INSIGHTS
# ============================================================

if st.session_state.logged_in and st.session_state.role == "hr":
    metrics = fetch_admin_metrics()

    st.markdown(
        '<div class="section-title">HR Admin Insights</div>'
        '<div class="section-subtitle">'
        'Operational metrics from the local privacy-aware audit log.'
        '</div>',
        unsafe_allow_html=True,
    )

    if metrics:
        metric_cols = st.columns(4)
        admin_items = [
            ("Questions", metrics.get("total_questions", 0)),
            ("Escalations", metrics.get("escalations", 0)),
            ("Sensitive events", metrics.get("sensitive_events", 0)),
            ("Low-confidence", metrics.get("low_confidence", 0)),
        ]

        for col, (label, value) in zip(metric_cols, admin_items):
            with col:
                st.markdown(
                    f'<div class="stat-card">'
                    f'<div class="stat-label">{label}</div>'
                    f'<div class="stat-number">{value}</div>'
                    f'<div class="stat-caption">Local audit metrics</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        sensitive_topics = metrics.get("sensitive_topics", {})
        if sensitive_topics:
            topics = sorted(
                sensitive_topics.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:5]

            st.markdown(
                '<div class="info-card" style="margin-top:16px;">'
                '<div class="access-title">Sensitive topic routing</div>'
                + "".join(
                    f'<div style="display:flex;justify-content:space-between;'
                    f'padding:9px 0;border-bottom:1px solid rgba(154,193,228,.10);">'
                    f'<span>{topic.title()}</span><b>{count}</b></div>'
                    for topic, count in topics
                )
                + '</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No audit events have been recorded yet.")
