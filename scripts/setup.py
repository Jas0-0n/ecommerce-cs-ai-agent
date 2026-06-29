# scripts/setup.py — 一鍵初始化
import subprocess
import sys
from pathlib import Path


def main():
    print("🔧 初始化電商客服 AI Agent...")

    # 1. 安裝依賴
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # 2. 建立 .env
    env_path = Path(".env")
    if not env_path.exists():
        env_path.write_text("LLM_API_KEY=your-api-key-here\n")
        print("⚠️  請編輯 .env 填入你的 LLM API Key")

    # 3. 匯入知識庫
    subprocess.run([sys.executable, "scripts/ingest_kb.py"])

    print("✅ 初始化完成！執行 python cli.py 開始測試")


if __name__ == "__main__":
    main()
