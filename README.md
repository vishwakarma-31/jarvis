# Jarvis

## Project Overview

Jarvis is an advanced AI-powered personal assistant system designed to provide seamless, voice-activated assistance. Built with Python and leveraging modern AI technologies, Jarvis follows an agentic loop (Perceive, Plan, Act, Learn) to process user commands, execute tasks securely, and continuously improve through feedback. It integrates local large language models (via Ollama with the phi3:3.8b model), voice recognition using Vosk and Whisper, memory management with ChromaDB, desktop automation via PyAutoGUI, system monitoring, hotkey listening, and security mediation. The system supports both local execution and containerized deployment in a Docker sandbox for enhanced safety. Key goals include proactive monitoring, biometric speaker verification, and fine-tuning capabilities using LoRA adapters for personalized learning.

## Features

- **Voice Recognition and Speaker Verification**: Detects the wake word "Jarvis" using the Vosk speech recognition model. Transcribes commands with OpenAI's Whisper model. Includes biometric verification using MFCC features and cosine similarity threshold (0.7) for authorized access only.

- **Agentic Loop**: Implements the ReAct (Reasoning and Acting) pattern with LangChain. Perceive processes voice input, Plan decomposes goals using the LLM, Act executes secure tools, and Learn logs feedback for improvement.

- **Desktop Automation**: Tools for controlling mouse, keyboard, taking screenshots, and interacting with the desktop environment using PyAutoGUI and pynput.

- **System Monitoring**: Proactive monitoring of CPU, memory, and other system resources with alerts delivered via text-to-speech.

- **Memory Management**: Stores conversation history and knowledge in a ChromaDB vector database for retrieval-augmented generation.

- **Hotkey Listening**: Global hotkey detection to trigger Jarvis actions without voice input.

- **Security Mediation**: All tool executions are wrapped with a security mediator to enforce permissions and prevent unauthorized actions.

- **Continuous Learning**: Collects user feedback for fine-tuning the language model using LoRA adapters. Includes scripts for dataset generation and periodic retraining.

- **Text-to-Speech Output**: Synthesizes responses using pyttsx3 for natural audio feedback.

## Installation

### Prerequisites
- Python 3.9 or higher
- Microphone and speakers for voice interaction
- Docker Desktop (for containerized setup)
- Git (to clone the repository if needed)

### Local Installation
1. Navigate to the project directory: `cd d:/Projects/jarvis`
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Download and extract the Vosk model: Unzip `vosk-model-small-en-us-0.15` into the `models/` directory.
6. Install Ollama (download from ollama.com) and pull the model: `ollama pull phi3:3.8b`
7. Enroll your voice for biometric verification: Run the enrollment function in `src/voice.py` (records 3 samples).
8. (Optional) Install additional system dependencies if needed (e.g., for audio: portaudio via package manager).

### Docker Installation
1. Ensure Docker Desktop is installed and running.
2. Build the Docker image: `docker build -t jarvis-agent .`
3. The image includes all dependencies, Vosk model, and Ollama with phi3:3.8b pre-pulled.
4. For volumes, mount user directories as read-only (see Usage for example).

## Usage

### Local Execution
- Run the agent: `python src/agent.py`
  - This starts proactive monitoring and enters the agentic loop.
  - Speak "Jarvis" followed by a command (e.g., "Jarvis, open Notepad" or "Jarvis, check CPU usage").
  - Jarvis will respond via text-to-speech and log feedback if corrections are provided.
- Configure hotkeys: Edit `src/hotkey_listener.py` to set custom triggers (e.g., Ctrl+J to activate).
- Test components individually:
  - Voice: `python src/voice.py` (for enrollment or testing transcription).
  - Tests: `python -m pytest src/`

### Docker Execution
- Use the provided batch script: Double-click `run_jarvis.bat` (builds the image if needed and runs the container).
- Manual command:
  ```
  docker run --rm \
    --name jarvis-container \
    --network none \
    --cpus 0.5 \
    --memory 512m \
    --read-only \
    --tmpfs /tmp \
    -v "C:/Users/Aryan/Documents:/app/user_docs:ro" \
    -v "C:/Users/Aryan/Downloads:/app/user_downloads:ro" \
    jarvis-agent
  ```
  - This runs Jarvis in a secure sandbox with no network access, resource limits, and read-only filesystem.
  - Note: Desktop automation may require additional X11 forwarding for GUI access in container (see docker-setup.md for improvements).
- Interact via voice as in local mode; the container executes `python src/agent.py`.

### Examples
- Voice command: "Jarvis, take a screenshot" → Uses desktop automation tool.
- Feedback: After a response, say "Jarvis, that was wrong. The correct answer is [correction]" within 3 seconds.
- Monitoring: Jarvis proactively speaks alerts like "High CPU usage detected."

## Architecture/Components

Jarvis follows a modular architecture with the following key components:

- **Core Agent (`src/agent.py`)**: LangChain ReAct agent using OllamaLLM (phi3:3.8b). Integrates tools with security wrappers. Handles the agentic loop: perceive → plan → act → learn.

- **Voice Processing (`src/voice.py`)**: Records audio with PyAudio, applies VAD (WebRTC), detects wake word with Vosk, transcribes with Whisper, verifies speaker with MFCC biometrics, and synthesizes speech with pyttsx3.

- **Memory (`src/memory.py`)**: ChromaDB-based vector store for persisting interactions and enabling retrieval.

- **Security Mediator (`src/security_mediator.py`)**: Wraps all tools to mediate execution, enforcing policies.

- **System Monitor (`src/system_monitor.py`)**: Tracks system resources (psutil) and triggers proactive callbacks.

- **Desktop Automation (`src/desktop_automation.py`)**: Defines tools for GUI interactions using PyAutoGUI.

- **Feedback Logger (`src/feedback_logger.py`)**: Logs user corrections for learning.

- **Hotkey Listener (`src/hotkey_listener.py`)**: Listens for keyboard shortcuts with pynput.

**Data Flow**: Voice input → Transcription & Verification → Agent Loop (LLM Planning) → Secure Tool Execution/Memory Query → TTS Response → Feedback Loop.

For detailed diagrams, refer to CONTINUOUS_LEARNING.md and SECURITY_MEDIATOR.md.

## Continuous Learning/Fine-tuning

Jarvis supports ongoing improvement through feedback-driven fine-tuning:

- **Feedback Collection**: During the agent loop, corrections are captured via voice and logged using `feedback_logger.py`.

- **Dataset Generation**: Use `jarvis_finetune_dataset.jsonl` as a base; append feedback to build training data.

- **Fine-tuning Script (`finetune_jarvis.py`)**: Trains LoRA adapters on the base model using datasets in `jarvis_lora/`. Runs training with Hugging Face Transformers.

- **Retraining (`retrain_jarvis.py`)**: Applies fine-tuned adapters to the Ollama model.

- **Scheduler (`continuous_learning_scheduler.py`)**: Periodically triggers retraining based on accumulated feedback.

- **Process**:
  1. Collect feedback from interactions.
  2. Update dataset.
  3. Run `python finetune_jarvis.py` to train LoRA.
  4. Integrate via retrain script.

- Training runs are stored in `jarvis_lora/runs/` with TensorBoard events.

See CONTINUOUS_LEARNING.md for advanced configurations.

## Security

- **Speaker Verification**: Biometric checks prevent unauthorized access (voiceprint stored in `data/voiceprint.pkl`).

- **Tool Mediation**: All actions pass through `security_mediator.py` for permission validation.

- **Sandboxing**: Docker deployment enforces:
  - No network access (`--network none`).
  - Resource limits (0.5 CPU, 512MB RAM).
  - Read-only filesystem with tmpfs for temp files.
  - Read-only mounts for user data.

- Additional safeguards: Proactive monitoring for anomalies, feedback logging for auditing.

- Refer to SECURITY_MEDIATOR.md for mediator policies and docker-setup.md for container details.

## Contributing

Contributions are welcome! To get started:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/amazing-feature`.
3. Commit changes: `git commit -m 'Add amazing feature'`.
4. Push to the branch: `git push origin feature/amazing-feature`.
5. Open a Pull Request.

Please run tests before submitting: `python -m pytest src/`. Ensure code follows PEP 8 standards. For major changes, open an issue first to discuss.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.