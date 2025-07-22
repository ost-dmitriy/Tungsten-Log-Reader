# Tungsten Log Reader

**Developed by Dmytro Nozhenko**

## 📄 Description

**Tungsten Log Reader** is a lightweight Windows desktop utility that:

* Parses Kofax log files and extracts processing steps:

  * Scan
  * Transformation Server
  * Transformation Validation
  * PDF Generator
  * Export
* Calculates the **average processing time** for each step (rounded to minutes).
* Analyses which batch classes are used **most frequently**.
* Presents results in a **simple popup window**.

This tool helps operations and IT teams **quickly assess performance metrics** without manual log analysis.

---

## ✨ Features

* **Single-click file selection** – Select one or multiple `.log` or `.txt` files.
* **Automated parsing** – Detects relevant processing steps automatically.
* **Minute-level averages** – Clear display of rounded processing times.
* **Batch class statistic** - Statistics on the use of package classes based on the selected log file.
* **Standalone EXE** – Built using PyInstaller for one-click deployment.

---

## 🧰 Requirements

* Windows 7 or later
* Python 3.6+
* PyInstaller (for building the `.exe`)
* `app.ico` placed next to `main.py` or the final `.exe`

---

## ⚙️ Installation & Build

### Option 1 – 🔽 **Download the pre-built `.exe`**

You can **download and run the ready-to-use executable** without installing Python or building anything.

1. Download the latest version of **Tungsten Log Reader.exe** from GitHub:
   👉 [Download EXE](https://github.com/ost-dmitriy/Tungsten-Log-Reader/blob/main/Tungsten%20Log%20Reader.exe)
2. Double-click to launch the app. No installation required.

> 💡 Ideal for non-technical users or quick deployment on multiple machines.

---

### Option 2 – 🛠 **Build from source**

1. **Clone or download** the repository.

2. Place your `app.ico` in the project folder.

3. Open PowerShell as Administrator and run:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install pyinstaller
   ```

4. Build the executable:

   ```powershell
   python -m PyInstaller --onefile --windowed --name "Tungsten Log Reader" --icon "app.ico" main.py
   ```

5. The final executable will be located in the `dist` directory:

   ```
   dist\Tungsten Log Reader.exe
   ```

---

## 🚀 Usage

1. Double-click `Tungsten Log Reader.exe`.
2. In the dialog, select one or more log files (`*.log`, `*.txt`).
3. Click **Open** – the application will parse and display average times in a popup window.

---

## 🛡 Defender Exclusion (Optional)

**Microsoft Defender ASR (Attack Surface Reduction)** may block newly built EXEs.

To prevent this:

1. Open PowerShell as Administrator.
2. Run:

   ```powershell
   # Replace with your full path to the EXE
   $exe = "C:\path\to\dist\Tungsten Log Reader.exe"
   Add-MpPreference -ExclusionProcess $exe
   ```

Alternatively, you can **disable the ASR rule** (not recommended globally):

```powershell
Set-MpPreference -AttackSurfaceReductionRules_Ids D4F940AB-401B-4EFC-AADC-AD5F3C50688A `
  -AttackSurfaceReductionRules_Actions Disabled
```

> ⚠️ **Disclaimer:** Disabling ASR or adding exclusions may reduce system security. Only apply in trusted environments.

---

## 📜 License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for details.
