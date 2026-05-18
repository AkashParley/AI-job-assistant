import json
import re
import asyncio
import hashlib

import streamlit as st
import plotly.graph_objects as go
from utils import extract_text_from_pdf, clean_text
from rag import build_vectorstore
from agent import run_all_analysis

st.set_page_config(
    page_title="JobAI — Smart Application Assistant",
    page_icon="💼",
    layout="wide",
)

st.markdown("""
<head>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>
<defs>
  <linearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'>
    <stop offset='0%25' style='stop-color:%234f46e5'/>
    <stop offset='100%25' style='stop-color:%237c3aed'/>
  </linearGradient>
</defs>
<rect width='100' height='100' rx='22' fill='url(%23g)'/>
<text y='.9em' font-size='62' x='50%25' text-anchor='middle' dominant-baseline='top' style='font-family:Inter,sans-serif;font-weight:800;fill:white;letter-spacing:-2px'>J</text>
</svg>">
</head>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp { background: #070b14; }

.block-container {
    padding: 2rem 3rem !important;
    max-width: 1400px;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    color: #818cf8;
    font-weight: 500;
    margin-bottom: 16px;
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.1;
    background: linear-gradient(135deg, #fff 0%, #818cf8 50%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 12px;
}
.hero-sub {
    font-size: 1.05rem;
    color: #64748b;
    margin: 0 0 2rem;
    line-height: 1.6;
}

.pills-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 2.5rem;
}
.pill {
    display: flex;
    align-items: center;
    gap: 7px;
    background: #0f1520;
    border: 1px solid #1e2a3a;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    color: #94a3b8;
    font-weight: 500;
}
.pill span { color: #6366f1; }

.input-label {
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}
.stFileUploader {
    background: #0d1320 !important;
    border: 1px solid #1e2a3a !important;
    border-radius: 12px !important;
    padding: 0.5rem !important;
    transition: border-color 0.2s;
}
.stFileUploader:hover { border-color: #6366f1 !important; }
.stTextArea textarea {
    background: #0d1320 !important;
    border: 1px solid #1e2a3a !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
    transition: border-color 0.2s;
}
.stTextArea textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em;
    width: 100%;
    transition: all 0.2s !important;
    box-shadow: 0 4px 24px rgba(99,102,241,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 32px rgba(99,102,241,0.4) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #0d1320;
    border: 1px solid #1e2a3a;
    border-radius: 12px;
    padding: 5px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 24px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    color: #64748b !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
}

.result-card {
    background: #0d1320;
    border: 1px solid #1e2a3a;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1rem;
    line-height: 1.8;
}
.result-card h2 {
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    color: #e2e8f0 !important;
    margin-top: 1.5rem !important;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e2a3a;
}
.result-card p, .result-card li {
    color: #94a3b8 !important;
    font-size: 0.95rem !important;
}
.result-card strong { color: #e2e8f0 !important; }

.chart-card {
    background: #0d1320;
    border: 1px solid #1e2a3a;
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 1rem;
}
.score-high { background: rgba(34,197,94,0.15);  color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.score-mid  { background: rgba(250,204,21,0.15);  color: #facc15; border: 1px solid rgba(250,204,21,0.3); }
.score-low  { background: rgba(239,68,68,0.15);   color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

.cache-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 11px;
    color: #22c55e;
    font-weight: 500;
    margin-left: 10px;
}

.custom-divider {
    border: none;
    border-top: 1px solid #1e2a3a;
    margin: 2rem 0;
}

.stAlert { border-radius: 10px !important; }

.stDownloadButton > button {
    background: #0d1320 !important;
    border: 1px solid #4f46e5 !important;
    color: #818cf8 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: rgba(99,102,241,0.1) !important;
}

.stProgress > div > div {
    background: linear-gradient(90deg, #4f46e5, #7c3aed) !important;
    border-radius: 10px !important;
}

.stCaption { color: #475569 !important; font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def make_cache_key(resume_text: str, jd_text: str) -> str:
    """MD5 hash of resume+JD — same pair never hits the API twice."""
    return hashlib.md5((resume_text + jd_text).encode()).hexdigest()


def render_result_card(content: str):
    with st.container():
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(content)
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown('<div class="hero-badge">⚡ Powered by LangChain + ChromaDB + Groq</div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">AI Job Application<br>Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Upload your resume · Paste any job description · Get instant gap analysis,<br>a tailored cover letter, and 10 personalised interview questions.</p>', unsafe_allow_html=True)

st.markdown("""
<div class="pills-row">
  <div class="pill"><span>📊</span> Skill Gap Analysis</div>
  <div class="pill"><span>✉️</span> Cover Letter Generator</div>
  <div class="pill"><span>💡</span> Resume Suggestions</div>
  <div class="pill"><span>🎯</span> Interview Prep</div>
  <div class="pill"><span>⚡</span> Parallel LLM Calls</div>
  <div class="pill"><span>🧠</span> RAG Pipeline</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INPUTS
# ─────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<p class="input-label">📄 Your Resume</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        st.success(f"✅ **{uploaded_file.name}** ready for analysis")
    else:
        st.markdown(
            "<p style='color:#334155;font-size:13px;margin-top:8px;'>Supports PDF format · Max 10MB</p>",
            unsafe_allow_html=True
        )

with col2:
    st.markdown('<p class="input-label">📋 Job Description</p>', unsafe_allow_html=True)
    jd_text = st.text_area(
        "Paste Job Description",
        height=180,
        placeholder="Paste the full job description here — include requirements, responsibilities, and tech stack for the most accurate analysis...",
        label_visibility="collapsed"
    )
    if jd_text:
        wc = len(jd_text.split())
        color = "#22c55e" if wc > 100 else "#facc15"
        st.markdown(
            f"<p style='color:{color};font-size:12px;margin-top:4px;'>{'✅' if wc > 100 else '⚠️'} {wc} words — {'Good detail' if wc > 100 else 'More detail = better analysis'}</p>",
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)
analyze = st.button("🔍 Analyze My Application", use_container_width=True)

# ─────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────
if analyze:
    if not uploaded_file or not jd_text.strip():
        st.warning("⚠️ Please upload your resume PDF and paste a job description.")
        st.stop()

    # ── Extract text ──────────────────────────
    with st.spinner("📖 Extracting resume content..."):
        raw_resume = extract_text_from_pdf(uploaded_file)
        resume_text = clean_text(raw_resume)
        jd_clean = clean_text(jd_text)

    # ── Input validation ──────────────────────
    if len(resume_text.split()) < 50:
        st.error("⚠️ Resume seems too short — please check your PDF uploaded correctly.")
        st.stop()

    if len(jd_clean.split()) < 30:
        st.error("⚠️ Job description too short for meaningful analysis. Please paste the full JD.")
        st.stop()

    # ── Cache check ───────────────────────────
    cache_key = make_cache_key(resume_text, jd_clean)
    from_cache = cache_key in st.session_state

    if not from_cache:
        progress = st.progress(0, text="Starting analysis...")

        with st.spinner("🧠 Building RAG knowledge base..."):
            try:
                vectorstore = build_vectorstore(resume_text, jd_clean)
                progress.progress(30, text="Knowledge base ready...")
            except Exception as e:
                st.error(f"⚠️ RAG pipeline failed: {str(e)}")
                st.stop()

        with st.spinner("⚡ Running all 5 analyses in parallel..."):
            try:
                analysis, scores, cover_letter, suggestions, questions = asyncio.run(
                    run_all_analysis(resume_text, jd_clean)
                )
                progress.progress(100, text="✅ Done!")
            except Exception as e:
                st.error(f"⚠️ Analysis failed: {str(e)}. Please try again.")
                st.stop()

        # Store in session cache
        st.session_state[cache_key] = {
            "analysis":     analysis,
            "scores":       scores,
            "cover_letter": cover_letter,
            "suggestions":  suggestions,
            "questions":    questions,
        }
    else:
        # Loaded from cache — instant
        analysis     = st.session_state[cache_key]["analysis"]
        scores       = st.session_state[cache_key]["scores"]
        cover_letter = st.session_state[cache_key]["cover_letter"]
        suggestions  = st.session_state[cache_key]["suggestions"]
        questions    = st.session_state[cache_key]["questions"]

    # ── Cache indicator ───────────────────────
    if from_cache:
        st.markdown(
            '<div style="margin-bottom:1rem;">'
            '<span class="cache-badge">⚡ Loaded from cache — instant results</span>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown("<br>", unsafe_allow_html=True)

    # ─────────────────────────────────────────
    # TABS
    # ─────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊  Gap Analysis",
        "✉️  Cover Letter",
        "💡  Resume Suggestions",
        "🎯  Interview Prep",
    ])

    # ── TAB 1: GAP ANALYSIS ──────────────────
    with tab1:
        # Resolve score — prefer scores JSON, fall back to text extraction
        try:
            score = int(scores["overall_score"])
        except (KeyError, TypeError, ValueError):
            match = re.search(r"\*\*Score:\s*(\d+)/100\*\*", analysis)
            score = int(match.group(1)) if match else 50

        score_class = "score-high" if score >= 70 else "score-mid" if score >= 45 else "score-low"
        score_label = "Strong Match" if score >= 70 else "Partial Match" if score >= 45 else "Weak Match"

        st.markdown(
            f'<div class="score-badge {score_class}">🎯 {score}/100 — {score_label}</div>',
            unsafe_allow_html=True
        )

        # Charts row 1
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                title={"text": "Overall Match Score", "font": {"color": "#94a3b8", "size": 14}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#334155", "tickfont": {"color": "#475569"}},
                    "bar": {"color": "#6366f1", "thickness": 0.25},
                    "bgcolor": "#0d1320",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 45],   "color": "#1a0f0f"},
                        {"range": [45, 70],  "color": "#1a1a0f"},
                        {"range": [70, 100], "color": "#0f1a0f"},
                    ],
                    "threshold": {
                        "line": {"color": "#facc15", "width": 2},
                        "thickness": 0.75,
                        "value": 70,
                    },
                },
                number={"suffix": "/100", "font": {"color": "#e2e8f0", "size": 32}},
            ))
            fig_gauge.update_layout(
                paper_bgcolor="#0d1320", plot_bgcolor="#0d1320",
                height=250, margin=dict(t=50, b=10, l=20, r=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            try:
                cats = ["Technical", "Experience", "Education", "Soft Skills"]
                vals = [
                    scores["technical_skills"],
                    scores["experience_match"],
                    scores["education_match"],
                    scores["soft_skills"],
                ]
                fig_radar = go.Figure(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=cats + [cats[0]],
                    fill="toself",
                    fillcolor="rgba(99,102,241,0.15)",
                    line=dict(color="#6366f1", width=2),
                    marker=dict(color="#818cf8", size=7),
                ))
                fig_radar.update_layout(
                    polar=dict(
                        bgcolor="#0d1320",
                        radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#334155", size=9), gridcolor="#1e2a3a", linecolor="#1e2a3a"),
                        angularaxis=dict(tickfont=dict(color="#94a3b8", size=12), gridcolor="#1e2a3a", linecolor="#1e2a3a"),
                    ),
                    paper_bgcolor="#0d1320",
                    title=dict(text="Skill Breakdown Radar", font=dict(color="#94a3b8", size=14)),
                    height=250, margin=dict(t=50, b=10, l=40, r=40),
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            except Exception:
                st.info("Radar chart unavailable for this analysis.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Charts row 2
        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            try:
                skills     = scores["matching_skills"] + scores["missing_skills"]
                skill_vals = [100] * len(scores["matching_skills"]) + [60] * len(scores["missing_skills"])
                colors_bar = ["#22c55e"] * len(scores["matching_skills"]) + ["#ef4444"] * len(scores["missing_skills"])
                labels_bar = ["✅ Match"] * len(scores["matching_skills"]) + ["❌ Missing"] * len(scores["missing_skills"])
                fig_bar = go.Figure(go.Bar(
                    x=skill_vals, y=skills, orientation="h",
                    marker_color=colors_bar,
                    text=labels_bar, textposition="inside",
                    textfont=dict(color="white", size=11),
                ))
                fig_bar.update_layout(
                    title=dict(text="Skills Match Overview", font=dict(color="#94a3b8", size=14)),
                    paper_bgcolor="#0d1320", plot_bgcolor="#0d1320",
                    xaxis=dict(showticklabels=False, gridcolor="#1e2a3a", zeroline=False),
                    yaxis=dict(tickfont=dict(color="#94a3b8", size=11), gridcolor="#1e2a3a"),
                    height=300, margin=dict(t=50, b=10, l=10, r=10),
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            except Exception:
                st.info("Skills chart unavailable for this analysis.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c4:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            try:
                gap_vals = [scores["critical_gaps"], scores["important_gaps"], scores["minor_gaps"]]
                fig_donut = go.Figure(go.Pie(
                    labels=["🔴 Critical", "🟡 Important", "🟢 Minor"],
                    values=gap_vals, hole=0.65,
                    marker=dict(colors=["#ef4444", "#facc15", "#22c55e"]),
                    textfont=dict(color="white", size=12),
                    hovertemplate="%{label}: %{value}<extra></extra>",
                ))
                fig_donut.update_layout(
                    title=dict(text="Gap Severity Breakdown", font=dict(color="#94a3b8", size=14)),
                    paper_bgcolor="#0d1320", plot_bgcolor="#0d1320",
                    legend=dict(font=dict(color="#94a3b8"), bgcolor="#0d1320"),
                    height=300, margin=dict(t=50, b=10, l=10, r=10),
                    annotations=[dict(
                        text=f"<b>{sum(gap_vals)}</b><br><span style='font-size:11px'>gaps</span>",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=20, color="#e2e8f0"),
                    )],
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            except Exception:
                st.info("Gap chart unavailable for this analysis.")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="input-label">📋 Detailed Analysis</p>', unsafe_allow_html=True)
        render_result_card(analysis)

    # ── TAB 2: COVER LETTER ──────────────────
    with tab2:
        st.markdown('<p class="input-label">✉️ Your Tailored Cover Letter</p>', unsafe_allow_html=True)
        render_result_card(cover_letter)
        st.download_button(
            label="⬇️ Download Cover Letter (.txt)",
            data=cover_letter,
            file_name="cover_letter.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # ── TAB 3: RESUME SUGGESTIONS ────────────
    with tab3:
        c1, c2, c3 = st.columns(3)
        for col, icon, title, sub in [
            (c1, "🔑", "Missing Keywords", "Add to pass ATS filters"),
            (c2, "📝", "Bullet Rewrites",  "Stronger, metric-driven"),
            (c3, "⚡", "ATS Boosters",     "Exact JD phrases to use"),
        ]:
            with col:
                st.markdown(f"""<div style='background:#0d1320;border:1px solid #1e2a3a;border-radius:12px;padding:1rem;text-align:center;'>
                    <div style='font-size:1.8rem'>{icon}</div>
                    <div style='color:#6366f1;font-weight:700;font-size:14px;margin-top:4px;'>{title}</div>
                    <div style='color:#475569;font-size:12px;'>{sub}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="input-label">💡 Your Personalised Resume Improvement Plan</p>', unsafe_allow_html=True)
        render_result_card(suggestions)
        st.download_button(
            label="⬇️ Download Improvement Plan (.txt)",
            data=suggestions,
            file_name="resume_improvement_plan.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # ── TAB 4: INTERVIEW PREP ────────────────
    with tab4:
        st.markdown('<p class="input-label">🎯 Your Interview Prep Guide</p>', unsafe_allow_html=True)
        render_result_card(questions)