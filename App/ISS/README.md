# ⚙️ App / ISS — Installer Scripts & Setup Guide

Welcome to the **Hyperspectral Imaging System** installer script directory. This folder contains the Inno Setup build configuration (`setup.iss`) used to generate the Windows application setup installer.

---

## 📦 Directory Contents & Direct Download Links

### 1. 📜 `setup.iss` (Inno Setup Installer Compiler Script)
- 📌 **Description:** Complete Inno Setup compilation script used to generate the standalone Windows installer package (`HyperspectralImaging_setup.exe`).
- 📥 **Direct Download / View:** [📜 Download setup.iss (Google Drive)](https://drive.google.com/file/d/11-p6E9BVMvNhJeK_7jE_t6iDNU0nBjtn/view?usp=drive_link)
- 🛠️ **Tool Required:** Inno Setup Compiler (v6.0 or higher)

---

## 📋 Step-by-Step Compilation Guide (`setup.iss`)

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
| `setup.iss` | Windows 10/11 | Inno Setup 6+ | Compiles setup wizard installer package |

---

## ⚠️ Notes & References
- For compiled executable binaries, visit the [`App/exe/`](../exe/) directory.
- For source code, visit the [`App/Source_Code/`](../Source_Code/) directory.
