from fastapi import FastAPI, File, UploadFile, HTTPException
import openai
import os
from dotenv import load_dotenv
import io
import uuid
from datetime import datetime
import subprocess


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


# Call GPT-3.5 or GPT-4 to clean up the transcription text
def clean_text_with_gpt(text):
    prompt = (f"Please clean up the following transcription text:\n\n{text}\n\nMake sure it is properly spaced, no all-caps, and formatted correctly. "
              f"Make sure it is prepared to be added to a word document and look nice. Do not add anything else! I don't want any comments, just the text I provided but nicely formatted.")

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt},
        ],
        model="gpt-4o-mini-2024-07-18",
    )
    response = chat_completion.choices[0].message.content.strip()
    return response


def convert_to_wav(input_path: str, output_path: str):
    subprocess.run([
        'ffmpeg', '-y', '-i', input_path,
        '-ar', '16000', '-ac', '1',
        '-c:a', 'pcm_s16le', output_path
    ], check=True)


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

        # If it's an .m4a file, convert it to .wav
        if file_extension == "m4a":
            wav_path = file_path.replace(".m4a", ".wav")
            convert_to_wav(file_path, wav_path)
            audio_path_to_send = wav_path
        else:
            audio_path_to_send = file_path

        # Call the Whisper API
        with open(audio_path_to_send, "rb") as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json"
            )

        # Extract the transcribed text
        text = response.text

        text = clean_text_with_gpt(text)

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

        # Also delete the .wav version if it was created
        if file_extension == "m4a" and os.path.exists(wav_path):
            os.remove(wav_path)

        print("Temporary audio files deleted")
        # Save the file or perform operations (e.g., using Whisper API)
        return {"transcript": text}
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return {"error": str(e)}