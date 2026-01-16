from logging import root
import platform
from pydoc import text
import psutil
import os
import time
import shutil

MAX_POINTS = 60  # last 60 seconds

cpu_history = []
mem_history = []
disk_history = []


def update_history():
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    cpu_history.append(cpu)
    mem_history.append(mem)
    disk_history.append(disk)

    if len(cpu_history) > MAX_POINTS:
        cpu_history.pop(0)
        mem_history.pop(0)


def draw_graph(canvas, data, color, label):
    canvas.delete("all")

    width = int(canvas["width"])
    height = int(canvas["height"])
    padding = 10

    if len(data) < 2:
        return

    max_val = 100  # percent-based graph
    step_x = (width - 2 * padding) / (len(data) - 1)

    points = []
    for i, value in enumerate(data):
        x = padding + i * step_x
        y = height - padding - (value / max_val) * (height - 2 * padding)
        points.extend([x, y])

    canvas.create_line(points, fill=color, width=2, smooth=True)
    canvas.create_text(
        5, 5,
        anchor="nw",
        text=f"{label}: {data[-1]:.1f}%",
        fill=color,
        font=("monospace", 10, "bold")
    )


ALERTS = {
    "cpu": 90,
    "memory": 90,
    "gpu_temp": 80,
    "battery_low": 20
}

def check_alerts():
    alerts = []
    cpu = psutil.cpu_percent(interval=None)
    if cpu > ALERTS["cpu"]:
        alerts.append(f"⚠️ CPU Usage High: {cpu:.1f}%")
    
    mem = psutil.virtual_memory().percent
    if mem > ALERTS["memory"]:
        alerts.append(f"⚠️ Memory Usage High: {mem:.1f}%")
    
    # GPU temp (if available)
    temps = psutil.sensors_temperatures()
    if temps:
        for name, entries in temps.items():
            for entry in entries:
                if "gpu" in entry.label.lower() or "nvidia" in name.lower():
                    if entry.current > ALERTS["gpu_temp"]:
                        alerts.append(f"⚠️ GPU Temp High: {entry.current} °C")
    
    # Battery
    bat = psutil.sensors_battery()
    if bat and not bat.power_plugged and bat.percent < ALERTS["battery_low"]:
        alerts.append(f"⚠️ Battery Low: {bat.percent:.1f}%")

    return alerts



THEMES = {
    "dark": {
        "bg": "#111111",
        "fg": "#e6e6e6",
        "accent": "#4fc3f7"
    },
    "light": {
        "bg": "#f5f5f5",
        "fg": "#111111",
        "accent": "#1976d2"
    },
    "hacker": {
        "bg": "#000000",
        "fg": "#00ff00",
        "accent": "#00cc00"
    },
    "red": {
        "bg": "#2e0000",
        "fg": "#ff4d4d",
        "accent": "#ff1a1a"
    }
}



def apply_theme(root, text, theme_name):
    theme = THEMES[theme_name]
    root.configure(bg=theme["bg"])
    text.configure(
        bg=theme["bg"],
        fg=theme["fg"],
        insertbackground=theme["fg"]  # caret color
    )


current_theme = "dark"  # default


def read_sys(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return None

## System Info ##

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
            f"CPU: {platform.processor()}",
            f"CPU Frequency: {psutil.cpu_freq().current:.2f} MHz",
            f"CPU Cores: {psutil.cpu_count(logical=False)}",
            f"Threads: {psutil.cpu_count(logical=True)}",
            f"Memory: {round(psutil.virtual_memory().total / (1024**3), 2)} GB",
            f"Disk: {round(psutil.disk_usage('/').total / (1024**3), 2)} GB",
            f"Uptime: {uptime_seconds / 3600:.2f} hours",
            f"User: {os.getlogin()}",
            f"Display Size: {shutil.get_terminal_size().columns}x{shutil.get_terminal_size().lines}",
            f"Filesystem: {platform.system()}"
        
        
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

def swap_memory():
    lines = ["=== Swap Memory ==="]
    swap = psutil.swap_memory()
    lines.append(f"Swap: {round(swap.total / (1024**3), 2)} GB, Used: {round(swap.used / (1024**3), 2)} GB ({swap.percent}%)")
    return lines

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
    width = 50
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

def keyboard_info():
    lines = ["=== Keyboard Information ==="]
    try:
        if platform.system() == "Linux":
            lsusb_output = os.popen("lsusb | grep -i 'keyboard'").read()
            keyboards = lsusb_output.strip().split("\n")
            if not keyboards or keyboards == ['']:
                return ["===No keyboard information found.==="]
            for kb in keyboards:
                lines.append(kb)
        else:
            lines.append("===Keyboard info not implemented for this OS.===")
    except Exception as e:
        lines.append(f"Keyboard info error: {e}")
    return lines


def mouse_info():
    lines = ["=== Mouse Information ==="]
    try:
        if platform.system() == "Linux":
            lsusb_output = os.popen("lsusb | grep -i 'mouse'").read()
            mice = lsusb_output.strip().split("\n")
            if not mice or mice == ['']:
                return ["===No mouse information found.==="]
            for mouse in mice:
                lines.append(mouse)
        else:
            lines.append("===Mouse info not implemented for this OS.===")
    except Exception as e:
        lines.append(f"Mouse info error: {e}")
    return lines


def os_info():
    lines = ["=== Operating System Information ==="]
    try:
        if platform.system() == "Linux":
            distro = ""
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            distro = line.split("=")[1].strip().strip('"')
                            break
            except Exception:
                distro = "Unknown Linux Distro"
            lines.append(f"Distribution: {distro}")
        elif platform.system() == "Windows":
            lines.append(f"Windows Version: {platform.version()}")
        elif platform.system() == "Darwin":
            mac_ver = platform.mac_ver()[0]
            lines.append(f"macOS Version: {mac_ver}")
        else:
            lines.append("OS information not implemented for this OS.")
    except Exception as e:
        lines.append(f"OS info error: {e}")
    return lines


def wifi_info():
    lines = ["=== Wi-Fi Information ==="]
    try:
        if platform.system() == "Linux":
            iwconfig_output = os.popen("iwconfig 2>/dev/null | grep 'ESSID'").read()
            wifis = iwconfig_output.strip().split("\n")
            if not wifis or wifis == ['']:
                return ["===No Wi-Fi information found.==="]
            for wifi in wifis:
                lines.append(wifi)
        else:
            lines.append("===Wi-Fi info not implemented for this OS.===")
    except Exception as e:
        lines.append(f"Wi-Fi info error: {e}")
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
            # OS Info
            for line in os_info():
                print(line)
            # Keyboard Info
            for line in keyboard_info():
                print(line)
            # Mouse Info
            for line in mouse_info():
                print(line)
            # Wi-Fi Info
            for line in wifi_info():
                print(line)
            
            print("\nPress Ctrl+C to exit...")
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nExiting...")

import tkinter as tk

import tkinter as tk

# Define your themes
THEMES = {
    "dark": {
        "bg": "#111111",
        "fg": "#21b0ed",
        "accent": "#00aeff"
    },
    "light": {
        "bg": "#f5f5f5",
        "fg": "#111111",
        "accent": "#FFFFFF"
    },
    "hacker": {
        "bg": "#000000",
        "fg": "#00ff00",
        "accent": "#00cc00"
    },
    "red": {
        "bg": "#2e0000",
        "fg": "#ff4d4d",
        "accent": "#ff1a1a"
    }
}
current_theme = "dark"

# List of all section functions
SECTIONS = [
    system_info,
    swap_memory,
    network_info,
    top_processes,
    cpu_mem_bar,
    drive_info,
    fan_info,
    motherboard_info,
    cpu_temperature,
    gpu_info,
    gpu_temperature,
    memory_temperature,
    os_info,
    keyboard_info,
    mouse_info,
    wifi_info
]

def apply_theme(root, text, theme_name):
    theme = THEMES[theme_name]
    root.configure(bg=theme["bg"])
    text.configure(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["fg"])

def gui_app():
    global current_theme





    root = tk.Tk()
    root.title("System Monitor")
    root.geometry("800x600")

    # Text widget
    text = tk.Text(root, font=("monospace", 11), bg="#111", fg="#0f0", insertbackground="white")
    text.pack(fill="both", expand=True)

    # Graph frame
    graph_frame = tk.Frame(root, bg=THEMES[current_theme]["bg"])
    graph_frame.pack(fill="x")

    cpu_canvas = tk.Canvas(graph_frame, width=380, height=120, bg="#000000", highlightthickness=0)
    mem_canvas = tk.Canvas(graph_frame, width=380, height=120, bg="#000000", highlightthickness=0)
    disk_canvas = tk.Canvas(graph_frame, width=380, height=120, bg="#000000", highlightthickness=0)
    cpu_temperature_canvas = tk.Canvas(graph_frame, width=380, height=120, bg="#000000", highlightthickness=0)
    cpu_canvas.pack(side="left", padx=5, pady=5)
    mem_canvas.pack(side="left", padx=5, pady=5)
    disk_canvas.pack(side="left", padx=5, pady=5)

    # Apply default theme
    apply_theme(root, text, current_theme)

    # Function to switch themes
    def switch_theme(event=None):
        global current_theme
        names = list(THEMES.keys())
        current_theme = names[(names.index(current_theme) + 1) % len(names)]
        apply_theme(root, text, current_theme)

    root.bind("<F2>", switch_theme)  # Press F2 to cycle themes



    
    # Update function
    def update():
        scroll = text.yview()  # preserve scroll position
        text.delete("1.0", tk.END)
        update_history()
        draw_graph(cpu_canvas, cpu_history, THEMES[current_theme]["accent"], "CPU Usage")
        draw_graph(mem_canvas, mem_history, THEMES[current_theme]["accent"], "Memory Usage")
        draw_graph(disk_canvas, disk_history, THEMES[current_theme]["accent"], "Disk Usage")
        alerts = check_alerts()
        if alerts:
            text.insert(tk.END, "\n=== ALERTS ===\n")
            for alert in alerts:
                text.insert(tk.END, alert + "\n")
                text.insert(tk.END, "\n")

        for section in SECTIONS:
            lines = section()
            for line in lines:
                text.insert(tk.END, line + "\n")
            text.insert(tk.END, "\n")  # blank line between sections

        text.yview_moveto(scroll[0])  # restore scroll
        root.after(1000, update)

    update()
    root.mainloop()

if __name__ == "__main__":
    gui_app()