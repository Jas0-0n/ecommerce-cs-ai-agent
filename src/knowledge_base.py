# src/knowledge_base.py
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from src.config import settings


class FAQKnowledgeBase:
    def __init__(self):
        self.encoder = SentenceTransformer(settings.embedding_model)
        persist_dir = Path("data/chroma_db")
        persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=settings.kb_collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, chunks: list[str], metadatas: list[dict] | None = None):
        """Add document chunks to the vector store in batch"""
        ids = [f"doc_{i}" for i in range(len(chunks))]
        embeddings = self.encoder.encode(chunks).tolist()
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas or [{}] * len(chunks),
            ids=ids
        )

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Search for the most relevant FAQ paragraphs"""
        query_embedding = self.encoder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        docs = []
        for i in range(len(results["documents"][0])):
            docs.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": results["distances"][0][i] if results.get("distances") else 0
            })
        return docs

    def format_context(self, results: list[dict]) -> str:
        """Format search results into LLM-usable context"""
        sections = []
        for i, r in enumerate(results, 1):
            source = r["metadata"].get("source", "knowledge_base")
            sections.append(f"[Reference {i} - Source: {source}]\n{r['content']}")
        return "\n\n".join(sections)
