from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Depends, Request
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure 'uploads' directory exists
UPLOAD_FOLDER = "backend/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --------------------------
# Basic Endpoint for Testing
@app.get("/")
def home():
    return {"message": "AI Resume Analyzer is Running 🚀"}

# --------------------------
# Endpoint: Batch Resume Upload (for background processing)
@app.post("/upload-resumes/")
async def upload_resumes(files: List[UploadFile] = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    for file in files:
        file_path = f"{UPLOAD_FOLDER}/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        # Process file asynchronously (simulate processing)
        background_tasks.add_task(lambda path: time.sleep(5) or print(f"Processed resume: {path}"), file_path)
    return {"message": "Resumes are being processed in the background"}

# --------------------------
# Endpoint: Rate-limited Single Resume Upload and Embedding Storage
@app.post("/upload-resume/")
@limiter.limit("5/minute")
async def upload_resume(request: Request, file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    file_path = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    resume_text = extract_text_from_pdf(file_path)
    if resume_text:
        background_tasks.add_task(store_resume_embedding, file.filename, resume_text)
        return {"message": f"Resume {file.filename} uploaded & processed"}
    else:
        return {"error": "Could not extract text from resume"}

# --------------------------
# Endpoint: Resume Search using FAISS
@app.get("/search-resume/")
async def search_resume_endpoint(query: str, k: int = 1):
    return search_resume(query, k)
