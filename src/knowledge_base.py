import re
from pathlib import Path
import chromadb
from src.config import settings


# Lazy-loaded singleton for the encoder — avoids slow startup
_encoder = None


def _get_encoder():
    global _encoder
    if _encoder is None:
        from sentence_transformers import SentenceTransformer
        _encoder = SentenceTransformer(settings.embedding_model)
    return _encoder


class FAQKnowledgeBase:
    def __init__(self, lazy_encoder: bool = True):
        persist_dir = Path("data/chroma_db")
        persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=settings.kb_collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        if not lazy_encoder:
            self.encoder = _get_encoder()
        else:
            self.encoder = None

    def _ensure_encoder(self):
        if self.encoder is None:
            self.encoder = _get_encoder()

    def add_documents(self, chunks: list[str], metadatas: list[dict] | None = None):
        """Add document chunks to the vector store in batch"""
        self._ensure_encoder()
        ids = [f"doc_{i}" for i in range(len(chunks))]
        embeddings = self.encoder.encode(chunks).tolist()
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas or [{}] * len(chunks),
            ids=ids
        )

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Hybrid search: semantic embedding + keyword matching, merge results."""
        # 1. Semantic search
        semantic_results = self._semantic_search(query, top_k)

        # 2. Keyword search (ChromaDB where_document contains)
        keyword_results = self._keyword_search(query, top_k)

        # 3. Merge and deduplicate
        return self._merge_results(semantic_results, keyword_results, top_k)

    def _semantic_search(self, query: str, top_k: int) -> list[dict]:
        """Vector similarity search."""
        self._ensure_encoder()
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
                "score": results["distances"][0][i] if results.get("distances") else 0,
                "source": "semantic"
            })
        return docs

    def _keyword_search(self, query: str, top_k: int) -> list[dict]:
        """Keyword-based search using ChromaDB where_document contains."""
        # Extract meaningful keywords (Chinese chars, 2+ chars)
        keywords = re.findall(r'[\u4e00-\u9fff]{2,}', query)
        if not keywords:
            # Fallback: split by spaces/punctuation
            keywords = [w.strip() for w in re.split(r'[\s,，。？！?!.]+', query) if len(w.strip()) >= 2]

        if not keywords:
            return []

        results = []
        seen_contents = set()

        for kw in keywords[:3]:  # limit to top 3 keywords to avoid too many queries
            try:
                res = self.collection.get(
                    where_document={"$contains": kw},
                    include=["documents", "metadatas"]
                )
                if res and res["documents"]:
                    for j, doc in enumerate(res["documents"]):
                        if doc not in seen_contents:
                            seen_contents.add(doc)
                            meta = res["metadatas"][j] if res.get("metadatas") else {}
                            results.append({
                                "content": doc,
                                "metadata": meta,
                                "score": 0.5,  # fixed score for keyword match
                                "source": "keyword"
                            })
            except Exception:
                continue

        return results[:top_k]

    def _merge_results(self, semantic: list[dict], keyword: list[dict], top_k: int) -> list[dict]:
        """Merge semantic and keyword results, deduplicate, sort by score."""
        seen = set()
        merged = []

        # Semantic results first (higher priority)
        for r in semantic:
            key = r["content"][:100]  # use first 100 chars as dedup key
            if key not in seen:
                seen.add(key)
                merged.append(r)

        # Then keyword results
        for r in keyword:
            key = r["content"][:100]
            if key not in seen:
                seen.add(key)
                # Boost keyword results that also appear in semantic
                r["score"] = r["score"] * 0.8  # slightly lower priority
                merged.append(r)

        # Sort by score (lower is better in ChromaDB cosine distance)
        merged.sort(key=lambda x: x.get("score", 1.0))
        return merged[:top_k]

    def format_context(self, results: list[dict]) -> str:
        """Format search results into LLM-usable context"""
        sections = []
        for i, r in enumerate(results, 1):
            source = r["metadata"].get("source", "knowledge_base")
            method = r.get("source", "")
            tag = f"[参考 {i} - 来源: {source}"
            if method:
                tag += f" | 匹配: {method}"
            tag += "]"
            sections.append(f"{tag}\n{r['content']}")
        return "\n\n".join(sections)
