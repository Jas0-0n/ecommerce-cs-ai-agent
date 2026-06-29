# scripts/ingest_kb.py
"""
Split markdown files in data/knowledge/ by headings, then import into the vector database

Usage: python scripts/ingest_kb.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.knowledge_base import FAQKnowledgeBase


def split_markdown_by_heading(text: str, source: str) -> list[tuple[str, dict]]:
    """Split markdown into paragraphs by ## Q: headings"""
    chunks = []
    # Match paragraphs starting with ## Q:
    pattern = r'(## Q:.*?)(?=## Q:|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)
    for m in matches:
        m = m.strip()
        if m:
            # Extract Q as metadata
            q_match = re.search(r'## (Q:.*?)(?:\n|$)', m)
            q_text = q_match.group(1) if q_match else ""
            chunks.append((m, {"source": source, "question": q_text}))
    return chunks


def main():
    kb = FAQKnowledgeBase()
    kb_dir = Path("data/knowledge")

    all_chunks = []
    all_metadatas = []

    for md_file in sorted(kb_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        chunks = split_markdown_by_heading(text, md_file.name)
        for content, meta in chunks:
            all_chunks.append(content)
            all_metadatas.append(meta)
        print(f"  {md_file.name}: {len(chunks)} chunks")

    if all_chunks:
        kb.add_documents(all_chunks, all_metadatas)
        print(f"\n✅ Imported {len(all_chunks)} paragraphs into the vector database")
    else:
        print("⚠️  No paragraphs found")


if __name__ == "__main__":
    main()
