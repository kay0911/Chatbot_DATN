from app.database import data_collection
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
collection = data_collection

def get_similar_answer(query: str, threshold: float = 0.95):
    query_embedding = embedding_model.embed_query(query)

    all_docs = list(collection.find({}, {"question": 1, "answer": 1, "embedding": 1}))
    if not all_docs:
        return None

    def cosine_sim(a, b):
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    best_match = max(
        all_docs,
        key=lambda doc: cosine_sim(query_embedding, doc["embedding"]),
        default=None
    )

    score = cosine_sim(query_embedding, best_match["embedding"])
    return best_match["answer"] if score >= threshold else None

def save_to_memory(question: str, answer: str):
    embedding = embedding_model.embed_query(question)
    collection.insert_one({
        "question": question,
        "answer": answer,
        "embedding": embedding
    })
