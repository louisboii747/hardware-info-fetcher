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
    lines = ["=== Battery Information ==="]
    if not hasattr(psutil, "sensors_battery"):
        return None
    bat = psutil.sensors_battery()
    if bat is None:
        return None
    percent = bat.percent
    plugged = bat.power_plugged
    secsleft = bat.secsleft
    if secsleft == psutil.POWER_TIME_UNLIMITED:
        time_str = "N/A"
    elif secsleft == psutil.POWER_TIME_UNKNOWN:
        time_str = "Unknown"
    else:
        hours, remainder = divmod(secsleft, 3600)
        minutes, _ = divmod(remainder, 60)
        time_str = f"{hours}h {minutes}m"
    return f"{percent}% {'(Charging)' if plugged else '(Discharging)'} - Time left: {time_str}"
    lines.append(f"{percent}% {'(Charging)' if plugged else '(Discharging)'} - Time left: {time_str}")
    return lines

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
    
## END System Info ##

def memory_temperature():
    lines = ["=== Memory Temperature ==="]
    temps = psutil.sensors_temperatures()
    if not temps:
        return ["===Memory temperature sensors not available"]

    for name, entries in temps.items():
        for entry in entries:
            if "memory" in entry.label.lower() or "ram" in name.lower():
                if entry.label:
                    lines.append(f"{entry.label}: {entry.current} °C")
                else:
                    lines.append(f"{name}: {entry.current} °C")

    return lines if len(lines) > 1 else ["===No Memory temperature data found==="]

def gpu_info():
    lines = ["=== GPU Information ==="]
    try:
        if platform.system() == "Linux":
            lspci_output = os.popen("lspci | grep -i 'vga\\|3d\\|2d'").read()
            gpus = lspci_output.strip().split("\n")
            if not gpus or gpus == ['']:
                return ["No GPU information found."]
            for gpu in gpus:
                lines.append(gpu)
        else:
            lines.append("GPU info not implemented for this OS.")
    except Exception as e:
        lines.append(f"GPU info error: {e}")
    return lines



def cpu_mem_bar():
    cpu = psutil.cpu_percent(interval=None)
    lines = ["=== CPU and Memory Usage ==="]
    mem = psutil.virtual_memory().percent
    width = shutil.get_terminal_size().columns - 20
    cpu_bar = "#" * int(cpu / 100 * width)
    mem_bar = "#" * int(mem / 100 * width)
    lines.append(f"CPU: [{cpu_bar:<{width}}] {cpu:.1f}%")
    lines.append(f"MEM: [{mem_bar:<{width}}] {mem:.1f}%")
    return lines


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
    if platform.system() == "Linux":
        lines = ["=== Motherboard Information ==="]
        base_path = "/sys/devices/virtual/dmi/id/"
        info = {
            "Manufacturer": read_sys(base_path + "board_vendor"),
            "Product Name": read_sys(base_path + "board_name"),
            "Version": read_sys(base_path + "board_version"),
            "Serial Number": read_sys(base_path + "board_serial"),
        
        }
    for key , value in info.items():
        lines.append(f"{key}: {value if value else 'N/A'}")

    return lines
    



def fan_info():
    lines = ["=== Fan Sensors ==="]
    hwmon_base = "/sys/class/hwmon"

    if not os.path.exists(hwmon_base):
        return ["Fan sensors not available"]

    for hw in os.listdir(hwmon_base):
        hw_path = os.path.join(hwmon_base, hw)
        name = read_sys(os.path.join(hw_path, "name")) or hw

        for file in os.listdir(hw_path):
            if file.startswith("fan") and file.endswith("_input"):
                rpm = read_sys(os.path.join(hw_path, file))
                if rpm and rpm.isdigit():
                    lines.append(f"{name} {file}: {rpm} RPM")

    return lines if len(lines) > 1 else ["==No fans detected==="]







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


def gpu_temperature():
    lines = ["=== GPU Temperature ==="]
    temps = psutil.sensors_temperatures()
    if not temps:
        return ["GPU temperature sensors not available"]

    for name, entries in temps.items():
        for entry in entries:
            if "gpu" in entry.label.lower() or "nvidia" in name.lower() or "amdgpu" in name.lower():
                if entry.label:
                    lines.append(f"{entry.label}: {entry.current} °C")
                else:
                    lines.append(f"{name}: {entry.current} °C")

    return lines if len(lines) > 1 else ["===No GPU temperature data found==="]



def cpu_temperature():
    lines = ["=== CPU Temperature ==="]
    temps = psutil.sensors_temperatures()
    if not temps:
        return ["CPU temperature sensors not available"]

    for name, entries in temps.items():
        for entry in entries:
            if entry.label:
                lines.append(f"{entry.label}: {entry.current} °C")
            else:
                lines.append(f"{name}: {entry.current} °C")

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
            # CPU Temperature
            for line in cpu_temperature():
                print(line)
            # Fan Info
            for line in fan_info():
                print(line)
            # GPU Info
            for line in gpu_info():
                print(line)
            # Motherboard Info
            for line in motherboard_info():
                print(line)
            # GPU Temperature
            for line in gpu_temperature():
                print(line)
            # Battery Info
            for line in [battery_info()]:
                print(f"Battery: {line}")
            # Memory Temperature
            for line in memory_temperature():
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
        font=("monospace", 11),
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

        for line in cpu_mem_bar():
            text.insert(tk.END, line + "\n")

        for line in drive_info():
            text.insert(tk.END, line + "\n")
        
        for line in fan_info():
            text.insert(tk.END, line + "\n")
        
        for line in motherboard_info():
            text.insert(tk.END, line + "\n")
        
        for line in cpu_temperature():
            text.insert(tk.END, line + "\n")

        for line in gpu_info():
            text.insert(tk.END, line + "\n")
        
        for line in gpu_temperature():
            text.insert(tk.END, line + "\n")
        
        for line in memory_temperature():
            text.insert(tk.END, line + "\n")

        text.yview_moveto(scroll[0])

        root.after(1000, update)

    update()
    root.mainloop()


if __name__ == "__main__":
    gui_app()