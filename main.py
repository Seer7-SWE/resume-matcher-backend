from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Depends, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from typing import List
import time
import os

# Import your resume parser and vector store functions
from utils.resume_parser import extract_text_from_pdf  # Assuming you use this for PDF extraction
from database.vector_store import store_resume_embedding  # Function to store embeddings
from database.search import search_resume  # New search functionality

# Initialize FastAPI app
app = FastAPI()

# Initialize Rate Limiter and add middleware
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Restrict to frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Ensure 'uploads' directory exists
UPLOAD_FOLDER = "backend/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to simulate background processing
def process_resume(file_path: str):
    time.sleep(5)  # Simulate delay
    print(f"✅ Processed resume: {file_path}")

# --------------------------
# Basic Endpoint for Testing
@app.get("/")
def home():
    return {"message": "AI Resume Analyzer is Running 🚀"}

# --------------------------
# Endpoint: Batch Resume Upload (for background processing)
@app.post("/upload-resumes/")
async def upload_resumes(files: List[UploadFile] = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        try:
            with open(file_path, "wb") as f:
                f.write(await file.read())
            background_tasks.add_task(process_resume, file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")

    return {"message": "Resumes are being processed in the background"}

# --------------------------
# Endpoint: Rate-limited Single Resume Upload and Embedding Storage
@app.post("/upload-resume/")
@limiter.limit("5/minute")
async def upload_resume(request: Request, file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        resume_text = extract_text_from_pdf(file_path)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from resume")
        
        background_tasks.add_task(store_resume_embedding, file.filename, resume_text)
        return {"message": f"Resume {file.filename} uploaded & processed"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# --------------------------
# Endpoint: Resume Search using FAISS
@app.get("/search-resume/")
async def search_resume_endpoint(query: str, k: int = 1):
    try:
        return search_resume(query, k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
