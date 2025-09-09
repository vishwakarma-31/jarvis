_tts_engine = None

def speak_pyttsx3(text):
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = pyttsx3.init()
    _tts_engine.say(text)
    _tts_engine.runAndWait()

import pyaudio
import webrtcvad
import librosa
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import vosk
import whisper
import pyttsx3
import time

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
VAD_AGGRESSIVENESS = 3
THRESHOLD = 0.7
VOICEPRINT_PATH = 'data/voiceprint.pkl'

# STT settings
VOSK_MODEL_PATH = 'models/vosk-model-small-en-us-0.15'
WHISPER_MODEL_NAME = 'base'

def record_audio(duration=5):
    """Record audio for the given duration."""
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    # Convert to numpy array
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
    return audio_data, RATE

def detect_wake_word():
    """Detect wake word 'Jarvis' using VOSK."""
    model = vosk.Model(VOSK_MODEL_PATH)
    rec = vosk.KaldiRecognizer(model, RATE, '["jarvis"]')
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Listening for wake word 'Jarvis'...")
    start_time = time.time()
    while True:
        if time.time() - start_time > 60:  # Timeout after 60 seconds
            print("Timeout: No wake word detected.")
            stream.stop_stream()
            stream.close()
            audio.terminate()
            return False
        data = stream.read(CHUNK)
        if rec.AcceptWaveform(data):
            result = rec.Result()
            if 'jarvis' in result.lower():
                print("Wake word detected!")
                stream.stop_stream()
                stream.close()
                audio.terminate()
                return True

def record_command_audio(duration=5):
    """Record audio for command after wake word."""
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
    return audio_data, RATE

def transcribe_audio(audio_data, sr):
    """Transcribe audio using Whisper."""
    model = whisper.load_model(WHISPER_MODEL_NAME)
    result = model.transcribe(audio_data, fp16=False)
    return result['text']

def apply_vad(audio_data, rate=RATE):
    """Apply VAD to detect speech segments."""
    vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
    frame_duration = 30  # ms
    frame_length = int(rate * frame_duration / 1000)
    speech_frames = []
    for i in range(0, len(audio_data) - frame_length, frame_length):
        frame = audio_data[i:i+frame_length]
        frame_int16 = (frame * 32767).astype(np.int16)
        if vad.is_speech(frame_int16.tobytes(), rate):
            speech_frames.extend(frame)
    return np.array(speech_frames)

def extract_features(audio, sr):
    """Extract MFCC features and average them."""
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    return np.mean(mfcc, axis=1)

def enroll_voice(num_samples=3):
    """Enroll voice by recording multiple samples and averaging features."""
    features_list = []
    print("Starting enrollment. Speak for 5 seconds each time.")
    count = 0
    while count < num_samples:
        print(f"Recording sample {count+1}...")
        audio, sr = record_audio(5)
        speech_audio = apply_vad(audio, sr)
        if len(speech_audio) > 0:
            features = extract_features(speech_audio, sr)
            features_list.append(features)
            count += 1
        else:
            print("No speech detected, try again.")
    if features_list:
        voiceprint = np.mean(features_list, axis=0)
        os.makedirs('data', exist_ok=True)
        with open(VOICEPRINT_PATH, 'wb') as f:
            pickle.dump(voiceprint, f)
        print("Enrollment complete.")
    else:
        print("Enrollment failed.")

def verify_speaker(audio_data, sr):
    """Verify speaker by comparing features to stored voiceprint."""
    if not os.path.exists(VOICEPRINT_PATH):
        print("No voiceprint found. Please enroll first.")
        return False
    with open(VOICEPRINT_PATH, 'rb') as f:
        voiceprint = pickle.load(f)
    speech_audio = apply_vad(audio_data, sr)
    if len(speech_audio) == 0:
        return False
    features = extract_features(speech_audio, sr)
    similarity = cosine_similarity([features], [voiceprint])[0][0]
    return similarity > THRESHOLD

def process_voice_input():
    """Process voice input: wake word, record, verify, transcribe."""
    if detect_wake_word():
        audio, sr = record_command_audio(5)
        if verify_speaker(audio, sr):
            print("Speaker verified.")
            transcription = transcribe_audio(audio, sr)
            print(f"Transcribed: {transcription}")
            return transcription
        else:
            print("Speaker not verified. Access denied.")
            return None
    else:
        print("No wake word detected.")
        return None

def test_enroll(audio, sr, num_samples=3):
    """Test enrollment with provided audio."""
    features_list = []
    count = 0
    while count < num_samples:
        speech_audio = apply_vad(audio, sr)
        if len(speech_audio) > 0:
            features = extract_features(speech_audio, sr)
            features_list.append(features)
            count += 1
        else:
            print("No speech detected in test audio.")
            break  # or continue, but since it's test, perhaps break
    if features_list:
        voiceprint = np.mean(features_list, axis=0)
        os.makedirs('data', exist_ok=True)
        with open(VOICEPRINT_PATH, 'wb') as f:
            pickle.dump(voiceprint, f)
        print("Test enrollment complete.")
    else:
        print("Test enrollment failed.")

def test_verify(audio, sr):
    """Test verification with provided audio."""
    if not os.path.exists(VOICEPRINT_PATH):
        print("No voiceprint found.")
        return False
    with open(VOICEPRINT_PATH, 'rb') as f:
        voiceprint = pickle.load(f)
    speech_audio = apply_vad(audio, sr)
    if len(speech_audio) == 0:
        return False
    features = extract_features(speech_audio, sr)
    similarity = cosine_similarity([features], [voiceprint])[0][0]
    print(f"Similarity: {similarity}")
    return similarity > THRESHOLD

def speak_pyttsx3(text):
    """Synthesize speech using pyttsx3."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def speak(text):
    """Synthesize speech using pyttsx3."""
    speak_pyttsx3(text)