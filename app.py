import streamlit as st
import openai
import os

# Load API key securely from Streamlit secrets
openai.api_key = os.getenv("OPENAI_API_KEY")

# Title
st.title("🎙️ TextToVoice (Arabic Qur’an + English Narration)")
st.write("Paste Surah text (Arabic + English) below to generate soulful recitation with Fable voice.")

# Password protection using session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Enter access password:", type="password")
    if st.button("🔑 Submit Password"):
        if password == os.getenv("APP_PASSWORD"):
            st.session_state.authenticated = True
            st.success("✅ Access granted. You can now use the app.")
        else:
            st.error("❌ Wrong password. Try again.")
    st.stop()

# Input box (session state fix for mobile copy-paste)
if "text_input" not in st.session_state:
    st.session_state.text_input = ""

text = st.text_area("✍️ Paste Surah (Arabic + English):", value=st.session_state.text_input, key="text_input")

# Permanent Instructions (guiding narration style only)
instructions = """
For Arabic text: Recite exactly like a professional Qur’an qāri’ with full tajweed. Use very long qirāʾt: stretch the vowels (madd) fully, elongate every sound naturally, sustain ghunnah (nasal sounds), and apply proper waqf (pauses) at the end of each verse. The Arabic recitation must be delivered in a strong, clear, and resonant voice — louder and more powerful than the English narration — with depth and richness, like an imam reciting in a masjid. Keep the recitation extremely slow, soulful, and natural, with realistic breathing and deep reverence. It must sound completely human and never robotic.  

For English text: After completing each Arabic verse, always narrate the English translation. Do not skip any English text. Use the natural strength of the Fable voice: calm, professional, warm, and clear, similar to David Attenborough or a BBC World Service presenter. Speak with measured pacing, smooth emphasis, and a respectful, documentary-style delivery. The English narration must sound fully human, like a professional audiobook.  

Always separate Arabic and English with a clear, natural pause. Arabic should flow like a live qirāʾt recitation in a strong and resonant voice, while English should follow in a softer, professional narration tone — creating a balanced, natural experience.
"""

# Generate Audio
if st.button("🎤 Generate Audio"):
    if not text.strip():
        st.warning("Please paste Surah text first.")
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
