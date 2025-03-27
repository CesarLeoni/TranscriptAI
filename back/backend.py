from fastapi import FastAPI, File, UploadFile
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Get API key from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    audio_content = await file.read()

    response = openai.Audio.transcribe(
        model="whisper-1",  # Uses Whisper API (Turbo version)
        file=audio_content,
        api_key=OPENAI_API_KEY  # Pass API key securely
    )

    return {"transcript": response["text"]}
