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
    # Expand disjointed letters (huruf al-muqattaʿāt)
    replacements = {
        "يسٓ": "يــــا ســـــيـــــن",
        "الم": "أ لــــيـــــف لــــام مــــيــــم",
        "حم": "حــــا مــــيــــم",
        "طه": "طــــا هــــا",
        "طسم": "طــــا ســــيــــن مــــيــــم",
        "كهيعص": "كــــاف هــــا يـــــا عــــيــــن صـــــاد",
        "عسق": "عــــيــــن ســـــيــــن قــــاف",
        "نٓ": "نـــــــو ن"
    }

    for k, v in replacements.items():
        text = re.sub(k, v, text)

    # Handle common waqf (pause) symbols
    waqf_map = {
        "۝": " [PAUSE: end of verse] ",
        "م": " [MANDATORY PAUSE] ",
        "ط": " [COMPLETE PAUSE] ",
        "ج": " [OPTIONAL PAUSE] ",
        "ق": " [PERMISSIBLE PAUSE] ",
        "لا": " [DO NOT PAUSE] ",
        "قف": " [STOP HERE] "
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

# Preprocess input for tajweed
text = apply_tajweed(raw_text)

st.write("")

# ---------------------------
# Permanent Instructions
# ---------------------------
instructions = """
For Arabic recitation:
- Recite like a professional Qur’an qāri’ with **full tajweed**. 
- Apply rules: **madd (elongation), ghunnah (nasal sounds), qalqalah (echo), ikhfāʾ, idghām, and waqf (pauses)**.
- At the **end of each verse or waqf symbol (۝, م, ط, ج, قف, etc.)**, pause naturally, just as in tajweed.
- If the verse has disjointed letters (ḥurūf al-muqattaʿāt, like يسٓ, الم, حم, نٓ), 
  recite each letter separately with **elongated madd** (e.g., يسٓ → “Yāaaa Sīīn”).
- Recite **very slowly, with reverence, humility, and realistic breathing**, like an imam leading prayer. 
- The recitation must sound **human and soulful, never robotic**.

For English narration:
- After completing each Arabic verse, **always narrate the English translation**.
- Speak calmly, warmly, and professionally (like David Attenborough or BBC World Service).
- Use measured pacing, clear emphasis, and respectful tone, like a professional audiobook.

General:
- Always **separate Arabic and English with a pause**.
- Arabic flows as soulful qirāʾt with tajweed, English follows softly and professionally.
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
