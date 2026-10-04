# embeddings.py
# Kaam: Chunks + embeddings + FAISS index (STRONG MODEL)

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os

# STRONG MODEL
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def embed_chunks(chunks):
    model = get_model()
    embeddings = model.encode(chunks, batch_size=32, show_progress_bar=False)
    return np.array(embeddings).astype("float32")


def build_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index


def save_index(index, chunks, metadata, path="data/index"):
    os.makedirs(path, exist_ok=True)
    faiss.write_index(index, f"{path}/faiss.index")
    with open(f"{path}/chunks.pkl", "wb") as f:
        pickle.dump({"chunks": chunks, "metadata": metadata}, f)


def load_index(path="data/index"):
    index = faiss.read_index(f"{path}/faiss.index")
    with open(f"{path}/chunks.pkl", "rb") as f:
        data = pickle.load(f)
    return index, data["chunks"], data["metadata"]


def process_documents(documents):
    all_chunks = []
    all_metadata = []

    for doc in documents:
        for page_data in doc["pages"]:
            page_num = page_data["page"]
            page_text = page_data["text"]
            chunks = chunk_text(page_text)
            for chunk in chunks:
                all_chunks.append(chunk)
                all_metadata.append({
                    "file": doc["file"],
                    "language": doc["language"],
                    "page": page_num
                })

    embeddings = embed_chunks(all_chunks)
    index = build_index(embeddings)
    save_index(index, all_chunks, all_metadata)

    return index, all_chunks, all_metadata