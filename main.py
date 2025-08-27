import csv
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from collections import defaultdict, Counter
import os
import sys
import atexit
import ctypes

mutex_handle = None
lock_fd = None
lock_path = None

def acquire_single_instance(app_id="LogTimeAverager_v1"):
    global mutex_handle, lock_fd, lock_path
    if os.name == 'nt':
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        mutex_name = f"Global\\{app_id}"
        mutex_handle = kernel32.CreateMutexW(None, False, mutex_name)
        err = ctypes.get_last_error()
        ERROR_ALREADY_EXISTS = 183
        if not mutex_handle:

            return False, "Can't create mutex handle."
        if err == ERROR_ALREADY_EXISTS:

            kernel32.CloseHandle(mutex_handle)
            mutex_handle = None
            return False, "Another instance of the application is already running."

        atexit.register(lambda: kernel32.CloseHandle(mutex_handle) if mutex_handle else None)
        return True, None
    else:

        try:
            base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            lock_path = os.path.join(base, f".{app_id}.lock")

            flags = os.O_CREAT | os.O_EXCL | os.O_RDWR
            lock_fd = os.open(lock_path, flags)

            os.write(lock_fd, str(os.getpid()).encode())
            atexit.register(_release_posix_lock)
            return True, None
        except FileExistsError:
            return False, "Another instance of the application is already running."
        except Exception as e:
            return False, f"Can't create lock file: {e}"

def _release_posix_lock():
    global lock_fd, lock_path
    try:
        if lock_fd:
            os.close(lock_fd)
            lock_fd = None
        if lock_path and os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except:
                pass
            lock_path = None
    except:
        pass


def parse_log_file(filepath):
    durations = defaultdict(list)
    errors = defaultdict(int)
    batch_classes = []

    encodings_to_try = ['utf-8', 'utf-8-sig', 'utf-16', 'cp1252']

    min_dt = None
    max_dt = None

    file_read = False
    for enc in encodings_to_try:
        try:
            with open(filepath, 'r', newline='', encoding=enc) as f:
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
                            if min_dt is None or start_dt < min_dt:
                                min_dt = start_dt
                            if max_dt is None or end_dt > max_dt:
                                max_dt = end_dt
                            step = row[5].strip('"')
                            durations[step].append((end_dt - start_dt).total_seconds())
                        except Exception:
                            continue
                        combined = ' '.join(cell.strip('"') for cell in row)
                        if 'error' in combined.lower():
                            try:
                                errors[step] += 1
                            except Exception:
                                pass
            file_read = True
            break
        except UnicodeDecodeError:
            continue
        except Exception:
            continue

    if not file_read:
        messagebox.showerror("Encoding Error", f"Unable to read file {os.path.basename(filepath)} with supported encodings.")
        return durations, errors, batch_classes, None, None

    min_date = min_dt.date() if min_dt else None
    max_date = max_dt.date() if max_dt else None

    return durations, errors, batch_classes, min_date, max_date

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

def format_date(d):
    return d.strftime("%d-%m-%Y") if d else "N/A"

def show_batch_class_window(parent, counter):
    total = sum(counter.values())
    win = tk.Toplevel(parent)
    win.title("Batch Class Details")
    win.geometry('400x300')
    win.resizable(False, False)

    try:
        base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        win.iconbitmap(os.path.join(base, 'app.ico'))
    except:
        pass

    cols = ('Class', 'Count', 'Percentage')
    tree = ttk.Treeview(win, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    for cls, cnt in counter.most_common():
        pct = cnt / total * 100 if total else 0
        tree.insert('', 'end', values=(cls, cnt, f"{pct:.1f}%"))

    btn_back = ttk.Button(win, text="Back", command=win.destroy)
    btn_back.pack(pady=(0, 10))

def show_results_window(root, averages, errors, batch_counter, min_date, max_date, on_close):
    win = tk.Toplevel(root)
    win.title("Results")
    win.resizable(False, False)

    try:
        base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        win.iconbitmap(os.path.join(base, 'app.ico'))
    except:
        pass
    win.protocol("WM_DELETE_WINDOW", on_close)

    text = tk.Text(win, width=60, height=18)
    text.pack(padx=10, pady=10)

    date_from = format_date(min_date)
    date_till = format_date(max_date)
    header = f"Batches analytics | Timestamp:{date_from} - {date_till}:\n\n"
    text.insert('end', header)

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

    btn_ok = ttk.Button(btn_frame, text="OK", command=on_close)
    btn_ok.pack(side='left', padx=5)

    btn_batch = ttk.Button(btn_frame, text="Batch Class Statistic",
                           command=lambda: show_batch_class_window(root, batch_counter))
    btn_batch.pack(side='left', padx=5)

def main():
    ok, msg = acquire_single_instance()
    if not ok:

        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning("Already Running", msg)
            root.destroy()
        except:
            print(msg)
        sys.exit(0)

    root = tk.Tk()
    root.withdraw()
    root.title("Log Time Averager")

    def on_close():

        root.destroy()
        sys.exit()

    root.protocol("WM_DELETE_WINDOW", on_close)

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
        on_close()
        return

    all_durations = defaultdict(list)
    all_errors = defaultdict(int)
    all_batch_classes = []

    global_min_date = None
    global_max_date = None

    for p in paths:
        durations, errors, batch_classes, min_date, max_date = parse_log_file(p)
        for step, vals in durations.items():
            all_durations[step].extend(vals)
        for step, count in errors.items():
            all_errors[step] += count
        all_batch_classes.extend(batch_classes)

        if min_date:
            if global_min_date is None or min_date < global_min_date:
                global_min_date = min_date
        if max_date:
            if global_max_date is None or max_date > global_max_date:
                global_max_date = max_date

    averages = compute_averages(all_durations)
    batch_counter = Counter(all_batch_classes)

    if not averages and not all_errors and not batch_counter:
        messagebox.showinfo("No Data", "No valid data or errors found.")
        on_close()
        return

    show_results_window(root, averages, all_errors, batch_counter, global_min_date, global_max_date, on_close)

    root.mainloop()

if __name__ == '__main__':
    main()
