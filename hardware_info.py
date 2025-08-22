import platform
import psutil
import os

def system_info():
    print("=== System Information ===")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Kernel: {platform.version()}")
    print(f"Architecture: {platform.machine()}")
    print(f"CPU: {platform.processor()}")
    print(f"CPU Cores: {psutil.cpu_count(logical=False)}")
    print(f"Threads: {psutil.cpu_count(logical=True)}")
    print(f"Memory: {round(psutil.virtual_memory().total / (1024**3), 2)} GB")
    print(f"Disk: {round(psutil.disk_usage('/').total / (1024**3), 2)} GB")
    print(f"Uptime: {round(psutil.boot_time())}")

if __name__ == "__main__":
    system_info()
