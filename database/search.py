import sqlite3
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Path to your SQLite database (make sure it exists and that your vector_store inserts embeddings)
DB_PATH = "backend/database/resumes.db"

def load_resume_embeddings():
    """
    Load stored resume embeddings from the SQLite database.
    Assume your table 'resumes' has columns: id, filename, resume_text, embedding (BLOB).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT filename, embedding FROM resumes")
    results = cursor.fetchall()
    conn.close()

    filenames = []
    embeddings_list = []
    for filename, emb_blob in results:
        filenames.append(filename)
        # Convert BLOB to numpy array (assumes embedding was saved as raw bytes of np.float32 array)
        emb_array = np.frombuffer(emb_blob, dtype=np.float32)
        embeddings_list.append(emb_array)
    
    if embeddings_list:
        embeddings = np.vstack(embeddings_list)
    else:
        embeddings = np.array([], dtype=np.float32)
    
    return filenames, embeddings

def create_faiss_index(embeddings, dimension):
    """
    Create a FAISS index with the given embeddings.
    """
    index = faiss.IndexFlatL2(dimension)
    if embeddings.size > 0:
        index.add(embeddings)
    return index

def search_resume(query: str, k: int = 1):
    """
    Generate an embedding for the query using SentenceTransformer, build a FAISS index
    from stored resume embeddings, and return the top k matching resume filenames.
    """
    # Load the embedding model (this model should be the same as used in vector_store.py)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode([query], convert_to_numpy=True).astype(np.float32)
    
    filenames, embeddings = load_resume_embeddings()
    if embeddings.size == 0:
        return {"error": "No resumes stored in database."}
    
    dimension = embeddings.shape[1]
    index = create_faiss_index(embeddings, dimension)
    
    distances, indices = index.search(query_embedding, k)
    
    results = []
    for i in indices[0]:
        if i < len(filenames):
            results.append(filenames[i])
    return {"results": results, "distances": distances.tolist()}
