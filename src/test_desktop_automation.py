import time
from desktop_automation import MouseMoveTool, MouseClickTool, KeyboardTypeTool, KeyboardPressTool, ScreenshotTool, LocateImageTool, CheckUserActivityTool, RequestPermissionTool

def test_mouse_move():
    tool = MouseMoveTool()
    result = tool._run("100,200")
    print("Mouse Move:", result)

def test_mouse_click():
    tool = MouseClickTool()
    result = tool._run("left")
    print("Mouse Click:", result)

def test_keyboard_type():
    tool = KeyboardTypeTool()
    result = tool._run("Hello World")
    print("Keyboard Type:", result)

def test_keyboard_press():
    tool = KeyboardPressTool()
    result = tool._run("ctrl c")
    print("Keyboard Press:", result)

def test_screenshot():
    tool = ScreenshotTool()
    result = tool._run("test_screenshot.png")
    print("Screenshot:", result)

def test_locate_image():
    tool = LocateImageTool()
    result = tool._run("test_screenshot.png")  # Assuming we have the screenshot
    print("Locate Image:", result)

def test_check_activity():
    tool = CheckUserActivityTool()
    result = tool._run("10")  # 10 seconds
    print("Check Activity:", result)

def test_request_permission():
    tool = RequestPermissionTool()
    result = tool._run("")
    print("Request Permission:", result)

if __name__ == "__main__":
    print("Testing Desktop Automation Tools...")
    test_mouse_move()
    time.sleep(1)
    test_mouse_click()
    time.sleep(1)
    test_keyboard_type()
    time.sleep(1)
    test_keyboard_press()
    time.sleep(1)
    test_screenshot()
    time.sleep(1)
    test_locate_image()
    time.sleep(1)
    test_check_activity()
    time.sleep(1)
    # test_request_permission()  # Skip for now as it requires voice
    print("Testing completed.")