Clear-Host

$CPU_ALERT = 90
$MEM_ALERT = 90
$BATTERY_ALERT = 20

function HR { Write-Host "------------------------------------------------------------" }

function CPU_Usage {
    (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue
}



function Memory_Usage {
    $os = Get-CimInstance Win32_OperatingSystem
    [math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100, 1)
}

function Disk_Usage {
    Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'" |
        Select-Object @{n="Used";e={[math]::Round(($_.Size - $_.FreeSpace)/$_.Size*100,1)}}
}

function Battery_Info {
    $bat = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue
    if ($bat) {
        "$($bat.EstimatedChargeRemaining)%"
    } else {
        "N/A"
    }
}

function GPU_Info {
    Get-CimInstance Win32_VideoController |
        Select-Object Name, AdapterRAM |
        ForEach-Object {
            "GPU: $($_.Name) | VRAM: $([math]::Round($_.AdapterRAM / 1GB,2)) GB"
        }
}

function Top_Processes {
    Get-Process |
        Sort-Object CPU -Descending |
        Select-Object -First 5 |
        ForEach-Object {
            "{0,-20} CPU:{1,6:N1} MEM:{2,6:N1}MB" -f `
            $_.ProcessName, $_.CPU, ($_.WorkingSet/1MB)
        }
}

function RAM_Usage {
    $os = Get-CimInstance Win32_OperatingSystem
    [math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100, 1)
}

while ($true) {
    Clear-Host

    HR
    Write-Host "=== SYSTEM MONITOR ==="
    HR

    $cpu = CPU_Usage
    $mem = Memory_Usage
    $disk = (Disk_Usage).Used
    $bat = Battery_Info

    Write-Host ("CPU Usage: {0:N1}%" -f $cpu)
    Write-Host ("Memory Usage: {0}%" -f $mem)
    Write-Host ("Disk Usage (C:): {0}%" -f $disk)
    Write-Host ("Battery: {0}" -f $bat)
    Write-Host ("RAM Usage: {0}%" -f (RAM_Usage))

    HR
    Write-Host "=== GPU ==="
    GPU_Info

    HR
    Write-Host "=== TOP PROCESSES ==="
    Top_Processes

    HR
    Write-Host "=== RAM USAGE ==="
    RAM_Usage


    if ($cpu -gt $CPU_ALERT) { Write-Host "⚠️ CPU USAGE HIGH" -ForegroundColor Red }
    if ($mem -gt $MEM_ALERT) { Write-Host "⚠️ MEMORY USAGE HIGH" -ForegroundColor Red }
    if ($bat -ne "N/A" -and [int]$bat.TrimEnd('%') -lt $BATTERY_ALERT) {
        Write-Host "⚠️ BATTERY LOW" -ForegroundColor Red
    }

    Start-Sleep 2.5
}
