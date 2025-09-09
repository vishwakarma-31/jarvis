import json
import os
from datetime import datetime
from typing import Dict, List, Optional

FEEDBACK_FILE = "feedback_data.jsonl"

def log_feedback(original_instruction: str, agent_response: str, correction: str, context: Optional[str] = None) -> None:
    """
    Log user feedback/correction for continuous learning.

    Args:
        original_instruction: The original user instruction
        agent_response: The agent's incorrect response
        correction: The correct response provided by user
        context: Additional context if available
    """
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "original_instruction": original_instruction,
        "agent_response": agent_response,
        "correction": correction,
        "context": context
    }

    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(feedback_entry) + "\n")

    print(f"Feedback logged: {correction}")

def load_feedback() -> List[Dict]:
    """
    Load all accumulated feedback data.

    Returns:
        List of feedback entries
    """
    if not os.path.exists(FEEDBACK_FILE):
        return []

    feedback_data = []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                feedback_data.append(json.loads(line.strip()))
    return feedback_data

def get_feedback_count() -> int:
    """
    Get the number of feedback entries.

    Returns:
        Number of feedback entries
    """
    return len(load_feedback())

def clear_feedback() -> None:
    """
    Clear all feedback data (use after retraining).
    """
    if os.path.exists(FEEDBACK_FILE):
        os.remove(FEEDBACK_FILE)
        print("Feedback data cleared.")