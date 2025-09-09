from system_monitor import monitoring_tools, ProactiveMonitor
import time

def test_monitoring_tools():
    print("Testing monitoring tools...")
    for tool in monitoring_tools:
        try:
            result = tool._run("")
            print(f"{tool.name}: {result}")
        except Exception as e:
            print(f"Error in {tool.name}: {e}")

def test_proactive_monitor():
    print("Testing proactive monitor...")
    def test_callback(message):
        print(f"Test Alert: {message}")

    monitor = ProactiveMonitor(callback=test_callback)
    monitor.start()
    print("Monitor started. Waiting 15 seconds for potential triggers...")
    time.sleep(15)
    monitor.stop()
    print("Monitor stopped.")

if __name__ == "__main__":
    test_monitoring_tools()
    test_proactive_monitor()
    print("Testing completed.")