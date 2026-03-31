"""JSONL-based error case storage."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path


class ErrorNotebook:
    def __init__(self, base_dir: Path):
        self.cases_dir = Path(base_dir) / "cases"
        self.cases_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.cases_dir / "errors.jsonl"
        self._counter = self._count_existing()

    def _count_existing(self) -> int:
        if not self.jsonl_path.exists():
            return 0
        count = 0
        with self.jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count

    def report(
        self,
        *,
        source: str,
        error_message: str,
        error_type: str,
        input_ir: dict | None = None,
        bad_json: dict | None = None,
    ) -> str:
        self._counter += 1
        year = datetime.now(timezone.utc).year
        entry_id = f"ERR-{year}-{self._counter:04d}"
        entry = {
            "id": entry_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "input_ir": input_ir,
            "bad_json": bad_json,
            "error": {
                "type": error_type,
                "message": error_message,
            },
            "status": "pending",
            "root_cause": None,
            "fix": None,
            "rule_ref": None,
            "test_ref": None,
        }
        with self.jsonl_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return entry_id

    def get_pending(self) -> list[dict]:
        if not self.jsonl_path.exists():
            return []
        results = []
        with self.jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                if entry.get("status") == "pending":
                    results.append(entry)
        return results

    def get_stats(self) -> dict:
        if not self.jsonl_path.exists():
            return {"total": 0, "by_type": {}, "by_status": {}}
        by_type: dict[str, int] = {}
        by_status: dict[str, int] = {}
        total = 0
        with self.jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                total += 1
                etype = entry.get("error", {}).get("type", "unknown")
                by_type[etype] = by_type.get(etype, 0) + 1
                status = entry.get("status", "unknown")
                by_status[status] = by_status.get(status, 0) + 1
        return {"total": total, "by_type": by_type, "by_status": by_status}
