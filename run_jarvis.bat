@echo off
REM Build the Docker image
docker build -t jarvis-agent .

REM Run the container with strict policies
docker run --rm ^
  --name jarvis-container ^
  --network none ^
  --cpus 0.5 ^
  --memory 512m ^
  --read-only ^
  --tmpfs /tmp ^
  -v "C:/Users/Aryan/Documents:/app/user_docs:ro" ^
  -v "C:/Users/Aryan/Downloads:/app/user_downloads:ro" ^
  jarvis-agent