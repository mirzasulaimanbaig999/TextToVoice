import streamlit as st
import openai
import os
import re

# Load API key securely from Streamlit secrets
openai.api_key = os.getenv("OPENAI_API_KEY")

# Title
st.title("🎙️ TextToVoice (Arabic Qur’an + English Narration)")
st.write("Paste Surah text (Arabic + English) below to generate soulful recitation with tajweed and Fable voice narration.")

# ---------------------------
# Password Protection
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Enter access password:", type="password")
    if st.button("🔑 Submit Password"):
        if password == os.getenv("APP_PASSWORD"):
            st.session_state.authenticated = True
            st.rerun()  # unlock immediately
        else:
            st.error("❌ Wrong password. Try again.")
    st.stop()

# ---------------------------
# Helper: Apply Tajweed Rules
# ---------------------------
def apply_tajweed(text):
    # Huruf al-Muqattaʿat (disjointed letters)
    replacements = {
        "يسٓ": "يا سين",
        "الم": "ألف لام ميم",
        "حم": "حا ميم",
        "طه": "طا ها",
        "طسم": "طا سين ميم",
        "كهيعص": "كاف ها يا عين صاد",
        "عسق": "عين سين قاف",
        "نٓ": "نون"
    }
    for k, v in replacements.items():
        text = re.sub(k, v, text)

    # Waqf signs → convert to silent pauses
    waqf_map = {
        "۝": " … ",
        "م": " … ",
        "ط": " … ",
        "ج": " , ",
        "ق": " , ",
        "لا": "",   # no pause
        "قف": " … "
    }
    for k, v in waqf_map.items():
        text = text.replace(k, v)

    return text

# ---------------------------
# Input Box (mobile-friendly)
# ---------------------------
st.markdown("### ✍️ Enter Surah Content")
raw_text = st.text_area(
    "Paste Surah (Arabic + English):",
    value=st.session_state.get("text_input", ""),
    key="text_input",
    height=250,
    placeholder="بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ\n\nIn the name of Allah, the Entirely Merciful, the Especially Merciful..."
)

# Preprocess text for tajweed
text = apply_tajweed(raw_text)

st.write("")

# ---------------------------
# Permanent Instructions
# ---------------------------
instructions = """
For Arabic:
- Recite exactly like a professional Qur’an qāri’ with **full tajweed**.
- Apply rules: madd (elongation), ghunnah (nasal), qalqalah (echo), and proper waqf (pauses).
- When you see “…” or “,” in the text, **pause naturally but do not read them aloud**.
- If a verse contains disjointed letters (يسٓ, الم, حم, نٓ), recite each separately with full elongation (e.g., يسٓ → “Yāaa Sīn”).
- Recite **very slowly, reverently, and naturally with breathing**, like an imam leading prayer.
- It must sound **human, soulful, and never robotic**.

For English:
- After each Arabic verse, narrate the English translation clearly.
- Use a calm, professional, documentary-style tone (like David Attenborough or BBC World Service).
- Speak warmly and respectfully, like a professional audiobook.

Always separate Arabic and English with a pause.
Arabic must flow as soulful qirāʾt with tajweed, English follows softly and professionally.
"""

# ---------------------------
# Audio Generation
# ---------------------------
if st.button("🎤 Generate Audio"):
    if not text.strip():
        st.warning("⚠️ Please paste Surah text first.")
    else:
        out_file = "surah_output.mp3"
        with openai.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="fable",  # locked to Fable voice
            input=text
        ) as response:
            response.stream_to_file(out_file)

        st.audio(out_file)
        with open(out_file, "rb") as f:
            st.download_button("⬇️ Download Audio", f, file_name="surah_output.mp3")
