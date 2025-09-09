from pynput import keyboard
from voice import process_voice_input
from agent import run_agentic_loop

def on_activate():
    print("Hotkey activated: Ctrl+Alt+J")
    # Trigger voice input and run agent loop
    transcription = process_voice_input()
    if transcription:
        result = run_agentic_loop()
        print(f"Agent result: {result}")

# Set up hotkey
hotkey = keyboard.HotKey(
    keyboard.HotKey.parse('<ctrl>+<alt>+j'),
    on_activate
)

def for_canonical(f):
    return lambda k: f(l.canonical(k))

l = keyboard.Listener(
    on_press=for_canonical(hotkey.press),
    on_release=for_canonical(hotkey.release)
)

l.start()