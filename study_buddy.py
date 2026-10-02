import streamlit as st
from openai import Openai
from PyPDF2 import PdfReader
import json
import os
import time
import random

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StudyBuddy AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Root Variables ── */
:root {
    --bg:        #0b0f19;
    --surface:   #121828;
    --card:      #1a2235;
    --border:    #232f47;
    --accent:    #4f8ef7;
    --accent2:   #7c3aed;
    --green:     #22c55e;
    --red:       #ef4444;
    --yellow:    #f59e0b;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --radius:    14px;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Main area ── */
.main .block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 900px !important;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, #4f8ef720, #7c3aed20);
    border: 1px solid #4f8ef740;
    border-radius: 99px;
    padding: .35rem 1.1rem;
    font-size: .75rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--accent) !important;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.2rem, 5vw, 3.4rem);
    font-weight: 800;
    background: linear-gradient(135deg, #e2e8f0 30%, #4f8ef7 80%, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin-bottom: .6rem;
}
.hero-sub {
    color: var(--muted) !important;
    font-size: 1.05rem;
    font-weight: 300;
    max-width: 480px;
    margin: 0 auto;
}

/* ── Cards ── */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
    transition: border-color .2s;
}
.card:hover { border-color: #354565; }

/* ── Question card ── */
.q-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.6rem 1.8rem 1.2rem;
    margin-bottom: 1.4rem;
    position: relative;
    overflow: hidden;
}
.q-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent2));
    border-radius: 4px 0 0 4px;
}
.q-number {
    font-family: 'Syne', sans-serif;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--accent) !important;
    margin-bottom: .5rem;
}
.q-text {
    font-size: 1.05rem;
    font-weight: 500;
    line-height: 1.55;
    color: var(--text) !important;
}

/* ── Stat pills ── */
.stat-row {
    display: flex;
    gap: .8rem;
    flex-wrap: wrap;
    margin: 1.2rem 0 2rem;
    justify-content: center;
}
.stat-pill {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 99px;
    padding: .45rem 1.1rem;
    font-size: .82rem;
    font-weight: 500;
    color: var(--muted) !important;
    display: flex;
    align-items: center;
    gap: .4rem;
}
.stat-pill span { color: var(--text) !important; font-weight: 600; }

/* ── Score bar ── */
.score-bar-wrap {
    background: var(--border);
    border-radius: 99px;
    height: 8px;
    margin: .6rem 0 1.4rem;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    transition: width .5s ease;
}

/* ── Result badges ── */
.result-correct {
    background: #16a34a18;
    border: 1px solid #16a34a40;
    color: var(--green) !important;
    border-radius: 8px;
    padding: .5rem .9rem;
    font-size: .88rem;
    font-weight: 500;
    margin-top: .5rem;
}
.result-wrong {
    background: #dc262618;
    border: 1px solid #dc262640;
    color: var(--red) !important;
    border-radius: 8px;
    padding: .5rem .9rem;
    font-size: .88rem;
    font-weight: 500;
    margin-top: .5rem;
}

/* ── Streamlit widgets override ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: .6rem 1.6rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: .92rem !important;
    cursor: pointer !important;
    transition: opacity .2s, transform .15s !important;
    box-shadow: 0 4px 18px #4f8ef730 !important;
}
.stButton > button:hover {
    opacity: .9 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* secondary button style via class */
div[data-testid="column"] .stButton > button {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
    color: var(--text) !important;
}

.stRadio > label { color: var(--text) !important; font-size: .95rem !important; }
.stRadio [data-testid="stMarkdownContainer"] p { color: var(--text) !important; }

div[data-testid="stFileUploader"] {
    background: var(--card) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1.6rem !important;
    transition: border-color .2s !important;
}
div[data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }

.stSelectbox > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}
.stSlider [data-testid="stThumbValue"] { color: var(--accent) !important; }

.stSuccess {
    background: #16a34a14 !important;
    border: 1px solid #16a34a30 !important;
    color: var(--green) !important;
    border-radius: 10px !important;
}
.stError {
    background: #dc262614 !important;
    border: 1px solid #dc262630 !important;
    color: var(--red) !important;
    border-radius: 10px !important;
}
.stInfo {
    background: #4f8ef714 !important;
    border: 1px solid #4f8ef730 !important;
    color: var(--accent) !important;
    border-radius: 10px !important;
}
.stWarning {
    background: #f59e0b14 !important;
    border: 1px solid #f59e0b30 !important;
    color: var(--yellow) !important;
    border-radius: 10px !important;
}

.stSpinner > div { border-top-color: var(--accent) !important; }
.stTextInput > div > input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}
.stTextArea > div > textarea {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card) !important;
    border-radius: 12px !important;
    padding: .3rem !important;
    gap: .2rem !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.4rem !important; }

hr { border-color: var(--border) !important; }

/* Divider */
.divider {
    height: 1px;
    background: var(--border);
    margin: 1.8rem 0;
}

/* Expander */
[data-testid="stExpander"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stExpander"] summary { color: var(--text) !important; }

/* Final score card */
.final-score {
    text-align: center;
    background: linear-gradient(135deg, #4f8ef715, #7c3aed15);
    border: 1px solid #4f8ef730;
    border-radius: var(--radius);
    padding: 2.4rem;
    margin: 1.5rem 0;
}
.final-score .big-num {
    font-family: 'Syne', sans-serif;
    font-size: 4rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.final-score .grade { font-size: 1.1rem; color: var(--muted) !important; margin-top: .4rem; }

/* Summary notes */
.summary-box {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    font-size: .92rem;
    line-height: 1.7;
    white-space: pre-wrap;
    color: var(--text) !important;
}

/* Flashcard */
.flashcard {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 2.4rem;
    text-align: center;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: transform .2s, box-shadow .2s;
    position: relative;
    overflow: hidden;
}
.flashcard::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, #4f8ef708, #7c3aed08);
    pointer-events: none;
}
.flashcard:hover { transform: translateY(-3px); box-shadow: 0 12px 40px #4f8ef720; }
.flashcard-label {
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--accent) !important;
    margin-bottom: 1rem;
}
.flashcard-text {
    font-family: 'Syne', sans-serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text) !important;
    line-height: 1.5;
}

/* Sidebar sections */
.sidebar-section-title {
    font-family: 'Syne', sans-serif;
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--muted) !important;
    margin: 1.4rem 0 .6rem;
}

/* Progress indicator */
.progress-text {
    font-size: .82rem;
    color: var(--muted) !important;
    text-align: right;
    margin-bottom: .3rem;
}
</style>
""", unsafe_allow_html=True)

# ── API Key ───────────────────────────────────────────────────────────────────
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    st.error("⚠️ DEEPSEEK_API_KEY environment variable not found. Please set it before running.")
    st.stop()
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# ── Session state defaults ────────────────────────────────────────────────────
for k, v in {
    "quiz": None,
    "score": 0,
    "answers": {},
    "checked": {},
    "flashcards": None,
    "fc_index": 0,
    "fc_show_answer": False,
    "summary": None,
    "content": "",
    "filename": "",
    "active_tab": 0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 .5rem;">
        <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;
                    background:linear-gradient(135deg,#e2e8f0,#4f8ef7);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">🧠 StudyBuddy</div>
        <div style="font-size:.78rem;color:#64748b;margin-top:.2rem;">Powered by Groq × LLaMA</div>
    </div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">⚙️ Quiz Settings</div>', unsafe_allow_html=True)
    num_questions = st.slider("Number of questions", 3, 10, 5)
    difficulty = st.selectbox("Difficulty", ["Mixed", "Easy", "Medium", "Hard"])
    question_type = st.selectbox("Question type", ["Multiple Choice", "True / False", "Mixed"])

    st.markdown('<div class="sidebar-section-title">📄 Document</div>', unsafe_allow_html=True)
    if st.session_state.filename:
        st.markdown(f"""
        <div class="card" style="padding:.9rem 1rem;margin-bottom:.6rem;">
            <div style="font-size:.72rem;color:#64748b;margin-bottom:.2rem;">LOADED</div>
            <div style="font-size:.9rem;font-weight:500;word-break:break-all;">{st.session_state.filename}</div>
            <div style="font-size:.75rem;color:#64748b;margin-top:.3rem;">{len(st.session_state.content):,} characters</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🗑 Clear document"):
            for k in ["quiz","score","answers","checked","flashcards","fc_index",
                      "fc_show_answer","summary","content","filename"]:
                st.session_state[k] = None if k in ["quiz","flashcards","summary"] else (
                    0 if k in ["score","fc_index"] else (
                    False if k == "fc_show_answer" else (
                    {} if k in ["answers","checked"] else ""
                )))
            st.rerun()

    st.markdown('<div class="sidebar-section-title">📊 Session Stats</div>', unsafe_allow_html=True)
    total_q = len(st.session_state.quiz) if st.session_state.quiz else 0
    answered = len(st.session_state.checked)
    st.markdown(f"""
    <div class="stat-pill" style="margin-bottom:.5rem;border-radius:10px;padding:.6rem .9rem;">
        📝 <span>{total_q}</span> questions generated
    </div>
    <div class="stat-pill" style="margin-bottom:.5rem;border-radius:10px;padding:.6rem .9rem;">
        ✅ <span>{st.session_state.score}</span> correct answers
    </div>
    <div class="stat-pill" style="border-radius:10px;padding:.6rem .9rem;">
        🎯 <span>{answered}/{total_q}</span> attempted
    </div>
    """, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">✦ AI-Powered Learning</div>
    <div class="hero-title">Your Personal<br>Study Companion</div>
    <div class="hero-sub">Upload your notes and let AI generate quizzes, flashcards, and summaries in seconds.</div>
</div>
""", unsafe_allow_html=True)

# ── Upload ────────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Drop your PDF notes here", type="pdf", label_visibility="collapsed")

if uploaded_file and uploaded_file.name != st.session_state.filename:
    with st.spinner("Reading your notes…"):
        reader = PdfReader(uploaded_file)
        content = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                content += text
        st.session_state.content = content
        st.session_state.filename = uploaded_file.name
        st.session_state.quiz = None
        st.session_state.flashcards = None
        st.session_state.summary = None
        st.session_state.score = 0
        st.session_state.answers = {}
        st.session_state.checked = {}
    st.success(f"✅ **{uploaded_file.name}** loaded — {len(content):,} characters across {len(reader.pages)} page(s).")

# ── Main content (only if doc loaded) ────────────────────────────────────────
if st.session_state.content:
    content = st.session_state.content

    # ── Generate buttons ──────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        gen_quiz = st.button("⚡ Generate Quiz", use_container_width=True)
    with col2:
        gen_flash = st.button("🃏 Make Flashcards", use_container_width=True)
    with col3:
        gen_sum = st.button("📋 Summarise Notes", use_container_width=True)

    # ── Generate Quiz ─────────────────────────────────────────────────────────
    if gen_quiz:
        diff_note = f"Difficulty: {difficulty}." if difficulty != "Mixed" else ""
        type_note = (
            "All questions must be True/False with options ['True','False']."
            if question_type == "True / False"
            else "Mix MCQ and True/False questions."
            if question_type == "Mixed"
            else "All questions must be MCQ with 4 options."
        )
        with st.spinner("Crafting your quiz…"):
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{
                    "role": "user",
                    "content": f"""
You are an expert educator. Create EXACTLY {num_questions} quiz questions from the notes below.
{diff_note} {type_note}
Return ONLY a valid JSON array, no markdown, no explanation:
[
  {{"q":"question text","options":["A","B","C","D"],"answer":"A","explanation":"brief reason"}}
]
Notes:
{content[:4000]}
"""
                }]
            )
            raw = resp.choices[0].message.content.strip()
            clean = raw.replace("```json","").replace("```","").strip()
            try:
                st.session_state.quiz = json.loads(clean)
                st.session_state.score = 0
                st.session_state.answers = {}
                st.session_state.checked = {}
                st.rerun()
            except json.JSONDecodeError:
                st.error("Couldn't parse the quiz. Please try again.")

    # ── Generate Flashcards ───────────────────────────────────────────────────
    if gen_flash:
        with st.spinner("Creating flashcards…"):
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{
                    "role": "user",
                    "content": f"""
Create 8 flashcards from the notes below. Each card has a concise question (front) and answer (back).
Return ONLY valid JSON, no markdown:
[{{"front":"question","back":"answer"}}]
Notes:
{content[:4000]}
"""
                }]
            )
            raw = resp.choices[0].message.content.strip()
            clean = raw.replace("```json","").replace("```","").strip()
            try:
                st.session_state.flashcards = json.loads(clean)
                st.session_state.fc_index = 0
                st.session_state.fc_show_answer = False
                st.rerun()
            except json.JSONDecodeError:
                st.error("Couldn't parse flashcards. Please try again.")

    # ── Generate Summary ──────────────────────────────────────────────────────
    if gen_sum:
        with st.spinner("Summarising your notes…"):
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{
                    "role": "user",
                    "content": f"""
Summarise the following notes in a clear, structured way.
Use short paragraphs or bullet points. Highlight key concepts.
Notes:
{content[:5000]}
"""
                }]
            )
            st.session_state.summary = resp.choices[0].message.content.strip()
            st.rerun()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["⚡ Quiz", "🃏 Flashcards", "📋 Summary"])

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 1 — QUIZ
    # ──────────────────────────────────────────────────────────────────────────
    with tab1:
        if not st.session_state.quiz:
            st.markdown("""
            <div class="card" style="text-align:center;padding:3rem;">
                <div style="font-size:2.5rem;margin-bottom:.8rem;">⚡</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:600;margin-bottom:.4rem;">No Quiz Yet</div>
                <div style="font-size:.88rem;color:#64748b;">Hit <b>Generate Quiz</b> above to create questions from your notes.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            quiz = st.session_state.quiz
            answered = len(st.session_state.checked)
            total = len(quiz)
            pct = int(answered / total * 100) if total else 0

            # Progress
            st.markdown(f'<div class="progress-text">{answered}/{total} answered</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="score-bar-wrap">
                <div class="score-bar-fill" style="width:{pct}%"></div>
            </div>
            """, unsafe_allow_html=True)

            for i, q in enumerate(quiz):
                st.markdown(f"""
                <div class="q-card">
                    <div class="q-number">Question {i+1} of {total}</div>
                    <div class="q-text">{q['q']}</div>
                </div>
                """, unsafe_allow_html=True)

                choice = st.radio(
                    f"q_{i}",
                    q["options"],
                    key=f"radio_{i}",
                    label_visibility="collapsed",
                )
                st.session_state.answers[i] = choice

                c1, c2 = st.columns([1, 4])
                with c1:
                    check = st.button("Check", key=f"check_{i}", use_container_width=True)

                if check and i not in st.session_state.checked:
                    st.session_state.checked[i] = choice
                    if choice == q["answer"]:
                        st.session_state.score += 1
                    st.rerun()

                if i in st.session_state.checked:
                    user_ans = st.session_state.checked[i]
                    if user_ans == q["answer"]:
                        st.markdown(f'<div class="result-correct">✅ Correct!</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="result-wrong">❌ Incorrect — Correct answer: <b>{q["answer"]}</b></div>', unsafe_allow_html=True)
                    if "explanation" in q and q["explanation"]:
                        with st.expander("💡 Explanation"):
                            st.write(q["explanation"])

            # Final score
            if len(st.session_state.checked) == total:
                score = st.session_state.score
                pct_score = int(score / total * 100)
                grade = (
                    "🏆 Outstanding!" if pct_score >= 90 else
                    "🌟 Great work!" if pct_score >= 75 else
                    "👍 Good effort!" if pct_score >= 60 else
                    "📚 Keep studying!"
                )
                st.markdown(f"""
                <div class="final-score">
                    <div class="big-num">{score}/{total}</div>
                    <div class="grade">{grade} &nbsp;·&nbsp; {pct_score}%</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("🔄 Retake Quiz"):
                    st.session_state.score = 0
                    st.session_state.answers = {}
                    st.session_state.checked = {}
                    st.rerun()

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 2 — FLASHCARDS
    # ──────────────────────────────────────────────────────────────────────────
    with tab2:
        if not st.session_state.flashcards:
            st.markdown("""
            <div class="card" style="text-align:center;padding:3rem;">
                <div style="font-size:2.5rem;margin-bottom:.8rem;">🃏</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:600;margin-bottom:.4rem;">No Flashcards Yet</div>
                <div style="font-size:.88rem;color:#64748b;">Hit <b>Make Flashcards</b> above to generate study cards.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            cards = st.session_state.flashcards
            idx = st.session_state.fc_index
            card = cards[idx]

            st.markdown(f'<div class="progress-text">Card {idx+1} of {len(cards)}</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="score-bar-wrap">
                <div class="score-bar-fill" style="width:{int((idx+1)/len(cards)*100)}%"></div>
            </div>
            """, unsafe_allow_html=True)

            side = "ANSWER" if st.session_state.fc_show_answer else "QUESTION"
            text = card["back"] if st.session_state.fc_show_answer else card["front"]
            st.markdown(f"""
            <div class="flashcard">
                <div class="flashcard-label">{side}</div>
                <div class="flashcard-text">{text}</div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("◀ Previous", use_container_width=True):
                    st.session_state.fc_index = max(0, idx - 1)
                    st.session_state.fc_show_answer = False
                    st.rerun()
            with c2:
                label = "Show Question 🔼" if st.session_state.fc_show_answer else "Reveal Answer 🔽"
                if st.button(label, use_container_width=True):
                    st.session_state.fc_show_answer = not st.session_state.fc_show_answer
                    st.rerun()
            with c3:
                if st.button("Next ▶", use_container_width=True):
                    st.session_state.fc_index = min(len(cards)-1, idx + 1)
                    st.session_state.fc_show_answer = False
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔀 Shuffle Cards"):
                random.shuffle(st.session_state.flashcards)
                st.session_state.fc_index = 0
                st.session_state.fc_show_answer = False
                st.rerun()

            # All cards list
            with st.expander("📚 View all flashcards"):
                for j, c in enumerate(cards):
                    st.markdown(f"""
                    <div class="card" style="padding:1rem 1.2rem;margin-bottom:.6rem;">
                        <div style="font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#4f8ef7;margin-bottom:.4rem;">Card {j+1}</div>
                        <div style="font-weight:500;margin-bottom:.3rem;">{c['front']}</div>
                        <div style="font-size:.88rem;color:#64748b;">{c['back']}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 3 — SUMMARY
    # ──────────────────────────────────────────────────────────────────────────
    with tab3:
        if not st.session_state.summary:
            st.markdown("""
            <div class="card" style="text-align:center;padding:3rem;">
                <div style="font-size:2.5rem;margin-bottom:.8rem;">📋</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:600;margin-bottom:.4rem;">No Summary Yet</div>
                <div style="font-size:.88rem;color:#64748b;">Hit <b>Summarise Notes</b> above to get an AI overview.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="summary-box">{st.session_state.summary}</div>', unsafe_allow_html=True)
            if st.button("🔄 Re-summarise"):
                st.session_state.summary = None
                st.rerun()

else:
    # ── Empty state ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:.5rem;">
        <div class="card" style="flex:1;min-width:200px;padding:1.4rem 1.6rem;">
            <div style="font-size:1.6rem;margin-bottom:.6rem;">⚡</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:.3rem;">Smart Quizzes</div>
            <div style="font-size:.85rem;color:#64748b;line-height:1.6;">Generate MCQ or True/False quizzes with explanations.</div>
        </div>
        <div class="card" style="flex:1;min-width:200px;padding:1.4rem 1.6rem;">
            <div style="font-size:1.6rem;margin-bottom:.6rem;">🃏</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:.3rem;">Flashcards</div>
            <div style="font-size:.85rem;color:#64748b;line-height:1.6;">Flip through key concepts to reinforce your memory.</div>
        </div>
        <div class="card" style="flex:1;min-width:200px;padding:1.4rem 1.6rem;">
            <div style="font-size:1.6rem;margin-bottom:.6rem;">📋</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:.3rem;">AI Summary</div>
            <div style="font-size:.85rem;color:#64748b;line-height:1.6;">Get a concise overview of your full document.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
