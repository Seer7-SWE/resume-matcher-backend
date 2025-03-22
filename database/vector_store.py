import faiss
import numpy as np
import sqlite3
from sentence_transformers import SentenceTransformer

# Load Embedding Model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# FAISS Index & Database Connection
DB_PATH = "C:/Users/SELVAMANI RAJENDRAN/Documents/resume-analyzer/backend/database/resume_db.sqlite"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Initialize FAISS index
DIMENSION = 384  # Output size of MiniLM model
index = faiss.IndexFlatL2(DIMENSION)

def store_resume_embedding(resume_id, resume_text):
    """Generates and stores an embedding for a given resume."""
    try:
        vector = embedding_model.encode([resume_text])[0]
        index.add(np.array([vector], dtype=np.float32))
        
        # Save to SQLite (optional for ID tracking)
        cursor.execute("INSERT INTO resumes (id, text) VALUES (?, ?)", (resume_id, resume_text))
        conn.commit()
        
        return {"message": "Resume stored successfully"}
    except Exception as e:
        print(f"Error storing resume embedding: {e}")
        return {"error": str(e)}
