#!/bin/bash

# Function to clear the screen
clear_screen() {
    clear
}

# Function to get system info
system_info() {
    echo "=== System Information ==="
    echo "OS/Kernel Version: $(uname -s) $(uname -r)"
    echo "Architecture: $(uname -m)"
    echo "CPU: $(lscpu | grep 'Model name' | sed 's/Model name: *//')"
    echo "CPU Cores: $(nproc --all)"
    echo "Threads: $(lscpu | grep '^CPU(s):' | awk '{print $2}')"
    echo "Memory: $(free -h | awk '/Mem:/ {print $2}')"
    echo "Disk: $(df -h / | awk 'NR==2 {print $2}')"
    echo "Uptime: $(uptime -p)"
    
    # Battery info if available
    if command -v acpi &> /dev/null; then
        echo "Battery: $(acpi | awk -F', ' '{print $2 " (" $3 ")"}')"
    else
        echo "Battery: N/A"
    fi
    echo ""
}

# Function to show CPU and memory bars
cpu_mem_usage() {
    CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
    MEM=$(free | awk '/Mem/ {printf("%.0f"), $3/$2 * 100}')
    WIDTH=$(($(tput cols)-20))
    
    # Generate bars
    CPU_BAR=$(printf "%-${WIDTH}s" "#" | cut -c1-$((CPU*WIDTH/100)))
    MEM_BAR=$(printf "%-${WIDTH}s" "#" | cut -c1-$((MEM*WIDTH/100)))
    
    echo "=== CPU & Memory Usage ==="
    echo "CPU: [${CPU_BAR}] ${CPU}%"
    echo "MEM: [${MEM_BAR}] ${MEM}%"
    echo ""
}

# Function to show network usage
network_info() {
    echo "=== Network Interfaces ==="
    for iface in $(ls /sys/class/net); do
        RX=$(cat /sys/class/net/$iface/statistics/rx_bytes)
        TX=$(cat /sys/class/net/$iface/statistics/tx_bytes)
        echo "$iface: Sent=$(echo "$TX / 1048576" | bc) MB | Recv=$(echo "$RX / 1048576" | bc) MB"
    done
    echo ""
}

# Function to show top 5 processes by CPU and memory
top_processes() {
    echo "=== Top 5 Processes ==="
    ps -eo comm,pcpu,pmem --sort=-pcpu | head -n 6 | awk '{printf "%-25s | CPU: %5s%% | MEM: %5s%%\n",$1,$2,$3}'
    echo ""
}

# Main loop
while true; do
    clear_screen
    system_info
    cpu_mem_usage
    network_info
    top_processes
    echo "Press Ctrl+C to exit..."
    sleep 1
done
