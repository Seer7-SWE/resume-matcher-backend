import faiss
import numpy as np
import sqlite3
import os
from sentence_transformers import SentenceTransformer

# Load Embedding Model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Define the database path (ensure it exists)
DB_DIR = "/app/database"
DB_PATH = os.path.join(DB_DIR, "resumes.db")

# Ensure the database directory exists
os.makedirs(DB_DIR, exist_ok=True)

# Create connection
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id TEXT PRIMARY KEY,
        text TEXT NOT NULL
    )
""")
conn.commit()

# Initialize FAISS index
DIMENSION = 384  # Output size of MiniLM model
index = faiss.IndexFlatL2(DIMENSION)

def store_resume_embedding(resume_id, resume_text):
    """Generates and stores an embedding for a given resume."""
    try:
        vector = embedding_model.encode([resume_text])[0]
        index.add(np.array([vector], dtype=np.float32))
        
        # Save to SQLite
        cursor.execute("INSERT INTO resumes (id, text) VALUES (?, ?)", (resume_id, resume_text))
        conn.commit()
        
        return {"message": "Resume stored successfully"}
    except Exception as e:
        print(f"Error storing resume embedding: {e}")
        return {"error": str(e)}
