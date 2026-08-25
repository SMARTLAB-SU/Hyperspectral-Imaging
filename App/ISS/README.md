# ⚙️ App / ISS — Installer Scripts & Application Launchers

Welcome to the **Hyperspectral Imaging System** installer script and launcher directory. This folder contains the Inno Setup build configuration (`setup.iss`) as well as quick-launch scripts (`Launch_App.bat` and `Launch_App.sh`) for Windows, Linux, and macOS environments.

---

## 📦 Directory Contents & Direct Download Links

### 1. ⚡ `Launch_App.bat` (Windows Batch Launcher)
- 📌 **Description:** Automated Windows Command Prompt launcher. Double-clicking this file executes the application binary (`HyperspectralImaging.exe`) or opens the Google Drive download page directly.
- 📥 **Direct Download:** [⚡ Download Launch_App.bat (Google Drive)](https://drive.google.com/file/d/15TcDZuNGD3Cu81OjIz_G94IX02aJqkjK/view?usp=drive_link)
- 🖥️ **Platform:** Windows 10 / 11 (64-bit)

---

### 2. 🐧 `Launch_App.sh` (Linux & macOS Shell Launcher)
- 📌 **Description:** Bash shell script launcher for Linux and macOS environments. Automatically resolves permissions and launches the application or opens the download portal in your browser.
- 📥 **Direct Download:** [🐧 Download Launch_App.sh (Google Drive)](https://drive.google.com/file/d/1r98-Xi5oIY5FQlEpG-3-fmzJGQVb_Eqc/view?usp=drive_link)
- 🖥️ **Platform:** Linux (Ubuntu, Debian, Fedora, etc.) & macOS

---

### 3. 📜 `setup.iss` (Inno Setup Installer Compiler Script)
- 📌 **Description:** Complete Inno Setup compilation script used to generate the standalone Windows installer package (`HyperspectralImaging_setup.exe`).
- 📥 **Direct Download / View:** [📜 Download setup.iss (Google Drive)](https://drive.google.com/file/d/11-p6E9BVMvNhJeK_7jE_t6iDNU0nBjtn/view?usp=drive_link)
- 🛠️ **Tool Required:** Inno Setup Compiler (v6.0 or higher)

---

## 📋 Step-by-Step Usage & Execution Guide

### 🔹 Method 1: Running `Launch_App.bat` on Windows (Start to Finish)

1. 📥 **Step 1: Download / Locate the File**
   - Click the download link above or navigate to [`App/ISS/Launch_App.bat`](./Launch_App.bat) in your local project directory.
2. 📂 **Step 2: Save to Folder**
   - Ensure `Launch_App.bat` is kept inside the repository folder structure so it can locate the executable.
3. 🔓 **Step 3: Unblock File (If Prompted by Windows)**
   - Right-click `Launch_App.bat` $\rightarrow$ Click **Properties**.
   - Check **Unblock** at the bottom $\rightarrow$ Click **Apply** $\rightarrow$ **OK**.
4. ⚡ **Step 4: Execute & Launch**
   - Double-click `Launch_App.bat` or run it from Command Prompt:
     ```cmd
     cd App\ISS
     Launch_App.bat
     ```
   - The script will launch `HyperspectralImaging.exe` or direct you to the Google Drive setup portal.

---

### 🔹 Method 2: Running `Launch_App.sh` on Linux & macOS (Start to Finish)

1. 📥 **Step 1: Download / Locate the File**
   - Download [`Launch_App.sh`](./Launch_App.sh) or open a Terminal in the `App/ISS` directory.
2. 💻 **Step 2: Open Terminal & Navigate**
   - Open your terminal and change directory to `App/ISS`:
     ```bash
     cd App/ISS
     ```
3. 🔑 **Step 3: Grant Executable Permissions**
   - Run the `chmod` command to make the shell script executable:
     ```bash
     chmod +x Launch_App.sh
     ```
4. 🐧 **Step 4: Run the Script**
   - Execute the script:
     ```bash
     ./Launch_App.sh
     ```
   - The script will automatically open your default browser to launch or download the application.

---

### 🔹 Method 3: Compiling Your Own Setup Installer (`setup.iss`)

1. 🛠️ **Step 1: Install Inno Setup Compiler**
   - Download and install [Inno Setup 6](https://jrsoftware.org/isdl.php) on Windows.
2. 📜 **Step 2: Open `setup.iss`**
   - Launch Inno Setup Compiler $\rightarrow$ File $\rightarrow$ Open $\rightarrow$ Select `App/ISS/setup.iss`.
3. ⚙️ **Step 3: Build & Compile**
   - Click **Build** $\rightarrow$ **Compile** (or press `Ctrl + F9`).
   - The compiled installer executable (`HyperspectralImaging_setup.exe`) will be generated inside the output directory.

---

## 🖥️ Environment & Tool Requirements

| Component | Target Platform | Compiler / Interpreter | Purpose |
| :--- | :--- | :--- | :--- |
| `Launch_App.bat` | Windows 10/11 | Windows `cmd.exe` | One-click Windows application launcher |
| `Launch_App.sh` | Linux / macOS | `bash` / `zsh` | Command-line Unix shell launcher |
| `setup.iss` | Windows | Inno Setup 6+ | Compiles setup wizard installer package |

---

## ⚠️ Troubleshooting & Common Fixes

- 🛡️ **"Windows protected your PC" / SmartScreen Alert:**
  - Click **More info** $\rightarrow$ Click **Run anyway**. Batch files trigger SmartScreen on first execution.
- 🔑 **"Permission denied" on Linux/macOS (`Launch_App.sh`):**
  - Run `chmod +x Launch_App.sh` in Terminal before running `./Launch_App.sh`.
- 📁 **File Not Found Errors:**
  - Keep the folder structure (`App/exe/`, `App/ISS/`, `App/Source_Code/`) intact so relative path shortcuts resolve properly.
