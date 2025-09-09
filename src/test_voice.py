import numpy as np
from voice import test_enroll, test_verify, transcribe_audio, speak

# Create dummy audio for testing
audio = np.random.randn(80000).astype(np.float32)
sr = 16000

print("Testing enrollment...")
test_enroll(audio, sr)

print("Testing verification with same audio...")
result1 = test_verify(audio, sr)
print(f"Verification result: {result1}")

print("Testing verification with different audio...")
different_audio = np.random.randn(80000).astype(np.float32)
result2 = test_verify(different_audio, sr)
print(f"Verification result: {result2}")

print("Testing transcription...")
transcription = transcribe_audio(audio, sr)
print(f"Transcription: {transcription}")

print("Testing TTS with sample text...")
sample_text = "Hello, this is a test of the text-to-speech system."
speak(sample_text)

print("Test completed.")