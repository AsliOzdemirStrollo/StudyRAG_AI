import chromadb
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="chroma_db")

collection = chroma_client.get_or_create_collection(
    name="studyrag_collection"
)


def reset_vector_collection():
    existing_ids = collection.get()["ids"]

    if existing_ids:
        collection.delete(ids=existing_ids)


def build_vector_store(chunk_data):
    reset_vector_collection()

    texts = [chunk["text"] for chunk in chunk_data]
    embeddings = embedding_model.encode(texts).tolist()
    ids = [f"chunk_{i}" for i in range(len(chunk_data))]
    metadatas = [{"page": chunk["page"]} for chunk in chunk_data]

    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )


def retrieve_relevant_chunks(question, top_k=4, candidate_k=10):
    question_embedding = embedding_model.encode([question]).tolist()[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=candidate_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    candidate_embeddings = embedding_model.encode(documents)

    rerank_scores = []

    for i, embedding in enumerate(candidate_embeddings):
        similarity = sum(
            a * b for a, b in zip(question_embedding, embedding)
        )

        rerank_scores.append(
            (
                similarity,
                documents[i],
                metadatas[i]
            )
        )

    rerank_scores.sort(reverse=True, key=lambda x: x[0])
    top_results = rerank_scores[:top_k]

    retrieved_chunks = []

    for score, doc, meta in top_results:
        retrieved_chunks.append(
            {
                "text": doc,
                "page": meta["page"],
                "score": score
            }
        )

    return retrieved_chunks