import platform
import psutil
import os
import time

uptime_seconds = time.time() - psutil.boot_time()

def system_info():
    print("=== System Information ===")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Kernel: {platform.version()}")
    print(f"Architecture: {platform.machine()}")
    print(f"processor : {platform.processor()}")
    print(f"CPU Cores: {psutil.cpu_count(logical=False)}")
    print(f"Threads: {psutil.cpu_count(logical=True)}")
    print(f"Memory: {round(psutil.virtual_memory().total / (1024**3), 2)} GB")
    print(f"Disk: {round(psutil.disk_usage('/').total / (1024**3), 2)} GB")
    print(f"Uptime: {uptime_seconds / 3600:.2f} hours")

def read_sys(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return None
    
def battery_info():
    base = "/sys/class/power_supply"
    if not os.path.exists(base):
        return None

    for item in os.listdir(base):
        if item.startswith("BAT"):
            cap = read_sys(f"{base}/{item}/capacity")
            stat = read_sys(f"{base}/{item}/status")
            return f"{cap}% ({stat})"


if __name__ == "__main__":
    system_info()


