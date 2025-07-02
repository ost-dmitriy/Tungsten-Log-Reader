import csv
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from collections import defaultdict, Counter
import os
import sys


def parse_log_file(filepath):
    durations = defaultdict(list)
    errors = defaultdict(int)
    batch_classes = []

    with open(filepath, 'r', newline='', encoding='utf-16') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue

            record_type = row[0].strip('"')
            if record_type == '04' and len(row) > 1:
                batch_name = row[1].strip('"')
                if batch_name:
                    batch_classes.append(batch_name)

            elif record_type == '05':
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

    return durations, errors, batch_classes


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


def show_batch_class_window(parent, counter):
    total = sum(counter.values())
    win = tk.Toplevel(parent)
    win.title("Batch Class Details")
    win.geometry('400x300')

    # Create Treeview for tabular display
    cols = ('Class', 'Count', 'Percentage')
    tree = ttk.Treeview(win, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    # Populate rows
    for cls, cnt in counter.most_common():
        pct = cnt / total * 100
        tree.insert('', 'end', values=(cls, cnt, f"{pct:.1f}%"))

    # Add Back button
    btn_back = ttk.Button(win, text="Back", command=win.destroy)
    btn_back.pack(pady=(0, 10))


def show_results_window(root, averages, errors, batch_counter):
    win = tk.Toplevel(root)
    win.title("Results")

    text = tk.Text(win, width=50, height=15)
    text.pack(padx=10, pady=10)
    text.insert('end', "Average processing times:\n")
    for step, avg in averages.items():
        line = f"- {step}: {format_duration(avg)}"
        if errors.get(step):
            line += f" ({errors[step]} errors)"
        text.insert('end', line + "\n")
    total_errors = sum(errors.values())
    if total_errors:
        text.insert('end', f"\nTotal errors: {total_errors}\n")
    text.config(state='disabled')

    btn_frame = ttk.Frame(win)
    btn_frame.pack(pady=10)

    btn_ok = ttk.Button(btn_frame, text="OK", command=win.destroy)
    btn_ok.pack(side='left', padx=5)

    btn_batch = ttk.Button(btn_frame, text="Batch Class Statistic", 
                           command=lambda: show_batch_class_window(root, batch_counter))
    btn_batch.pack(side='left', padx=5)


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
    all_batch_classes = []

    for p in paths:
        durations, errors, batch_classes = parse_log_file(p)
        for step, vals in durations.items():
            all_durations[step].extend(vals)
        for step, count in errors.items():
            all_errors[step] += count
        all_batch_classes.extend(batch_classes)

    averages = compute_averages(all_durations)
    batch_counter = Counter(all_batch_classes)

    if not averages and not all_errors and not batch_counter:
        messagebox.showinfo("No Data", "No valid data or errors found.")
        return

    show_results_window(root, averages, all_errors, batch_counter)
    root.mainloop()

if __name__ == '__main__':
    main()
