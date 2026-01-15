import platform
import psutil
import os
import time
import shutil

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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def system_info():
    uptime_seconds = time.time() - psutil.boot_time()
    info = [
        f"OS/Kernel Version: {platform.system()} {platform.release()}",
        f"Architecture: {platform.machine()}",
        f"Processor: {platform.processor()}",
        f"CPU Cores: {psutil.cpu_count(logical=False)}",
        f"Threads: {psutil.cpu_count(logical=True)}",
        f"Memory: {round(psutil.virtual_memory().total / (1024**3), 2)} GB",
        f"Disk: {round(psutil.disk_usage('/').total / (1024**3), 2)} GB",
        f"Uptime: {uptime_seconds / 3600:.2f} hours"
    ]
    bat = battery_info()
    if bat:
        info.append(f"Battery: {bat}")
    else:
        info.append("Battery: N/A")
    return info

def cpu_mem_bar():
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory().percent
    width = shutil.get_terminal_size().columns - 20
    cpu_bar = "#" * int(cpu / 100 * width)
    mem_bar = "#" * int(mem / 100 * width)
    return f"CPU: [{cpu_bar:<{width}}] {cpu:.1f}%\nMEM: [{mem_bar:<{width}}] {mem:.1f}%"

def network_info():
    net = psutil.net_io_counters(pernic=True)
    lines = ["=== Network Interfaces ==="]
    for iface, data in net.items():
        lines.append(f"{iface:10}: Sent={data.bytes_sent / (1024**2):6.2f} MB | Recv={data.bytes_recv / (1024**2):6.2f} MB")
    return lines

def top_processes(n=5):
    procs = [(p.info["name"], p.info["cpu_percent"], p.info["memory_percent"])
             for p in psutil.process_iter(["name", "cpu_percent", "memory_percent"])]
    procs.sort(key=lambda x: (x[1], x[2]), reverse=True)
    lines = [f"=== Top {n} Processes ==="]
    for name, cpu, mem in procs[:n]:
        lines.append(f"{name[:25]:25} | CPU: {cpu:5.1f}% | MEM: {mem:5.1f}%")
    return lines

def main():
    try:
        while True:
            clear_screen()
            # System info
            for line in system_info():
                print(line)
            print("\n" + cpu_mem_bar())
            # Network
            for line in network_info():
                print(line)
            # Top processes
            for line in top_processes():
                print(line)
            print("\nPress Ctrl+C to exit...")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
