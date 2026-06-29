# scripts/setup.py — One-click initialization
import subprocess
import sys
from pathlib import Path


def main():
    print("🔧 Initializing e-commerce CS AI Agent...")

    # 1. Install dependencies
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # 2. Create .env
    env_path = Path(".env")
    if not env_path.exists():
        env_path.write_text("LLM_API_KEY=your-api-key-here\n")
        print("⚠️  Please edit .env to enter your LLM API Key")

    # 3. Import knowledge base
    subprocess.run([sys.executable, "scripts/ingest_kb.py"])

    print("✅ Initialization complete! Run python cli.py to start testing")


if __name__ == "__main__":
    main()
