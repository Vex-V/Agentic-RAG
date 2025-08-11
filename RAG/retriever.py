from RAG.utils1 import *
from sentence_transformers import SentenceTransformer
import torch
import faiss
import numpy as np

def get_relevant_chunks(url, questions, top_k=5 ):
    
    if 'pdf' not in url:
        contexts = {}
        for q in questions:
            contexts[q] = ""
        return contexts
    device = "cuda" if torch.cuda.is_available() else "cpu"

    chunks = EandCL(url, 80,20)
    model = SentenceTransformer("BAAI/bge-base-en", device=device)
    model.half()
    embeddings = model.encode(chunks,batch_size=64, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True)

    d = embeddings.shape[1] 
    index = faiss.IndexFlatIP(d)
    index.add(np.array(embeddings))
    contexts = {}
    
    for question in questions:

        query_embedding = model.encode([question], normalize_embeddings=True)
        D, I = index.search(np.array(query_embedding), top_k)
        top_chunks = [chunks[i] for i in I[0]]
        contexts[question] = " ".join(top_chunks)
        
    return contexts

