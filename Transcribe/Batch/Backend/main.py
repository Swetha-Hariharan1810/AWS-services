from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uvicorn
import whisper
import json

from upload_to_s3 import upload_to_s3
from config import region_name, bucket
from get_transcribe import transcribe_file
from uuid import uuid4

model = whisper.load_model("tiny.en")

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:4800",  # Update this to the actual origin(s) you want to allow
    "http://127.0.0.1:4800"   # Add more origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Ensure the upload directory exists
os.makedirs("uploaded_files", exist_ok=True)

# Upload endpoint using whisper model
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), file_id: str = Form(...)):
    try:
        file_location = os.path.join("uploaded_files", file_id + ".wav")
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #'model.transcribe' helps in  transcription l
        absolute_path = os.path.abspath(file_location)
        print(absolute_path)
        result = model.transcribe(absolute_path)
        
        response_message = f"File saved to: {file_location}"
        return JSONResponse(content={"message": result["text"]}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Upload endpoint using aws trascribe Batch
# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...), file_id: str = Form(...)):
#     try:
#         # Create the full file path using the file_id
#         file_location = os.path.join("uploaded_files", file_id + ".wav")
#         with open(file_location, "wb") as buffer:
#              shutil.copyfileobj(file.file, buffer)
#         filename = os.path.abspath(file_location)
#         job_name = str(uuid4())
#         file_uri = upload_to_s3(filename)
#         if file_uri:
#             response = transcribe_file(job_name=job_name,file_uri=file_uri,transcribe_client=bucket)

#         return JSONResponse(content={"message": response}, status_code=200)
    
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

