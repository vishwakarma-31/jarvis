# Jarvis Docker Containerized Sandbox Setup

## Overview
This document outlines the Docker containerization of the Jarvis AI agent with strict security policies for sandboxed execution.

## Docker Installation
- Docker Desktop was installed on the Windows 11 system using `winget install Docker.DockerDesktop`.
- Ensure Docker Desktop is running before building or running containers.

## Dockerfile Configuration
The `Dockerfile` is based on Python 3.9-slim and includes:
- System dependencies: portaudio, alsa, ffmpeg, espeak-ng for audio processing.
- Ollama installation for local LLM support.
- Python dependencies: langchain, vosk, whisper, chromadb, pyautogui, etc.
- Project files copied: src/, models/, data/, config/.
- Ollama model `phi3:3.8b` pre-pulled during build.
- CMD runs the agent with `python src/agent.py`.

## Container Policies
The container is configured with strict isolation policies:
- **Network**: `--network none` - No external network access.
- **CPU Limit**: `--cpus 0.5` - Limited to 50% of one CPU core.
- **Memory Limit**: `--memory 512m` - Limited to 512 MB RAM.
- **Filesystem**: `--read-only` with `--tmpfs /tmp` - Read-only root filesystem, writable temp directory.
- **Volumes**: Read-only mounts for user directories:
  - `C:/Users/Aryan/Documents:/app/user_docs:ro`
  - `C:/Users/Aryan/Downloads:/app/user_downloads:ro`

## Running the Container
Use `run_jarvis.bat` to build and run the container with policies:
```
docker build -t jarvis-agent .
docker run --rm --name jarvis-container --network none --cpus 0.5 --memory 512m --read-only --tmpfs /tmp -v "C:/Users/Aryan/Documents:/app/user_docs:ro" -v "C:/Users/Aryan/Downloads:/app/user_downloads:ro" jarvis-agent
```

## Testing Results
- Docker installation: Successful.
- Image build: Pending user confirmation (Docker PATH may require terminal restart).
- Container run: To be tested with policies applied.
- Agent execution: Expected to run in sandbox with limited resources and no network access.

## Security Considerations
- The sandbox prevents accidental damage by isolating the agent.
- Network isolation blocks unauthorized access.
- Resource limits prevent exhaustion.
- Read-only filesystem with specific writable paths enhances security.
- Note: Desktop automation tools may not function in container without X11 forwarding.

## Future Improvements
- Implement X11 forwarding for GUI tools if needed.
- Add logging and monitoring for container activity.
- Consider using Docker Compose for easier management.