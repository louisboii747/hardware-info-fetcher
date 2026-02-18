# HardwareMon #


HardwareMon is a lightweight system monitoring tool designed to provide a detailed overview of your computer’s hardware and performance metrics. It can display CPU, memory, disk, GPU, battery, network, and peripheral information in real time. The project includes two main implementations: a Python version for Linux systems and a PowerShell version for Windows.

## Features ##

HardwareMon gathers and presents information such as CPU usage, memory usage, disk activity, top running processes, GPU specifications and temperatures, battery status, and peripheral details. On Linux, the Python version uses the psutil library and native system commands to extract detailed system information. On Windows, the PowerShell version leverages CIM/WMI queries to report similar statistics.

The Linux version also includes a GUI mode built with Tkinter, offering a modern and configurable interface with light, dark, and hacker-style themes. To cycle themes, press F2. Graphs for CPU, memory, and disk usage are updated in real time, providing a quick visual snapshot of system performance.

## Installation ##
Linux (Python version)

Ensure Python 3 and the psutil library are installed.

Clone the repository or download the Python script.

Run the script from a terminal:

```
python3 hardware_mon.py
```
## Windows (PowerShell version) ##

Open PowerShell.

Run the script directly or use the provided .exe if available:

```
.\hardware-info.ps1
```

The Windows .exe was generated from the PowerShell script but is not maintained as actively as the source script. It may lack the latest bug fixes or features and is provided primarily for convenience.

# Notes #

The Windows version relies on CIM/WMI queries and may have limitations on certain hardware or older operating systems. The Linux Python version provides more extensive monitoring capabilities, including GPU lane and VRAM information for NVIDIA and AMD cards, as well as real-time graphical representations.

While the project can run as a standalone script or executable, it is recommended to use the scripts directly to ensure maximum compatibility and access to the latest updates.

# Contribution #

Contributions and suggestions are welcome. Please feel free to fork the repository and submit pull requests or report issues on the project’s issue tracker.

Made with ❤️ by Louis
