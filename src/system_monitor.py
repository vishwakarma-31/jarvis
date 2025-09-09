import psutil
from langchain.tools import BaseTool
from typing import List, Any

class CPUUsageTool(BaseTool):
    name: str = "cpu_usage"
    description: str = "Get current CPU usage percentage"

    def _run(self, query: str) -> str:
        usage = psutil.cpu_percent(interval=1)
        return f"Current CPU usage: {usage}%"

    async def _arun(self, query: str) -> str:
        return self._run(query)

class MemoryUsageTool(BaseTool):
    name: str = "memory_usage"
    description: str = "Get current memory usage statistics"

    def _run(self, query: str) -> str:
        mem = psutil.virtual_memory()
        return f"Memory usage: {mem.percent}%, Total: {mem.total / (1024**3):.2f} GB, Used: {mem.used / (1024**3):.2f} GB"

    async def _arun(self, query: str) -> str:
        return self._run(query)

class DiskUsageTool(BaseTool):
    name: str = "disk_usage"
    description: str = "Get disk usage for a specified path (default: C:)"

    def _run(self, path: str = "C:") -> str:
        disk = psutil.disk_usage(path)
        return f"Disk usage for {path}: {disk.percent}%, Total: {disk.total / (1024**3):.2f} GB, Used: {disk.used / (1024**3):.2f} GB"

    async def _arun(self, path: str = "C:") -> str:
        return self._run(path)

class ListProcessesTool(BaseTool):
    name: str = "list_processes"
    description: str = "List running processes with PID and name"

    def _run(self, query: str) -> str:
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            processes.append(f"PID: {proc.info['pid']}, Name: {proc.info['name']}")
        return "\n".join(processes[:20])  # Limit to first 20 for brevity

    async def _arun(self, query: str) -> str:
        return self._run(query)

class ProcessDetailsTool(BaseTool):
    name: str = "process_details"
    description: str = "Get details of a process by PID"

    def _run(self, pid: str) -> str:
        try:
            proc = psutil.Process(int(pid))
            info = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent', 'status'])
            return f"Process details: {info}"
        except psutil.NoSuchProcess:
            return f"No process found with PID {pid}"

    async def _arun(self, pid: str) -> str:
        return self._run(pid)

class NetworkStatsTool(BaseTool):
    name: str = "network_stats"
    description: str = "Get basic network statistics"

    def _run(self, query: str) -> str:
        net = psutil.net_io_counters()
        return f"Network stats: Bytes sent: {net.bytes_sent}, Bytes received: {net.bytes_recv}"

    async def _arun(self, query: str) -> str:
        return self._run(query)

# List of all monitoring tools
monitoring_tools = [
    CPUUsageTool(),
    MemoryUsageTool(),
    DiskUsageTool(),
    ListProcessesTool(),
    ProcessDetailsTool(),
    NetworkStatsTool()
]
import psutil
from langchain.tools import BaseTool
from typing import List, Any
import threading
import time

class CPUUsageTool(BaseTool):
    name: str = "cpu_usage"
    description: str = "Get current CPU usage percentage"

    def _run(self, query: str) -> str:
        usage = psutil.cpu_percent(interval=1)
        return f"Current CPU usage: {usage}%"

    async def _arun(self, query: str) -> str:
        return self._run(query)

class MemoryUsageTool(BaseTool):
    name: str = "memory_usage"
    description: str = "Get current memory usage statistics"

    def _run(self, query: str) -> str:
        mem = psutil.virtual_memory()
        return f"Memory usage: {mem.percent}%, Total: {mem.total / (1024**3):.2f} GB, Used: {mem.used / (1024**3):.2f} GB"

    async def _arun(self, query: str) -> str:
        return self._run(query)

class DiskUsageTool(BaseTool):
    name: str = "disk_usage"
    description: str = "Get disk usage for a specified path (default: C:)"

    def _run(self, path: str = "C:") -> str:
        disk = psutil.disk_usage(path)
        return f"Disk usage for {path}: {disk.percent}%, Total: {disk.total / (1024**3):.2f} GB, Used: {disk.used / (1024**3):.2f} GB"

    async def _arun(self, path: str = "C:") -> str:
        return self._run(path)

class ListProcessesTool(BaseTool):
    name: str = "list_processes"
    description: str = "List running processes with PID and name"

    def _run(self, query: str) -> str:
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            processes.append(f"PID: {proc.info['pid']}, Name: {proc.info['name']}")
        return "\n".join(processes[:20])  # Limit to first 20 for brevity

    async def _arun(self, query: str) -> str:
        return self._run(query)

class ProcessDetailsTool(BaseTool):
    name: str = "process_details"
    description: str = "Get details of a process by PID"

    def _run(self, pid: str) -> str:
        try:
            proc = psutil.Process(int(pid))
            info = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent', 'status'])
            return f"Process details: {info}"
        except psutil.NoSuchProcess:
            return f"No process found with PID {pid}"

    async def _arun(self, pid: str) -> str:
        return self._run(pid)

class NetworkStatsTool(BaseTool):
    name: str = "network_stats"
    description: str = "Get basic network statistics"

    def _run(self, query: str) -> str:
        net = psutil.net_io_counters()
        return f"Network stats: Bytes sent: {net.bytes_sent}, Bytes received: {net.bytes_recv}"

    async def _arun(self, query: str) -> str:
        return self._run(query)

# Proactive Monitoring
class ProactiveMonitor:
    def __init__(self, callback=None):
        self.callback = callback or self.default_callback
        self.running = False
        self.thread = None

    def default_callback(self, message):
        print(f"Proactive Alert: {message}")

    def check_triggers(self):
        # CPU usage
        cpu = psutil.cpu_percent(interval=1)
        if cpu > 80:
            self.callback(f"High CPU usage detected: {cpu}%")

        # Memory usage
        mem = psutil.virtual_memory()
        if mem.percent > 90:
            self.callback(f"High memory usage detected: {mem.percent}%")

        # Disk usage
        disk = psutil.disk_usage('C:')
        if disk.percent > 90:
            self.callback(f"Low disk space detected: {disk.percent}% used")

        # Battery (if available)
        if hasattr(psutil, 'sensors_battery') and psutil.sensors_battery():
            battery = psutil.sensors_battery()
            if battery.percent < 20 and not battery.power_plugged:
                self.callback(f"Low battery detected: {battery.percent}%")

    def monitor_loop(self):
        while self.running:
            self.check_triggers()
            time.sleep(10)  # Check every 10 seconds

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.monitor_loop)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

# List of all monitoring tools
monitoring_tools = [
    CPUUsageTool(),
    MemoryUsageTool(),
    DiskUsageTool(),
    ListProcessesTool(),
    ProcessDetailsTool(),
    NetworkStatsTool()
]