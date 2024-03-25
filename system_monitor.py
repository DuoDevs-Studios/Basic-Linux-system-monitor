import psutil
import platform
import tkinter as tk
from tkinter import ttk
import os
import time

refresh_interval = 1000  # 1 second
paused = False

def clear_screen():
    os.system('clear')  # For Linux/OS X

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def update_usage():
    if not paused:
        clear_screen()

        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_label.config(text=f"CPU Usage: {cpu_usage}%", foreground="purple")

        svmem = psutil.virtual_memory()
        memory_label.config(text=f"Memory Usage: {get_size(svmem.used)} / {get_size(svmem.total)} ({svmem.percent}%)", foreground="purple")

        partitions = psutil.disk_partitions()
        disk_text = ""
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disk_text += f"{partition.device} - Disk Usage: {get_size(partition_usage.used)} / {get_size(partition_usage.total)} ({partition_usage.percent}%)\n"
            except PermissionError:
                continue
        disk_label.config(text=disk_text, foreground="purple")

        net_io = psutil.net_io_counters()
        network_label.config(text=f"Total Network Sent: {get_size(net_io.bytes_sent)}\nTotal Network Received: {get_size(net_io.bytes_recv)}", foreground="purple")

        # Temperature Monitoring
        try:
            temperatures = psutil.sensors_temperatures()
            cpu_temp = temperatures['coretemp'][0].current
            temp_label.config(text=f"CPU Temperature: {cpu_temp}°C", foreground="purple")
        except Exception as e:
            temp_label.config(text="CPU Temperature: N/A", foreground="purple")

        # Process List
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(f"PID: {proc.info['pid']} | Name: {proc.info['name']} | CPU: {proc.info['cpu_percent']}% | Memory: {proc.info['memory_percent']}%")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        process_listbox.delete(0, tk.END)
        for process in processes:
            process_listbox.insert(tk.END, process)

        # System Information
        system_info = platform.uname()
        system_label.config(text=f"System: {system_info.system} {system_info.release}\nArchitecture: {system_info.machine}\nKernel Version: {system_info.version}", foreground="purple")

    root.after(refresh_interval, update_usage)

def toggle_pause():
    global paused
    paused = not paused
    pause_button.config(text="Resume" if paused else "Pause")

def start_logging():
    logging_time = 30  # seconds
    log_file = "system_log.txt"
    with open(log_file, 'w') as f:
        start_time = time.time()
        while time.time() - start_time <= logging_time:
            f.write(f"{time.ctime()}\n")
            f.write(f"CPU Usage: {psutil.cpu_percent()}%\n")
            f.write(f"Memory Usage: {psutil.virtual_memory().percent}%\n")
            f.write(f"Disk Usage: {psutil.disk_usage('/').percent}%\n")
            f.write(f"Network Sent: {psutil.net_io_counters().bytes_sent}\n")
            f.write(f"Network Received: {psutil.net_io_counters().bytes_recv}\n\n")
            time.sleep(1)
    print(f"Logging complete. Data saved to {log_file}")

root = tk.Tk()
root.title("System Monitor")
root.configure(bg="black")

tab_control = ttk.Notebook(root)
tab_control.configure(style='Dark.TNotebook')

tab1 = ttk.Frame(tab_control, style='Dark.TFrame')
tab_control.add(tab1, text="CPU")

tab2 = ttk.Frame(tab_control, style='Dark.TFrame')
tab_control.add(tab2, text="Memory")

tab3 = ttk.Frame(tab_control, style='Dark.TFrame')
tab_control.add(tab3, text="Disk")

tab4 = ttk.Frame(tab_control, style='Dark.TFrame')
tab_control.add(tab4, text="Network")

tab5 = ttk.Frame(tab_control, style='Dark.TFrame')
tab_control.add(tab5, text="Temperature")

tab6 = ttk.Frame(tab_control, style='Dark.TFrame')
tab_control.add(tab6, text="Processes")

tab7 = ttk.Frame(tab_control, style='Dark.TFrame')
tab_control.add(tab7, text="System Info")

tab_control.pack(expand=1, fill="both")

cpu_label = tk.Label(tab1, text="", foreground="purple", bg="black")
cpu_label.pack(padx=10, pady=10)

memory_label = tk.Label(tab2, text="", foreground="purple", bg="black")
memory_label.pack(padx=10, pady=10)

disk_label = tk.Label(tab3, text="", foreground="purple", bg="black")
disk_label.pack(padx=10, pady=10)

network_label = tk.Label(tab4, text="", foreground="purple", bg="black")
network_label.pack(padx=10, pady=10)

temp_label = tk.Label(tab5, text="", foreground="purple", bg="black")
temp_label.pack(padx=10, pady=10)

process_scrollbar = tk.Scrollbar(tab6)
process_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

process_listbox = tk.Listbox(tab6, yscrollcommand=process_scrollbar.set, foreground="purple", bg="black")
process_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
process_scrollbar.config(command=process_listbox.yview)

system_label = tk.Label(tab7, text="", foreground="purple", bg="black")
system_label.pack(padx=10, pady=10)

refresh_button = tk.Button(root, text="Refresh", command=update_usage)
refresh_button.pack()

pause_button = tk.Button(root, text="Pause", command=toggle_pause)
pause_button.pack()

start_logging_button = tk.Button(root, text="Start Logging", command=start_logging)
start_logging_button.pack()

update_usage()

style = ttk.Style()
style.configure('Dark.TFrame', background='black')

root.mainloop()
