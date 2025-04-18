import json
import datetime
from pathlib import Path

memory_path = Path(__file__).parent
memory_file = memory_path / "sov_memory.jsonl"

memory_file.touch(exist_ok=True)

def save_event(event: dict):
    timestamp = datetime.datetime.utcnow().isoformat()
    event_record = {"timestamp": timestamp, **event}
    with memory_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event_record) + "\n")

def load_events() -> list:
    with memory_file.open("r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]

def summarize_memory(n=5) -> str:
    events = load_events()[-n:]
    return "\n".join(
        f"{e['timestamp']}: {e.get('tag', 'Unknown')} — {e.get('content', '')}"
        for e in events
    ) or "No memory entries found."
