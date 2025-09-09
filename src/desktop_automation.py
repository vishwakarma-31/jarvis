import pyautogui
from langchain.tools import BaseTool
from typing import Any
import time
import threading
from pynput import mouse, keyboard
from voice import speak, process_voice_input

# Disable PyAutoGUI failsafe for automation
pyautogui.FAILSAFE = False

class MouseMoveTool(BaseTool):
    name: str = "mouse_move"
    description: str = "Move the mouse cursor to specified coordinates (x, y). Input: 'x,y' e.g., '100,200'"

    def _run(self, query: str) -> str:
        try:
            x, y = map(int, query.split(','))
            pyautogui.moveTo(x, y)
            return f"Mouse moved to ({x}, {y})"
        except ValueError:
            return "Invalid input. Use format: x,y"

    async def _arun(self, query: str) -> str:
        return self._run(query)

class MouseClickTool(BaseTool):
    name: str = "mouse_click"
    description: str = "Click the mouse at current position or specified coordinates. Input: 'left' or 'x,y' for position"

    def _run(self, query: str) -> str:
        if ',' in query:
            x, y = map(int, query.split(','))
            pyautogui.click(x, y)
            return f"Clicked at ({x}, {y})"
        elif query.lower() == 'left':
            pyautogui.click()
            return "Left clicked at current position"
        else:
            return "Invalid input. Use 'left' or 'x,y'"

    async def _arun(self, query: str) -> str:
        return self._run(query)

class KeyboardTypeTool(BaseTool):
    name: str = "keyboard_type"
    description: str = "Type the specified text. Input: text to type"

    def _run(self, query: str) -> str:
        pyautogui.typewrite(query)
        return f"Typed: {query}"

    async def _arun(self, query: str) -> str:
        return self._run(query)

class KeyboardPressTool(BaseTool):
    name: str = "keyboard_press"
    description: str = "Press specified keys. Input: key names separated by space, e.g., 'ctrl c'"

    def _run(self, query: str) -> str:
        keys = query.split()
        pyautogui.hotkey(*keys)
        return f"Pressed keys: {keys}"

    async def _arun(self, query: str) -> str:
        return self._run(query)

class ScreenshotTool(BaseTool):
    name: str = "take_screenshot"
    description: str = "Take a screenshot of the screen. Input: filename to save (optional, defaults to screenshot.png)"

    def _run(self, query: str) -> str:
        filename = query if query else "screenshot.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"Screenshot saved as {filename}"

    async def _arun(self, query: str) -> str:
        return self._run(query)

class LocateImageTool(BaseTool):
    name: str = "locate_image"
    description: str = "Locate an image on the screen. Input: path to image file"

    def _run(self, query: str) -> str:
        try:
            location = pyautogui.locateOnScreen(query, confidence=0.8)
            if location:
                return f"Image found at {location}"
            else:
                return "Image not found"
        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(self, query: str) -> str:
        return self._run(query)

# Focus Management
last_activity = time.time()

def on_activity():
    global last_activity
    last_activity = time.time()

mouse_listener = mouse.Listener(on_move=on_activity, on_click=on_activity)
keyboard_listener = keyboard.Listener(on_press=on_activity)

class CheckUserActivityTool(BaseTool):
    name: str = "check_user_activity"
    description: str = "Check if user has been active recently. Input: idle threshold in seconds (e.g., 60)"

    def _run(self, query: str) -> str:
        try:
            threshold = int(query)
            idle_time = time.time() - last_activity
            if idle_time > threshold:
                return f"User idle for {idle_time:.1f} seconds"
            else:
                return f"User active, last activity {idle_time:.1f} seconds ago"
        except ValueError:
            return "Invalid threshold"

    async def _arun(self, query: str) -> str:
        return self._run(query)

class RequestPermissionTool(BaseTool):
    name: str = "request_permission"
    description: str = "Request verbal permission from user before taking control. Input: any (ignored)"

    def _run(self, query: str) -> str:
        speak("Do you allow me to take control of the desktop? Say yes or no after the wake word.")
        response = process_voice_input()
        if response and 'yes' in response.lower():
            return "Permission granted"
        else:
            return "Permission denied"

    async def _arun(self, query: str) -> str:
        return self._run(query)

# List of tools
desktop_tools = [
    MouseMoveTool(),
    MouseClickTool(),
    KeyboardTypeTool(),
    KeyboardPressTool(),
    ScreenshotTool(),
    LocateImageTool(),
    CheckUserActivityTool(),
    RequestPermissionTool()
]

# Start listeners for activity tracking
mouse_listener.start()
keyboard_listener.start()