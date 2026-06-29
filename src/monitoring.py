# src/monitoring.py
import json
import logging
import time
from datetime import datetime
from pathlib import Path


class AgentMonitor:
    """Simple Agent logging system — writes JSON Lines to logs/agent.log"""

    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger("ecommerce_agent")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()  # avoid duplicate handlers on re-init

        fh = logging.FileHandler(self.log_dir / "agent.log", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        self.logger.addHandler(fh)

    def log_interaction(self, user_input: str, result: dict, duration_ms: int):
        """Log a single customer interaction to agent.log"""
        # Extract useful fields from the nested result
        route = result.get("route", "unknown")
        case_id = result.get("case_id") or (
            result.get("route_info", {}).get("case_id")
        )
        escalated = result.get("type") == "escalate" if route == "complaint" else False
        reason = result.get("reason") or result.get("escalate_reason", "")
        sentiment = result.get("sentiment_score")

        record = {
            "timestamp": datetime.now().isoformat(),
            "input": user_input[:300],
            "route": route,
            "duration_ms": duration_ms,
            "escalated": escalated,
            "has_response": bool(result.get("response")),
        }
        if case_id:
            record["case_id"] = case_id
        if reason:
            record["reason"] = reason
        if sentiment is not None:
            record["sentiment_score"] = sentiment

        self.logger.info(json.dumps(record, ensure_ascii=False))

    def print_stats(self):
        """Print statistical summary from agent.log"""
        log_file = self.log_dir / "agent.log"
        if not log_file.exists():
            print("No data available")
            return

        total = 0
        routes = {}
        escalations = 0
        recent = []

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
                    recent.append(data)
                except Exception:
                    pass

        print(f"\n📊 Customer Service Agent Statistics")
        print(f"Total processed: {total}")
        for r, c in sorted(routes.items()):
            print(f"  - {r}: {c} ({c/total*100:.0f}%)")
        if total:
            print(f"Escalations to human: {escalations} ({escalations/total*100:.0f}%)")

        # Show last 5 escalations
        escalations_log = [r for r in recent if r.get("escalated")]
        if escalations_log:
            print(f"\n🔴 Last {min(5, len(escalations_log))} escalations:")
            for r in escalations_log[-5:]:
                inp = r.get("input", "")[:50]
                rid = r.get("case_id", "?")
                why = r.get("reason", "")
                print(f"  [{rid}] {inp} → {why}")


# Global singleton for easy import
monitor = AgentMonitor()
