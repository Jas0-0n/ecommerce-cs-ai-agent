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
        """批次新增文件段落到向量庫"""
        ids = [f"doc_{i}" for i in range(len(chunks))]
        embeddings = self.encoder.encode(chunks).tolist()
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas or [{}] * len(chunks),
            ids=ids
        )

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """搜尋最相關的 FAQ 段落"""
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
        """將搜尋結果格式化為 LLM 可用的 context"""
        sections = []
        for i, r in enumerate(results, 1):
            source = r["metadata"].get("source", "知識庫")
            sections.append(f"[參考 {i} - 來源: {source}]\n{r['content']}")
        return "\n\n".join(sections)
