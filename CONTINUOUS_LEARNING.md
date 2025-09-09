# Jarvis Continuous Learning System

This document describes the continuous learning implementation for Jarvis, enabling the AI assistant to learn from user corrections and adapt over time through a feedback-driven retraining cycle.

## Overview

The continuous learning system consists of:
1. **Feedback Logging**: Captures user corrections in real-time
2. **Structured Storage**: Stores feedback data for retraining
3. **Periodic Retraining**: Uses QLoRA to fine-tune the model with new data
4. **Automated Scheduling**: Triggers retraining based on feedback accumulation
5. **Integration**: Seamlessly integrated into the agent loop

## Components

### 1. Feedback Logger (`src/feedback_logger.py`)

- **Purpose**: Logs user corrections with context
- **Functions**:
  - `log_feedback()`: Records correction with original instruction and response
  - `load_feedback()`: Retrieves all stored feedback
  - `get_feedback_count()`: Returns number of feedback entries
  - `clear_feedback()`: Removes all feedback after retraining

**Storage Format** (JSONL):
```json
{
  "timestamp": "2025-09-06T17:54:54.658Z",
  "original_instruction": "Jarvis, what's the weather?",
  "agent_response": "It's raining.",
  "correction": "It's sunny.",
  "context": null
}
```

### 2. Agent Integration (`src/agent.py`)

- **Modified Functions**:
  - `run_agentic_loop()`: Now includes feedback capture after response
  - `capture_feedback()`: Listens for corrections after speaking

**Flow**:
1. Agent responds to user query
2. Waits 3 seconds for potential correction
3. If correction detected (containing "that was wrong"), logs it
4. Acknowledges correction to user

### 3. Retraining Script (`retrain_jarvis.py`)

- **Purpose**: Fine-tunes the model with accumulated feedback
- **Process**:
  1. Loads existing LoRA adapters
  2. Combines original dataset with feedback data
  3. Performs incremental fine-tuning with QLoRA
  4. Saves updated LoRA adapters
  5. Clears feedback data

**Key Features**:
- Uses lower learning rate for incremental learning
- Fewer epochs to avoid catastrophic forgetting
- Tests updated model with sample prompts

### 4. Scheduler (`continuous_learning_scheduler.py`)

- **Purpose**: Automates retraining based on conditions
- **Triggers**:
  - Feedback count reaches threshold (5 corrections)
  - Daily check (can be modified)

**Usage**:
```bash
python continuous_learning_scheduler.py
```

## Usage Instructions

### For Users

1. **Providing Corrections**:
   - After Jarvis responds, say: "Jarvis, that was wrong. The correct answer is [correction]."
   - Jarvis will acknowledge and log the correction

2. **Monitoring Learning**:
   - Feedback is stored in `feedback_data.jsonl`
   - Retraining occurs automatically when threshold is met

### For Developers

1. **Running Tests**:
   ```bash
   python src/test_continuous_learning.py
   ```

2. **Manual Retraining**:
   ```bash
   python retrain_jarvis.py
   ```

3. **Starting Scheduler**:
   ```bash
   python continuous_learning_scheduler.py &
   ```

## Technical Details

### Model Fine-tuning

- **Base Model**: Microsoft Phi-2
- **Technique**: LoRA (Low-Rank Adaptation)
- **Quantization**: QLoRA for memory efficiency
- **Hardware**: CPU-based training (low VRAM)

### Data Format

- **Original Dataset**: `jarvis_finetune_dataset.jsonl`
- **Feedback Format**: Converted to instruction-response pairs
- **Combined Training**: Original + feedback data

### Scheduling

- **Threshold-based**: Retrains after N corrections
- **Time-based**: Daily checks
- **Background Process**: Runs continuously

## Testing

The system includes comprehensive tests in `src/test_continuous_learning.py`:

- Feedback logging functionality
- Data persistence
- Clearing mechanism
- Retraining simulation

Run tests with:
```bash
python src/test_continuous_learning.py
```

## Future Enhancements

1. **Real-time Transcription**: Replace dummy transcription with actual STT
2. **Advanced Scheduling**: Weekly retraining, user preference-based
3. **Feedback Quality**: Validate corrections before logging
4. **Model Evaluation**: Automated testing of improved performance
5. **Backup/Restore**: Version control for LoRA adapters

## Troubleshooting

- **No Feedback Logged**: Check microphone permissions and STT integration
- **Retraining Fails**: Ensure sufficient disk space and model files
- **Scheduler Not Running**: Check Python path and background process status
- **Model Not Improving**: Adjust learning rate or increase feedback threshold

## Security Considerations

- Feedback data is stored locally
- No external data transmission
- Corrections are validated for format
- Model updates are incremental and reversible