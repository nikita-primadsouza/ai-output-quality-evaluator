import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path("data/evaluation_history.json")


def load_history() -> list:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_record(record: dict) -> None:
    history = load_history()
    history.append(record)
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def build_record(prompt: str, result: dict, human_decision: str, notes: str) -> dict:
    return {
        "Date/Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Prompt": prompt[:80],
        "Overall Score": result["overall_score"],
        "AI Recommendation": result["decision"],
        "Human Decision": human_decision,
        "Hallucination Risk": result["hallucination_risk"],
        "Reviewer Notes": notes,
    }


def summary_metrics(history: list) -> dict:
    total = len(history)
    scores = [row["Overall Score"] for row in history]
    decisions = [row["AI Recommendation"] for row in history]
    return {
        "Total Evaluations": total,
        "Average Score": round(sum(scores) / total, 1),
        "Pass Rate": f"{decisions.count('PASS') / total:.0%}",
        "Human Review Rate": f"{decisions.count('HUMAN REVIEW') / total:.0%}",
        "Failure Rate": f"{decisions.count('FAIL') / total:.0%}",
    }