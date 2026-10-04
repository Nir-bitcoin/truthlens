# retrieval.py
# Kaam: Question ke liye top-k chunks nikalna (FAST)

from embeddings import get_model, load_index


def retrieve(query, top_k=5):
    index, chunks, metadata = load_index()
    model = get_model()

    query_vec = model.encode([query]).astype("float32")
    distances, indices = index.search(query_vec, top_k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        results.append({
            "text": chunks[idx],
            "file": metadata[idx]["file"],
            "language": metadata[idx]["language"],
            "page": metadata[idx].get("page", "?"),
            "score": float(dist)
        })

    return results