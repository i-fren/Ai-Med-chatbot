import base64
import html
from pathlib import Path

import streamlit as st

from Memory_connect_with_llm import qa_chain
from report_analyzer import analyze_medical_report

# ============================================================
# MediOrb: premium medical knowledge assistant
# Keep these files in the same folder:
#   app.py, styles.css, mybot_circle_transparent.webm (or mybot.mp4),
#   Memory_connect_with_llm.py, report_analyzer.py
# Requires Streamlit >= 1.39 (keyed containers).
# ============================================================
st.set_page_config(
    page_title="MediOrb | Medical Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
CSS_FILE = BASE_DIR / "styles.css"


@st.cache_data
def load_css() -> str:
    return CSS_FILE.read_text(encoding="utf-8") if CSS_FILE.exists() else ""


@st.cache_data
def load_robot_video() -> tuple[str, str]:
    """Return (data_uri, mime). Prefers the transparent webm, falls back to mp4."""
    for name, mime in (
        ("mybot_circle_transparent.webm", "video/webm"),
        ("mybot.mp4", "video/mp4"),
    ):
        file = BASE_DIR / name
        if file.exists():
            encoded = base64.b64encode(file.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{encoded}", mime
    return "", ""


css = load_css()
if css:
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
else:
    st.warning("styles.css not found. The app will use Streamlit's default styling.")

robot_video_data_uri, robot_video_mime = load_robot_video()

# Session state.
st.session_state.setdefault("messages", [])
st.session_state.setdefault("page", "Home")
st.session_state.setdefault("pending_question", "")
st.session_state.setdefault("health_record", None)
st.session_state.setdefault("night_mode", False)
st.session_state.setdefault("last_report_analysis", None)
st.session_state.setdefault("last_report_name", "")


def go_to_page(page: str) -> None:
    st.session_state.page = page


def ask_question(question: str) -> None:
    question = question.strip()
    if question:
        st.session_state.pending_question = question
        st.session_state.page = "Chat"


def render_theme_toggle() -> None:
    _, toggle_col = st.columns([6, 1])
    with toggle_col:
        st.toggle("Night mode", key="night_mode")
    if st.session_state.night_mode:
        # styles.css switches to the night palette when this marker exists.
        st.markdown('<div class="night-flag"></div>', unsafe_allow_html=True)


def render_topbar() -> None:
    st.markdown(
        """
        <div class="topbar">
          <div class="logo-wrap">
            <div class="logo-mark">M</div>
            <div>
              <div class="logo-name">MediOrb</div>
              <div class="logo-sub">MEDICAL INTELLIGENCE</div>
            </div>
          </div>
          <div class="online-pill"><span class="online-dot"></span> Knowledge system online</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_items = [
        ("⌂  Home", "Home"),
        ("✦  AI Chat", "Chat"),
        ("▣  Report AI", "Report Analyzer"),
        ("＋  Equipment", "Equipment"),
        ("♡  Wellness", "Health Records"),
    ]
    columns = st.columns(len(nav_items), gap="small")
    for col, (label, page) in zip(columns, nav_items):
        with col:
            if st.button(
                label,
                key=f"nav_{page.lower().replace(' ', '_')}",
                use_container_width=True,
                type="primary" if st.session_state.page == page else "secondary",
            ):
                go_to_page(page)
                st.rerun()


def render_footer() -> None:
    st.markdown(
        """
        <div class="footer">
          <strong>MediOrb</strong> · Medical Intelligence<br><br>
          Powered by Groq · Hugging Face · FAISS<br>
          <span class="footer-note">For education and general information only.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_disclaimer() -> None:
    st.markdown(
        """
        <div class="disclaimer">
          <strong>Medical information notice</strong><br>
          MediOrb provides educational information and is not a substitute for
          professional medical advice, diagnosis, or treatment. For urgent or
          concerning symptoms, contact a qualified healthcare professional.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home() -> None:
    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        if robot_video_data_uri:
            robot_html = (
                '<video class="robot-video" autoplay loop muted playsinline preload="auto" '
                'aria-label="Animated MediOrb robot assistant">'
                f'<source src="{robot_video_data_uri}" type="{robot_video_mime}"></video>'
            )
        else:
            robot_html = '<div class="robot-fallback">🤖</div>'

        st.markdown(
            f"""
            <section class="hero">
              <div class="hero-copy-wrap">
                <div class="eyebrow"><span class="eyebrow-spark">✦</span> AI-POWERED MEDICAL KNOWLEDGE</div>
                <h1 class="hero-title">Your personal <span>medical AI</span> companion.</h1>
                <p class="hero-copy">Explore your medical knowledge library, understand health information,
                and ask questions in a calm, focused space designed around you.</p>
                <div class="hero-badge"><span class="badge-dot"></span>
                  <strong>Knowledge base</strong><span>·</span> Medical encyclopedia
                </div>
              </div>
              <div class="hero-art">
                <div class="art-orbit orbit-one"></div><div class="art-orbit orbit-two"></div>
                <div class="art-glow"></div>{robot_html}
                <div class="art-caption"><span class="online-dot"></span> Your AI buddy is ready</div>
              </div>
            </section>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-heading">Explore MediOrb '
            '<span class="section-subtitle">Your tools, one calm workspace</span></div>',
            unsafe_allow_html=True,
        )

        features = [
            ("✦", "Ask MediOrb", "Get focused answers from your medical knowledge base.", "Start a conversation", "Chat"),
            ("＋", "Medical equipment", "Explore common tools and their general purpose.", "Explore equipment", "Equipment"),
            ("♡", "Health & wellness", "Record optional wellness measurements for this session.", "Open health space", "Health Records"),
            ("▣", "Medical report analyzer", "Upload a PDF report for an educational explanation.", "Analyze a report", "Report Analyzer"),
        ]
        for start in (0, 2):
            cols = st.columns(2, gap="medium")
            for col, feature in zip(cols, features[start:start + 2]):
                icon, title, desc, button, page = feature
                with col:
                    st.markdown(
                        f'<div class="feature-card"><div class="icon-box">{icon}</div>'
                        f'<div class="card-title">{title}</div><div class="card-desc">{desc}</div></div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        button,
                        key=f"home_{page}",
                        use_container_width=True,
                        type="primary" if page == "Chat" else "secondary",
                    ):
                        go_to_page(page)
                        st.rerun()

    with right:
        st.markdown(
            '<div class="section-heading section-heading-first">System overview '
            '<span class="section-subtitle">Live workspace</span></div>',
            unsafe_allow_html=True,
        )
        m1, m2 = st.columns(2, gap="small")
        with m1:
            st.markdown(
                '<div class="metric-card"><div class="metric-icon">✦</div><div class="metric-label">Assistant</div>'
                '<div class="metric-value">Ready</div><div class="metric-note">Knowledge search</div></div>',
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                '<div class="metric-card"><div class="metric-icon">⌘</div><div class="metric-label">Answer mode</div>'
                '<div class="metric-value">RAG</div><div class="metric-note">Source-grounded</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="content-panel side-panel"><div class="panel-kicker">QUICK START</div>'
            '<div class="panel-title">What can I help you explore?</div>'
            '<p class="panel-copy">Choose a prompt to start a conversation with MediOrb.</p></div>',
            unsafe_allow_html=True,
        )
        quick_prompts = [
            "Explain what a complete blood count measures",
            "What is the purpose of a stethoscope?",
            "Explain common medical terms in simple language",
        ]
        for i, prompt in enumerate(quick_prompts):
            if st.button(f"✧  {prompt}", key=f"prompt_{i}", use_container_width=True):
                ask_question(prompt)
                st.rerun()

        st.markdown(
            '<div class="content-panel side-panel wellness-preview"><div class="panel-kicker">YOUR HEALTH SPACE</div>'
            '<div class="panel-title">Wellness, at a glance</div>'
            '<div class="history-item">Heart rate <span class="item-hint">Optional</span></div>'
            '<div class="history-item">Daily steps <span class="item-hint">Optional</span></div>'
            '<div class="history-item">Sleep & hydration <span class="item-hint">Optional</span></div></div>',
            unsafe_allow_html=True,
        )
        if st.button("Open wellness space →", key="open_wellness_side", use_container_width=True):
            go_to_page("Health Records")
            st.rerun()

    st.markdown('<div class="section-heading">Recent questions</div>', unsafe_allow_html=True)
    user_messages = [m for m in st.session_state.messages if m.get("role") == "user"]
    if not user_messages:
        st.markdown(
            '<div class="history-item empty-history">No conversations yet. Start with a medical knowledge question.</div>',
            unsafe_allow_html=True,
        )
    else:
        for i, message in enumerate(reversed(user_messages[-4:])):
            safe_content = html.escape(message.get("content", ""))
            st.markdown(f'<div class="history-item">✦ &nbsp; {safe_content}</div>', unsafe_allow_html=True)
            if st.button("Ask again", key=f"recent_{i}"):
                ask_question(message.get("content", ""))
                st.rerun()
    render_disclaimer()
    render_footer()


def render_sources(sources: list) -> None:
    with st.expander("View source evidence"):
        for source in sources:
            name = html.escape(str(source.get("name", "Medical document")))
            text = html.escape(str(source.get("text", "")))
            st.markdown(
                f'<div class="source-box"><strong>{name}</strong><br><br>{text}</div>',
                unsafe_allow_html=True,
            )


def render_chat() -> None:
    st.markdown(
        '<div class="eyebrow">YOUR MEDICAL KNOWLEDGE ASSISTANT</div>'
        '<h1 class="page-title">Ask MediOrb<span class="title-period">.</span></h1>'
        '<p class="page-lead">Ask questions about your indexed medical encyclopedia and explore source-backed explanations.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="chat-tip"><span>✦</span> Tip: Ask one clear question at a time for a more focused answer.</div>',
        unsafe_allow_html=True,
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                render_sources(message["sources"])

    question = st.chat_input("Ask a question about medical knowledge…")
    if not question and st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = ""

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Searching your medical knowledge base…"):
                try:
                    result = qa_chain.invoke({"query": question})
                    answer = str(result.get("result", "I couldn't find an answer in the available knowledge base."))
                    sources = []
                    for document in result.get("source_documents", []):
                        metadata = getattr(document, "metadata", {}) or {}
                        source_path = metadata.get("source", "")
                        sources.append({
                            "name": Path(str(source_path)).name if source_path else "Medical document",
                            "text": str(getattr(document, "page_content", ""))[:1200],
                        })
                    st.markdown(answer)
                    if sources:
                        render_sources(sources)
                    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
                except Exception as error:
                    error_message = "Sorry, I couldn't process that question right now. Please try again in a moment."
                    st.error(error_message)
                    print(f"MediOrb chat error: {type(error).__name__}: {error}")
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
        st.rerun()

    render_disclaimer()
    render_footer()


def render_equipment() -> None:
    st.markdown(
        '<div class="eyebrow">REFERENCE LIBRARY</div>'
        '<h1 class="page-title">Medical equipment<span class="title-period">.</span></h1>'
        '<p class="page-lead">A quick guide to common medical tools and their general purpose.</p>',
        unsafe_allow_html=True,
    )
    equipment = [
        ("🩺", "Stethoscope", "Used by healthcare professionals to listen to internal body sounds."),
        ("🌡️", "Thermometer", "Used to measure body temperature."),
        ("◉", "Blood pressure monitor", "Measures blood pressure."),
        ("◌", "Pulse oximeter", "Estimates blood oxygen saturation and pulse rate."),
        ("✚", "Infusion pump", "Controls the delivery rate of fluids or medicines in clinical settings."),
        ("⌁", "Electrocardiogram (ECG)", "Records the electrical activity of the heart."),
    ]
    cols = st.columns(3, gap="medium")
    for i, (icon, name, description) in enumerate(equipment):
        with cols[i % 3]:
            st.markdown(
                f'<div class="feature-card equipment-card"><div class="icon-box">{icon}</div>'
                f'<div class="card-title card-title-large">{name}</div>'
                f'<div class="card-desc card-desc-large">{description}</div></div>',
                unsafe_allow_html=True,
            )
    st.caption("This is a general educational reference, not instructions for operating clinical equipment.")
    render_footer()


def render_report_analyzer() -> None:
    st.markdown(
        '<div class="eyebrow">AI DOCUMENT ANALYSIS</div>'
        '<h1 class="page-title">Medical report analyzer<span class="title-period">.</span></h1>'
        '<p class="page-lead">Upload a readable PDF report to receive an educational explanation of its contents.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="content-panel upload-panel"><div class="panel-kicker">YOUR DOCUMENT</div>'
        '<div class="panel-title">Bring your report into focus</div>'
        '<p class="panel-copy">PDF files only. Avoid uploading documents you do not have permission to share.</p></div>',
        unsafe_allow_html=True,
    )
    uploaded_report = st.file_uploader(
        "Choose a medical PDF",
        type=["pdf"],
        key="medical_report_upload",
        help="Upload a readable medical or laboratory report in PDF format.",
    )
    if uploaded_report is not None:
        st.markdown(
            f'<div class="history-item">📄 &nbsp; {html.escape(uploaded_report.name)}</div>',
            unsafe_allow_html=True,
        )
        if st.button("✦  Analyze report", key="analyze_report_button", type="primary", use_container_width=True):
            with st.spinner("Reading the report and preparing an explanation…"):
                try:
                    analysis = analyze_medical_report(uploaded_report.getvalue(), uploaded_report.name)
                    st.session_state.last_report_analysis = analysis
                    st.session_state.last_report_name = uploaded_report.name
                except Exception as error:
                    st.session_state.last_report_analysis = None
                    st.error("Could not analyze this report. Please check that the PDF is readable and try again.")
                    print(f"MediOrb report analysis error: {type(error).__name__}: {error}")
    else:
        # A removed upload should not leave a stale explanation on screen.
        st.session_state.last_report_analysis = None

    # Rendered outside the button block so it survives reruns.
    if st.session_state.last_report_analysis:
        st.markdown('<div class="section-heading">MediOrb explanation</div>', unsafe_allow_html=True)
        with st.container(key="report_result"):
            st.markdown(st.session_state.last_report_analysis)

    render_disclaimer()
    render_footer()


def render_health_records() -> None:
    st.markdown(
        '<div class="eyebrow">PERSONAL WELLNESS</div>'
        '<h1 class="page-title">Health space<span class="title-period">.</span></h1>'
        '<p class="page-lead">Optionally record simple wellness measurements for the current session.</p>',
        unsafe_allow_html=True,
    )
    with st.form("health_records_form"):
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            heart_rate = st.number_input("Heart rate (beats per minute)", min_value=0, max_value=250, value=0)
            daily_steps = st.number_input("Daily steps", min_value=0, max_value=100000, value=0, step=100)
        with c2:
            sleep_hours = st.number_input("Sleep (hours)", min_value=0.0, max_value=24.0, value=0.0, step=0.5)
            water_glasses = st.number_input("Water intake (glasses)", min_value=0, max_value=50, value=0)
        submitted = st.form_submit_button("Save wellness record", use_container_width=True, type="primary")
    if submitted:
        st.session_state.health_record = {
            "Heart rate": f"{heart_rate} bpm",
            "Daily steps": f"{daily_steps:,}",
            "Sleep": f"{sleep_hours:g} hrs",
            "Water": f"{water_glasses} glasses",
        }
        st.success("Your wellness record has been saved for this session.")

    if st.session_state.health_record:
        st.markdown('<div class="section-heading">Latest session record</div>', unsafe_allow_html=True)
        cols = st.columns(4, gap="small")
        for col, (label, value) in zip(cols, st.session_state.health_record.items()):
            with col:
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">{html.escape(label)}</div>'
                    f'<div class="metric-value metric-value-small">{html.escape(value)}</div></div>',
                    unsafe_allow_html=True,
                )
        st.caption("These records are stored only in the current Streamlit session and are not saved to a permanent database.")
    render_disclaimer()
    render_footer()


# Main layout.
render_theme_toggle()
render_topbar()
page = st.session_state.page
if page == "Home":
    render_home()
elif page == "Chat":
    render_chat()
elif page == "Equipment":
    render_equipment()
elif page == "Report Analyzer":
    render_report_analyzer()
elif page == "Health Records":
    render_health_records()
else:
    st.session_state.page = "Home"
    st.rerun()