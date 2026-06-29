# scripts/ingest_kb.py
"""
將 data/knowledge/ 下的 markdown 文件
按標題分割後匯入向量資料庫

用法: python scripts/ingest_kb.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.knowledge_base import FAQKnowledgeBase


def split_markdown_by_heading(text: str, source: str) -> list[tuple[str, dict]]:
    """將 markdown 按 ## Q: 標題分割成段落"""
    chunks = []
    # 匹配 ## Q: 開頭的段落
    pattern = r'(## Q:.*?)(?=## Q:|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)
    for m in matches:
        m = m.strip()
        if m:
            # 提取 Q 作為 metadata
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
        print(f"\n✅ 共匯入 {len(all_chunks)} 個段落到向量資料庫")
    else:
        print("⚠️  沒有找到任何段落")


if __name__ == "__main__":
    main()
