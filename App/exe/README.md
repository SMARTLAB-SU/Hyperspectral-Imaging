# 💻 App / exe — Application Executables & Installation Guide

Welcome to the **Hyperspectral Imaging System** executables directory. This folder contains the compiled Windows application binaries and setup installers.

> [!NOTE]
> Due to GitHub file size limits, the large binary executable files are hosted externally on Google Drive. Use the direct download links below to fetch the files.

---

## 📦 Executable Files & Direct Download Links

### 1. 🚀 `HyperspectralImaging.exe` (Portable Binary)
- 📌 **Description:** Standalone main application executable. Run this file directly to launch the Hyperspectral Imaging System interface instantly without installation.
- 📥 **Direct Download:** [🚀 Download HyperspectralImaging.exe (Google Drive)](https://drive.google.com/file/d/1HoCol66_ExuojPXvfUXJMjDM9vCpZ0zL/view?usp=drive_link)
- ⚡ **Type:** Portable Executable (`.exe`)

---

### 2. ⚙️ `HyperspectralImaging_setup.exe` (Automated Installer)
- 📌 **Description:** Automated installer wizard package built using Inno Setup. Installs the application on your computer, creates Desktop & Start Menu shortcuts, and configures environment paths.
- 📥 **Direct Download:** [⚙️ Download HyperspectralImaging_setup.exe (Google Drive)](https://drive.google.com/file/d/1HoCol66_ExuojPXvfUXJMjDM9vCpZ0zL/view?usp=drive_link)
- ⚡ **Type:** Windows Setup Installer Package (`.exe`)

---

## 📋 Comprehensive Usage & Execution Guide

### 🔹 Option 1: Direct Execution (No Installation Required)

1. 📥 **Download:** Click the link above to open Google Drive and download `HyperspectralImaging.exe`.
2. 📂 **Location:** Save the file to your preferred folder (e.g., `Downloads` or `Desktop`).
3. 🔓 **Security Unblock (If Prompted):**
   - Right-click `HyperspectralImaging.exe` $\rightarrow$ Select **Properties**.
   - Check the **Unblock** checkbox at the bottom of the *General* tab $\rightarrow$ Click **Apply** $\rightarrow$ **OK**.
4. 🚀 **Launch & Run:**
   - Double-click `HyperspectralImaging.exe` to run the application.
   - The GUI will open immediately, ready for spectral camera capture and data processing.

---

### 🔹 Option 2: Full System Installation (Recommended for Desktop Setup)

1. 📥 **Download:** Click the link above to download `HyperspectralImaging_setup.exe`.
2. ⚙️ **Run Installer:** Double-click `HyperspectralImaging_setup.exe` to launch the Inno Setup wizard.
3. 📋 **Follow On-Screen Instructions:**
   - Select installation destination folder (default: `C:\Program Files\HyperspectralImaging`).
   - Check options to create **Desktop Shortcut** and **Start Menu Shortcut**.
   - Click **Install** $\rightarrow$ Wait for installation to complete $\rightarrow$ Click **Finish**.
4. 🖥️ **Launch Application:**
   - Double-click the **Hyperspectral Imaging System** desktop shortcut or open it from the Windows Start Menu.

---

## 🖥️ System Requirements

| Specification | Minimum Requirement | Recommended Requirement |
| :--- | :--- | :--- |
| **Operating System** | Windows 10 (64-bit) | Windows 11 (64-bit) |
| **RAM** | 8 GB | 16 GB or higher |
| **Display Resolution** | 1280 × 720 | 1920 × 1080 (Full HD) |
| **Processor** | Intel Core i5 / AMD Ryzen 5 | Intel Core i7 / AMD Ryzen 7 |
| **Hardware Devices** | USB 3.0 Port for Spectral Camera | USB 3.0 / 3.1 High-Speed Port |

---

## ⚠️ Important Troubleshooting & Security Notes

- 🛡️ **Windows Defender / SmartScreen Alert:**
  - If Windows shows a *"Windows protected your PC"* popup:
    1. Click **More info**.
    2. Click **Run anyway**.
  - *Reason:* Unsigned executable binaries trigger SmartScreen warnings on first run.

- 🐍 **Python Environment & Dependencies:**
  - Standard PyInstaller binaries are fully self-contained with bundled Python dependencies.
  - If running via source code instead, refer to the [`Source_Code/`](../Source_Code/) directory and run `pip install -r requirements.txt`.

- 📜 **Installer Scripts:**
  - The Inno Setup script (`setup.iss`) used to generate the setup installer is available in the [`ISS/`](../ISS/) folder.
