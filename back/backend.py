from fastapi import FastAPI, File, UploadFile, HTTPException
import openai
import os
from dotenv import load_dotenv
import io
import uuid
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Get API key from .env
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Supported audio formats for Whisper API
SUPPORTED_FORMATS = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']

# Parent directory for storing files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Transcript API!"}


@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    try:
        # Log the file name and size
        print(f"Received file: {file.filename}, size: {file.size} bytes")

        # Check if the file extension is valid
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in SUPPORTED_FORMATS:
            raise HTTPException(status_code=400,
                                detail=f"Unsupported file format. Supported formats are: {', '.join(SUPPORTED_FORMATS)}")

        # Create a subfolder based on the current date and time (optional for better organization)
        # timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        subfolder = os.path.join(UPLOAD_DIR)
        os.makedirs(subfolder, exist_ok=True)

        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(subfolder, unique_filename)

        # Save the file to the subfolder
        with open(file_path, "wb") as f:
            file_content = await file.read()
            f.write(file_content)

        # Debugging: Log the file being passed to Whisper API
        print(f"Passing file: {file_path} to Whisper API")

        # Debugging: Log type of object passed to Whisper API
        print(f"Passing {type(file_content)} to Whisper API")

        # Call the OpenAI Whisper API
        with open(file_path, "rb") as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json"  # Request verbose JSON response
        )

        # Extract the transcribed text and detected language
        text = response.text

        # Here you'd process the file (transcription logic)
        # Replace this with actual transcription logic
        # transcription = "This is a mock transcription."

        if not text:
            raise HTTPException(status_code=500, detail="Transcription failed. No text returned from Whisper API.")

        # Print the transcription result for debugging
        print("Transcription:", text)

        # Delete the file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

        print("Temporary audio files deleted")
        # Save the file or perform operations (e.g., using Whisper API)
        return {"transcript": text}
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return {"error": str(e)}