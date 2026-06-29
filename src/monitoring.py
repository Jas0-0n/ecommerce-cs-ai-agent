# src/monitoring.py
import json
import logging
from datetime import datetime
from pathlib import Path


class AgentMonitor:
    """簡單的 Agent 日誌系統"""

    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s"
        )
        self.logger = logging.getLogger("ecommerce_agent")

        # 也寫入檔案
        fh = logging.FileHandler(self.log_dir / "agent.log", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        self.logger.addHandler(fh)

    def log_interaction(self, user_input: str, result: dict, duration_ms: int):
        record = {
            "timestamp": datetime.now().isoformat(),
            "input": user_input[:200],
            "route": result.get("route"),
            "duration_ms": duration_ms,
            "escalated": result.get("type") == "escalate" if result.get("route") == "complaint" else False,
            "has_response": bool(result.get("response"))
        }
        self.logger.info(json.dumps(record, ensure_ascii=False))

    def print_stats(self):
        """輸出統計摘要"""
        log_file = self.log_dir / "agent.log"
        if not log_file.exists():
            print("尚無資料")
            return

        total = 0
        routes = {}
        escalations = 0
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if "| INFO |" not in line:
                    continue
                try:
                    data = json.loads(line.split("| INFO |")[1])
                    total += 1
                    route = data.get("route", "unknown")
                    routes[route] = routes.get(route, 0) + 1
                    if data.get("escalated"):
                        escalations += 1
                except Exception:
                    pass

        print(f"\n📊 客服 Agent 統計")
        print(f"總處理次數: {total}")
        for r, c in routes.items():
            print(f"  - {r}: {c}次 ({c/total*100:.0f}%)")
        if total:
            print(f"升級人工: {escalations}次 ({escalations/total*100:.0f}%)")
