import time
import subprocess
import sys
from feedback_logger import get_feedback_count

def run_retraining():
    """Run the retraining script."""
    try:
        subprocess.run([sys.executable, "retrain_jarvis.py"], check=True)
        print("Retraining completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Retraining failed: {e}")

def main():
    """Scheduler for continuous learning."""
    feedback_threshold = 5  # Retrain after 5 corrections
    check_interval = 86400  # Check daily (in seconds)

    print("Continuous learning scheduler started.")
    print(f"Will retrain when feedback count reaches {feedback_threshold} or daily check.")

    while True:
        feedback_count = get_feedback_count()
        print(f"Current feedback count: {feedback_count}")

        if feedback_count >= feedback_threshold:
            print("Threshold reached. Starting retraining...")
            run_retraining()
        else:
            print("Threshold not reached. Waiting...")

        time.sleep(check_interval)

if __name__ == "__main__":
    main()