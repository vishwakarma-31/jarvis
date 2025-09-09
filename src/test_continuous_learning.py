import unittest
from feedback_logger import log_feedback, load_feedback, get_feedback_count, clear_feedback
import os

class TestContinuousLearning(unittest.TestCase):

    def setUp(self):
        # Clear any existing feedback
        if os.path.exists("feedback_data.jsonl"):
            os.remove("feedback_data.jsonl")

    def test_log_feedback(self):
        log_feedback("Jarvis, what's the weather?", "It's raining.", "It's sunny.")
        self.assertEqual(get_feedback_count(), 1)
        feedback = load_feedback()
        self.assertEqual(len(feedback), 1)
        self.assertEqual(feedback[0]["correction"], "It's sunny.")

    def test_multiple_feedback(self):
        log_feedback("Test1", "Wrong1", "Correct1")
        log_feedback("Test2", "Wrong2", "Correct2")
        self.assertEqual(get_feedback_count(), 2)

    def test_clear_feedback(self):
        log_feedback("Test", "Wrong", "Correct")
        clear_feedback()
        self.assertEqual(get_feedback_count(), 0)

    def test_retraining_simulation(self):
        # Log some feedback
        log_feedback("Jarvis, open email.", "Opening browser.", "Opening email client.")
        log_feedback("Jarvis, set timer.", "Timer set for 5 min.", "Timer set for 10 min.")

        # In real test, would run retrain_jarvis.py
        # For now, just check feedback is loaded
        feedback = load_feedback()
        self.assertEqual(len(feedback), 2)

        # Simulate clearing after retraining
        clear_feedback()
        self.assertEqual(get_feedback_count(), 0)

if __name__ == "__main__":
    unittest.main()