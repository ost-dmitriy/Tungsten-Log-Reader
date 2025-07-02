import csv
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import defaultdict
import os
import sys

def parse_log_file(filepath):
    durations = defaultdict(list)
    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip('"') == '05':
                try:
                    start_str = row[1].strip('"') + ' ' + row[2].strip('"')
                    end_str = row[3].strip('"') + ' ' + row[4].strip('"')
                    start_dt = datetime.datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
                    end_dt = datetime.datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
                    step_name = row[5].strip('"')
                    durations[step_name].append((end_dt - start_dt).total_seconds())
                except Exception:
                    continue
    return durations

def average_durations(all_durations):
    averages = {}
    for step, times in all_durations.items():
        if times:
            avg_seconds = sum(times) / len(times)
            averages[step] = avg_seconds
    return averages

def format_duration(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes > 0:
        if secs > 0:
            return f"{minutes} min {secs} sec"
        else:
            return f"{minutes} min"
    else:
        return f"{secs} sec"

def main():
    root = tk.Tk()
    root.withdraw()
    root.title("Tungsten Log Reader")
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, 'app.ico')
        root.iconbitmap(icon_path)
    except Exception:
        pass

    filepaths = filedialog.askopenfilenames(
        title="Select log file(s)",
        filetypes=[("Log files", "*.log *.txt"), ("All files", "*")]
    )
    if not filepaths:
        messagebox.showwarning("No Selection", "No files selected. Exiting.")
        return

    aggregate = defaultdict(list)
    for path in filepaths:
        durations = parse_log_file(path)
        for step, times in durations.items():
            aggregate[step].extend(times)

    averages = average_durations(aggregate)
    if not averages:
        messagebox.showinfo("No Data", "No valid entries found in the selected files.")
        return

    output_lines = ["Average processing times:"]
    for step, avg_sec in averages.items():
        formatted = format_duration(avg_sec)
        output_lines.append(f"- {step}: {formatted}")
    output_lines.append("")
    output_lines.append("Developed by Dmytro Nozhenko")
    output_message = "\n".join(output_lines)

    messagebox.showinfo("Processing Results", output_message)

if __name__ == '__main__':
    main()
