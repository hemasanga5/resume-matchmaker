import json
import random
import time
 
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
 
# ---------- Setup ----------
load_dotenv()
client = genai.Client(http_options=types.HttpOptions(timeout=120000))
MODEL = "gemini-3.5-flash"
 
ROAST_LEVELS = {
    "Gentle 🧸": "Be warm, encouraging and lightly playful, like a supportive best friend.",
    "Honest 😏": "Be witty and cheeky, with playful teasing, like a funny friend who tells the truth.",
    "Savage 🔥": "Be a hilarious, savage roast comic. Roast the RESUME hard, never the person's identity, "
                 "looks or background. Keep it clean, clever and ultimately helpful.",
}
 
LOADING_LINES = [
    "Swiping through your bullet points... 👆",
    "Asking the job description if it's ready for commitment... 💍",
    "Checking if 'proficient in Excel' is still a personality... 📊",
    "Consulting the recruiter gods... 🔮",
    "Counting how many times you wrote 'synergy'... 🤝",
    "Running a background check on your buzzwords... 🕵️‍♀️",
]
 
VERDICTS = [
    (90, "💍 SOULMATES", "Book the venue. This resume and this job were made for each other."),
    (75, "💕 STRONG CHEMISTRY", "There's definitely a spark. A few tweaks and it's official."),
    (50, "🤷‍♀️ IT'S COMPLICATED", "Some good vibes, some red flags. Worth a second date with edits."),
    (25, "🙃 JUST FRIENDS", "The job likes you... as a friend. Time for a glow-up."),
    (0, "💔 LEFT-SWIPED", "Oof. This job ghosted you before the first message."),
]
 
 
def get_verdict(score):
    for minimum, title, line in VERDICTS:
        if score >= minimum:
            return title, line
    return VERDICTS[-1][1], VERDICTS[-1][2]
 
 
# ---------- The AI part ----------
def match_resume(resume, job_description, roast_level):
    prompt = (
        "You are 'Cupid the Recruiter', a funny matchmaker who sets resumes up with jobs.\n"
        f"Tone: {ROAST_LEVELS[roast_level]}\n"
        "Use dating and romance jokes where they fit. Be funny, but the analysis must be accurate "
        "and the advice genuinely useful.\n\n"
        "Compare the RESUME to the JOB DESCRIPTION.\n"
        "Respond ONLY with JSON in exactly this shape:\n"
        "{\n"
        '  "match_score": <integer from 0 to 100, honest and realistic>,\n'
        '  "one_liner": "<a witty one-sentence verdict>",\n'
        '  "summary": "<2-3 funny but honest sentences about the overall match>",\n'
        '  "matching_keywords": ["<skill or keyword found in both>", ...],\n'
        '  "missing_keywords": ["<important keyword from the job that the resume lacks>", ...],\n'
        '  "suggestions": ["<specific, actionable fix, phrased with humour>", ...],\n'
        '  "pickup_line": "<a cheesy pickup line this resume could use on this job>"\n'
        "}\n"
        "Keywords should be skills, tools, qualifications and responsibilities named in the job description.\n\n"
        f"RESUME:\n{resume}\n\n"
        f"JOB DESCRIPTION:\n{job_description}\n"
    )
 for attempt in range(3):
  try:
   response = client.models.generate_content(
    model=MODEL,
    contents=prompt,
    config=types.GenerateContentConfig(response_mime_type="application/json"),
       )
   return json.loads(response.text)
  except Exception as error:
   temporary = any(code in str(error) for code in ["504", "503", "DEADLINE", "UNAVAILABLE"])
   if attempt == 2 or not temporary:
    raise
    time.sleep(3 * (attempt + 1))
 
 
# ---------- The page ----------
st.set_page_config(page_title="Resume Matchmaker", page_icon="💘", layout="wide")
 
st.markdown(
    """
    <style>
    .big-title {
        font-size: 3rem; font-weight: 800; text-align: center; margin-bottom: 0;
        background: linear-gradient(90deg, #ff4b8b, #ff9a3c);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .subtitle { text-align: center; font-size: 1.15rem; opacity: 0.8; margin-top: 0.2rem; }
    .verdict-card {
        text-align: center; padding: 1.5rem; border-radius: 18px; margin: 1rem 0;
        background: linear-gradient(135deg, rgba(255,75,139,0.15), rgba(255,154,60,0.15));
        border: 2px solid rgba(255,75,139,0.4);
    }
    .verdict-score { font-size: 4rem; font-weight: 800; margin: 0; }
    .verdict-title { font-size: 1.8rem; font-weight: 700; margin: 0.2rem 0; }
    .pickup {
        font-style: italic; font-size: 1.2rem; text-align: center; padding: 1rem;
        border-radius: 12px; background: rgba(255,154,60,0.12);
    }
    </style>
    """,
    unsafe_allow_html=True,
)
 
st.markdown('<p class="big-title">💘 Resume Matchmaker</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Is your resume their type? Let Cupid the Recruiter decide. 🏹</p>',
    unsafe_allow_html=True,
)
 
with st.sidebar:
    st.header("⚙️ Settings")
    roast_level = st.radio("Roast level", list(ROAST_LEVELS.keys()), index=1)
    st.caption("Gentle for your feelings. Savage for your friends. 😈")
    st.divider()
    st.caption("Made with 💖, Python and questionable jokes by Hema.")
 
col1, col2 = st.columns(2)
with col1:
    resume = st.text_area(
        "🙋 Your resume (the single)",
        height=320,
        placeholder="Paste your resume here. Don't be shy, we've seen worse.",
    )
with col2:
    job_description = st.text_area(
        "💼 The job description (the crush)",
        height=320,
        placeholder="Paste the job you're pining for...",
    )
 
if st.button("💘 Find out if it's a match", type="primary", use_container_width=True):
    if not resume.strip() or not job_description.strip():
        st.warning("It takes two to tango 💃🕺 Paste both your resume AND the job description.")
    else:
        with st.spinner(random.choice(LOADING_LINES)):
            try:
                result = match_resume(resume, job_description, roast_level)
            except Exception as error:
                st.error(f"Cupid tripped over his own arrow 🏹💥 Error: {error}")
                st.stop()
 
        score = min(max(int(result.get("match_score", 0)), 0), 100)
        title, line = get_verdict(score)
 
        st.markdown(
            f"""
            <div class="verdict-card">
                <p class="verdict-score">{score}%</p>
                <p class="verdict-title">{title}</p>
                <p>{line}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(score / 100)
 
        if score >= 90:
            st.balloons()
        elif score < 25:
            st.snow()
 
        st.subheader("🗣️ Cupid says")
        st.markdown(f"**{result.get('one_liner', '')}**")
        st.write(result.get("summary", ""))
 
        left, right = st.columns(2)
        with left:
            st.markdown("### 💚 What you have in common")
            for keyword in result.get("matching_keywords", []):
                st.markdown(f"- {keyword}")
        with right:
            st.markdown("### 🚩 Red flags (missing keywords)")
            for keyword in result.get("missing_keywords", []):
                st.markdown(f"- {keyword}")
 
        st.markdown("### 💅 Glow-up tips")
        for tip in result.get("suggestions", []):
            st.markdown(f"- {tip}")
 
        st.markdown("### 😘 Your official pickup line")
        st.markdown(
            f'<div class="pickup">"{result.get("pickup_line", "")}"</div>',
            unsafe_allow_html=True,
        )
 
