import streamlit as st
import requests
import io
from docx import Document

# URL of your backend on laptop
#BACKEND_URL = "http://127.0.0.1:8000/upload"

# production link
BACKEND_URL = "https://transcriptai.onrender.com/upload"

# Title of the app
st.title("Audio Transcription and Word Document by Cesar")

# Upload the audio file
uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])

# If file is uploaded, show the player and send to backend
if uploaded_file:
    st.audio(uploaded_file, format="audio/wav")

    if st.button("Transcribe"):
        # Send audio file to backend for transcription
        files = {"file": uploaded_file}
        response = requests.post(BACKEND_URL, files=files)

        if response.status_code == 200:
            st.success("Transcription completed!")
            # Convert transcription to Word document
            transcription = response.json().get("transcript")

            doc = Document()
            doc.add_heading("Transcription", 0)
            doc.add_paragraph(transcription)

            # Save Word file to disk and offer for download
            doc_io = io.BytesIO()
            doc.save(doc_io)
            doc_io.seek(0)

            st.download_button(
                label="Download Transcription",
                data=doc_io,
                file_name="transcription.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        else:
            st.error("Error during transcription.")

    # Google Ads
    st.markdown("""
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2114950528659296" 
            crossorigin="anonymous"></script>
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-2114950528659296" 
         data-ad-slot="XXXXX" 
         data-ad-format="auto"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
    """, unsafe_allow_html=True)

