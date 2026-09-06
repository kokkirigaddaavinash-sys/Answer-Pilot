def __init__(self, collection):
    self.collection = collection

    self.embedding_model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

def add_documents(
    self,
    chunks,
    filename
):
    if not chunks:
        return 0

    embeddings = self.embedding_model.encode(
        chunks,
        show_progress_bar=False
    ).tolist()

    import uuid

    ids = [
        f"{uuid.uuid4().hex}_{index}"
        for index in range(len(chunks))
    ]

    metadatas = [
        {
            "filename": filename,
            "chunk_index": index
        }
        for index in range(len(chunks))
    ]

    self.collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)

def search(
    self,
    query,
    top_k=5
):
    if not query:
        return {
            "documents": [],
            "metadatas": []
        }

    collection_count = self.collection.count()

    if collection_count == 0:
        return {
            "documents": [],
            "metadatas": []
        }

    top_k = min(
        top_k,
        collection_count
    )

    query_embedding = self.embedding_model.encode(
        query,
        show_progress_bar=False
    ).tolist()

    results = self.collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=top_k
    )

    documents = results.get(
        "documents",
        [[]]
    )

    metadatas = results.get(
        "metadatas",
        [[]]
    )

    return {
        "documents": documents[0] if documents else [],
        "metadatas": metadatas[0] if metadatas else []
    }

def get_context(
    self,
    query,
    top_k=5,
    max_characters=14000
):
    results = self.search(
        query,
        top_k
    )

    documents = results["documents"]

    context_parts = []

    for document in documents:
        if document:
            context_parts.append(
                document.strip()
            )

    context = "\n\n".join(
        context_parts
    )

    return (
        context[:max_characters],
        results["metadatas"]
    )

def count(self):
    return self.collection.count()