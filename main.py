import csv
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import defaultdict
import os
import sys

def parse_log_file(filepath):
    durations = defaultdict(list)
    errors = defaultdict(int)
    with open(filepath, 'r', newline='', encoding='utf-16') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip('"') == '05':
                try:
                    start_str = row[1].strip('"') + ' ' + row[2].strip('"')
                    end_str = row[3].strip('"') + ' ' + row[4].strip('"')
                    start_dt = datetime.datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
                    end_dt = datetime.datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
                    step = row[5].strip('"')
                    durations[step].append((end_dt - start_dt).total_seconds())
                except:
                    continue
                combined = ' '.join(cell.strip('"') for cell in row)
                if 'error' in combined.lower():
                    errors[step] += 1
    return durations, errors

def compute_averages(durations):
    averages = {}
    for step, times in durations.items():
        if times:
            averages[step] = sum(times) / len(times)
    return averages

def format_duration(sec):
    minutes = int(sec // 60)
    seconds = int(sec % 60)
    if minutes:
        return f"{minutes} min {seconds} sec" if seconds else f"{minutes} min"
    return f"{seconds} sec"

def main():
    root = tk.Tk()
    root.withdraw()
    root.title("Log Time Averager")
    try:
        base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        root.iconbitmap(os.path.join(base, 'app.ico'))
    except:
        pass

    paths = filedialog.askopenfilenames(
        title="Select log file(s)",
        filetypes=[("Log files", "*.log *.txt"), ("All files", "*")]
    )
    if not paths:
        messagebox.showwarning("No Selection", "No files selected.")
        return

    all_durations = defaultdict(list)
    all_errors = defaultdict(int)

    for p in paths:
        durations, errors = parse_log_file(p)
        for step, vals in durations.items():
            all_durations[step].extend(vals)
        for step, count in errors.items():
            all_errors[step] += count

    averages = compute_averages(all_durations)
    if not averages and not all_errors:
        messagebox.showinfo("No Data", "No valid data or errors found.")
        return

    lines = ["Average processing times:"]
    for step, avg in averages.items():
        text = f"- {step}: {format_duration(avg)}"
        if all_errors.get(step):
            text += f" ({all_errors[step]} errors)"
        lines.append(text)

    total = sum(all_errors.values())
    if total:
        lines.append(f"\nTotal errors in file: {total}")

    lines.append(f"\nDeveloped by Dmytro Nozhenko")
    messagebox.showinfo("Results", "\n".join(lines))

if __name__ == '__main__':
    main()
