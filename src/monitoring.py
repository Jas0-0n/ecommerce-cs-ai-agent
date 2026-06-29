# src/monitoring.py
import json
import logging
from datetime import datetime
from pathlib import Path


class AgentMonitor:
    """Simple Agent logging system"""

    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s"
        )
        self.logger = logging.getLogger("ecommerce_agent")

        # Also write to file
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
        """Print statistical summary"""
        log_file = self.log_dir / "agent.log"
        if not log_file.exists():
            print("No data available")
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

        print(f"\n📊 Customer Service Agent Statistics")
        print(f"Total processed: {total}")
        for r, c in routes.items():
            print(f"  - {r}: {c} ({c/total*100:.0f}%)")
        if total:
            print(f"Escalations to human: {escalations} ({escalations/total*100:.0f}%)")
