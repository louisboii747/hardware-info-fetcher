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

def swap_memory():
    lines = ["=== Swap Memory ==="]
    swap = psutil.swap_memory()
    return f"Swap: {round(swap.total / (1024**3), 2)} GB, Used: {round(swap.used / (1024**3), 2)} GB ({swap.percent}%)"

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
    lines = ["=== System Information ==="]
    try:
        uptime_seconds = time.time() - psutil.boot_time()
        info = [
            f"OS/Kernel Version: {platform.system()} {platform.release()}",
            f"Architecture: {platform.machine()}",
            f"CPU Cores: {psutil.cpu_count(logical=False)}",
            f"Threads: {psutil.cpu_count(logical=True)}",
            f"Memory: {round(psutil.virtual_memory().total / (1024**3), 2)} GB",
            f"Disk: {round(psutil.disk_usage('/').total / (1024**3), 2)} GB",
            f"Uptime: {uptime_seconds / 3600:.2f} hours",
            f"User: {os.getlogin()}",
        ]

        io = psutil.disk_io_counters()
        if io:
            info.append(
                f"Disk Activity: {io.read_bytes / (1024**2):.2f} MB read, "
                f"{io.write_bytes / (1024**2):.2f} MB written"
            )

        bat = battery_info()
        info.append(f"Battery: {bat if bat else 'N/A'}")

        return info

    except Exception as e:
        return [f"System info error: {e}"]

def cpu_mem_bar():
    lines = ["=== CPU and Memory Usage ==="]
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




def motherboard_info():
    if platform.system() == "Windows":
        lines = ["=== Motherboard Information ==="]
        base_path = "/sys/devices/virtual/dmi/id/"
        info = {
            "Manufacturer": read_sys(base_path + "board_vendor"),
            "Product Name": read_sys(base_path + "board_name"),
            "Version": read_sys(base_path + "board_version"),
            "Serial Number": read_sys(base_path + "board_serial"),
        }
        return [f"{key}: {value if value else 'N/A'}" for key, value in info.items()]
    return ["Motherboard info not available on this OS."]



def drive_info():
    lines = ["=== Drive Information ==="]
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (PermissionError, FileNotFoundError):
            continue

        lines.append(
            f"{part.mountpoint:15} "
            f"{usage.used // (1024**3):4} / "
            f"{usage.total // (1024**3):4} GB "
            f"({usage.percent:5.1f}%)"
        )

    return lines

## Print Lines ##
def main():
    try:
        while True:
            clear_screen()
            # System info
            for line in system_info():
                print(line)
            # Swap memory
            for line in [swap_memory()]:
                print(line)
            # Network
            for line in network_info():
                print(line)
            # Top processes
            for line in top_processes():
                print(line)
            # Drive info
            for line in drive_info():
                print(line)
            # CPU and Memory bar
            for line in [cpu_mem_bar()]:
                print(line)
            # Motherboard Info
            for line in motherboard_info():
                print(line)
            print("\nPress Ctrl+C to exit...")
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nExiting...")

import tkinter as tk

def gui_app():
    root = tk.Tk()
    root.title("System Monitor")
    root.geometry("800x600")

    text = tk.Text(
        root,
        font=("monospace", 10),
        bg="#111",
        fg="#0f0",
        insertbackground="white"
    )
    text.pack(fill="both", expand=True)

    def update():
        scroll = text.yview()
        
        text.delete("1.0", tk.END)

        for line in system_info():
            text.insert(tk.END, line + "\n")

        text.insert(tk.END, swap_memory() + "\n\n")

        for line in network_info():
            text.insert(tk.END, line + "\n")

        text.insert(tk.END, "\n")

        for line in top_processes():
            text.insert(tk.END, line + "\n")

        text.insert(tk.END, "\n")

        for line in cpu_mem_bar().split("\n"):
            text.insert(tk.END, line + "\n")

        for line in drive_info():
            text.insert(tk.END, line + "\n")
        
        
        for line in motherboard_info():
            text.insert(tk.END, line + "\n")

        text.yview_moveto(scroll[0])

        root.after(1000, update)

    update()
    root.mainloop()


if __name__ == "__main__":
    gui_app()
