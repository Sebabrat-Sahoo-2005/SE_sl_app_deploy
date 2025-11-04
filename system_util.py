# use of psutil in the code 

import psutil
import time
import os
import platform
import GPUtil
from datetime import datetime, timedelta

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def bytes_to_gb(bytes_val):
    return round(bytes_val / (1024 ** 3), 2)

def get_uptime():
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    return str(timedelta(seconds=int(uptime.total_seconds())))

def get_gpu_info():
    try:
        gpus = GPUtil.getGPUs()
        gpu_data = []
        for gpu in gpus:
            gpu_data.append({
                "GPU Name": gpu.name,
                "GPU Load (%)": round(gpu.load * 100, 1),
                "GPU Temp (°C)": gpu.temperature,
                "GPU Memory Used (GB)": round(gpu.memoryUsed / 1024, 2),
                "GPU Memory Total (GB)": round(gpu.memoryTotal / 1024, 2)
            })
        return gpu_data
    except Exception:
        return []

def get_top_processes(limit=5):
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            procs.append(proc.info)
        except psutil.NoSuchProcess:
            pass
    procs = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
    return procs

def get_system_metrics():
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
    cpu_freq = psutil.cpu_freq()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net = psutil.net_io_counters()
    battery = psutil.sensors_battery()

    metrics = {
        "System": platform.node(),
        "OS": platform.system() + " " + platform.release(),
        "Uptime": get_uptime(),
        "CPU Usage (%)": cpu_percent,
        "Per-Core Usage (%)": cpu_per_core,
        "CPU Frequency (MHz)": round(cpu_freq.current, 2) if cpu_freq else "N/A",
        "Memory Usage (%)": mem.percent,
        "Used Memory (GB)": bytes_to_gb(mem.used),
        "Total Memory (GB)": bytes_to_gb(mem.total),
        "Disk Usage (%)": disk.percent,
        "Used Disk (GB)": bytes_to_gb(disk.used),
        "Total Disk (GB)": bytes_to_gb(disk.total),
        "Bytes Sent (MB)": round(net.bytes_sent / (1024 ** 2), 2),
        "Bytes Received (MB)": round(net.bytes_recv / (1024 ** 2), 2),
        "Battery (%)": round(battery.percent, 1) if battery else "N/A",
        "Charging": battery.power_plugged if battery else "N/A"
    }

    return metrics

def print_metrics(metrics, gpu_data, top_procs):
    clear_screen()
    print("=" * 50)
    print("        🖥️  ADVANCED SYSTEM MONITOR (psutil + GPUtil)")
    print("=" * 50)
    for key, value in metrics.items():
        if isinstance(value, list):
            continue
        print(f"{key:<25}: {value}")
    print("=" * 50)
    print("Per-Core CPU Usage:")
    for i, val in enumerate(metrics["Per-Core Usage (%)"]):
        print(f"  Core {i+1:<2}: {val:>5}%")
    print("=" * 50)
    if gpu_data:
        for gpu in gpu_data:
            print(f"GPU: {gpu['GPU Name']}")
            print(f"  Load: {gpu['GPU Load (%)']}% | Temp: {gpu['GPU Temp (°C)']}°C")
            print(f"  Memory: {gpu['GPU Memory Used (GB)']}/{gpu['GPU Memory Total (GB)']} GB")
            print("-" * 50)
    print("=" * 50)
    print("Top 5 Processes by CPU Usage:")
    for proc in top_procs:
        print(f"PID {proc['pid']:>5} | {proc['name'][:20]:<20} | CPU: {proc['cpu_percent']:>5}%")
    print("=" * 50)

if __name__ == "__main__":
    try:
        while True:
            data = get_system_metrics()
            gpu_data = get_gpu_info()
            top_procs = get_top_processes()
            print_metrics(data, gpu_data, top_procs)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nExiting System Monitor...")