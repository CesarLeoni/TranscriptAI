import streamlit as st
import requests
import io
from docx import Document
from fpdf import FPDF

# URL of your backend on laptop
BACKEND_URL = "http://127.0.0.1:8000/upload"

# production link
#BACKEND_URL = "https://transcriptai.onrender.com/upload"

# Title of the app
st.title("Audio Transcription + Document Generation by Cesar")

# Custom CSS for button styling
st.markdown("""
<style>
/* Center the Transcribe button */
    div.stButton > button {
        display: block;
        margin: 0 auto;
    }
    /* Target the first download button (Word) */
    div.stDownloadButton:nth-of-type(1) button {
        background-color: #1E90FF !important;
        color: white !important;
        border: none !important;
    }
    div.stDownloadButton:nth-of-type(1) button:hover {
        background-color: #0066CC !important;
    }

    /* Target the second download button (PDF) */
    div.stDownloadButton:nth-of-type(2) button {
        background-color: #FF4444 !important;
        color: white !important;
        border: none !important;
    }
    div.stDownloadButton:nth-of-type(2) button:hover {
        background-color: #CC0000 !important;
    }

    /* Center buttons in their columns */
    .stDownloadButton {
        display: flex;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for storing transcription
if 'transcription' not in st.session_state:
    st.session_state.transcription = None
if 'current_file' not in st.session_state:
    st.session_state.current_file = None

# Upload the audio file
uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])

# Clear transcription if a new file is uploaded
if uploaded_file and uploaded_file != st.session_state.current_file:
    st.session_state.transcription = None
    st.session_state.current_file = uploaded_file

# If file is uploaded, show the player and send to backend
if uploaded_file:
    st.audio(uploaded_file, format="audio/wav")

    if st.button("Transcribe"):
        # Send audio file to backend for transcription
        files = {"file": uploaded_file}
        response = requests.post(BACKEND_URL, files=files)

        if response.status_code == 200:
            # Convert transcription to Word document
            st.session_state.transcription = response.json().get("transcript")
        else:
            st.error("Error during transcription.")




# Display download buttons only if transcription exists in session state
if st.session_state.transcription and uploaded_file == st.session_state.current_file:
    st.success("Transcription completed!")
    # Convert transcription to Word document
    doc = Document()
    doc.add_heading(f"{uploaded_file.name} Transcription", 0)
    doc.add_paragraph(st.session_state.transcription)

    # Save Word file to BytesIO
    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)

    # Create PDF document
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"{uploaded_file.name} Transcription", ln=True, align='C')
    pdf.multi_cell(0, 10, st.session_state.transcription)

    # Save PDF to BytesIO
    pdf_output = pdf.output(dest='S').encode('latin-1')
    pdf_io = io.BytesIO(pdf_output)
    pdf_io.seek(0)

    # Create centered columns
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📝 Download Word",
            data=doc_io,
            file_name=f"{uploaded_file.name}_transcription.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

    with col2:
        st.download_button(
            label="📄 Download PDF",
            data=pdf_io,
            file_name=f"{uploaded_file.name}_transcription.pdf",
            mime="application/pdf",
            use_container_width=True
        )


    # Google Ads
# st.markdown("""
#     <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2114950528659296"
#             crossorigin="anonymous"></script>
#     <ins class="adsbygoogle"
#          style="display:block"
#          data-ad-client="ca-pub-2114950528659296"
#          data-ad-slot="XXXXX"
#          data-ad-format="auto"></ins>
#     <script>
#          (adsbygoogle = window.adsbygoogle || []).push({});
#     </script>
#     """, unsafe_allow_html=True)