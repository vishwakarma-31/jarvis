# Use Python 3.9 base image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    libasound2-dev \
    libevdev-dev \
    python3-dev \
    libsndfile1-dev \
    ffmpeg \
    espeak-ng \
    curl \
    build-essential \
    libopenblas-dev \
    libblas-dev \
    liblapack-dev \
    pkg-config \
    x11-utils \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy project files
COPY src/ ./src/
COPY models/ ./models/
COPY data/ ./data/
COPY config/ ./config/
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pull the Ollama model
RUN ollama serve & sleep 5 && ollama pull phi3:3.8b && pkill ollama

# Expose port if needed (Ollama uses 11434)
EXPOSE 11434

# Set environment variables
ENV PYTHONPATH=/app

# Run the agent
CMD ["python", "src/agent.py"]