# 📸 Output Directory — Results, Visualizations & Data Samples

Welcome to the **Hyperspectral Imaging System** output directory. This folder stores generated hyperspectral images, classification maps, pseudo-color spectral renders, and captured sample session data (`HyperspectralImaging_Data`).

---

## 🖼️ Sample System Interface Output

![Hyperspectral System Output Preview](./Output_Images/Hyperspectral_System_Output.png)

*Figure 1: Hyperspectral Imaging System GUI showing live camera capture (left: Original spatial image, right: Processed pseudo-color spectral reflectance band overlay at 2.5x gain).*

---

## 📂 Folder Breakdown & Contents

### 1. 📁 `Output_Images/`
Contains processed output images, spectral reflectance maps, disease detection classification masks, and GUI screenshot captures.
- **`Hyperspectral_System_Output.png`**: High-resolution GUI capture showing real-time original vs multi-spectral processed tissue imagery.

### 2. 📁 `HyperspectralImaging_Data/`
Contains raw and calibrated sample session datasets recorded during live imaging runs.
- **`sample1_20260731_113044/`**: Sample 1 session containing `original.png` and `processed.png`.
- **`sample1_20260804_132726/`**: Sample 2 session containing calibrated reflectance frames.
- **`sample1_20260804_132821/`**: Video capture session containing `original_video.avi` and `processed_video.avi`.

---

## 📋 Comprehensive Usage & Workflow Guide (Start to Finish)

### 🔹 Step 1: Generate Output via Desktop Application (GUI)

1. Launch the application:
   - Double-click [`App/exe/HyperspectralImaging.exe`](../App/exe/HyperspectralImaging.exe) or run [`App/ISS/Launch_App.bat`](../App/ISS/Launch_App.bat).
2. Adjust band sliders (Band 1: 405–435nm, Band 2: 515–555nm, Band 3: 600–650nm) and Gain settings.
3. Click **Capture** or **Save**.
4. The application automatically exports original images, processed pseudo-color spectral overlays, and video captures into `Output/HyperspectralImaging_Data/`.

---

### 🔹 Step 2: Generate Output via Evaluation Pipeline (CLI)

You can also run batch processing and evaluation via command line:

1. Open terminal in the project root directory.
2. Run the inference script:
   ```bash
   python Evaluation/Inference.py ./Dataset ./Output/Output_Images
   ```
3. Processed disease classification maps and reflectance spectra plots will be generated inside [`Output/Output_Images/`](./Output_Images/).

---

### 🔹 Step 3: View & Interpret Output Files

- 🖼️ **`original.png` / `original_video.avi`**: Unprocessed standard RGB spatial input.
- 🌈 **`processed.png` / `processed_video.avi`**: Calibrated multi-spectral composite highlighting absorption peaks (e.g., chlorophyll, hemoglobin, or pathological tissue changes).
- 📊 **CSV & Log Outputs**: Wavelength reflectance intensity metrics used for quantitative reporting.

---

## 🖥️ Output File Formats & Technical Specs

| Output File Type | Format | Resolution | Description |
| :--- | :--- | :--- | :--- |
| **Spectral Render** | `.png` / `.tiff` | $512 \times 512$ / $1080p$ | Multi-band pseudo-color false-spectrum overlay |
| **Video Stream** | `.avi` / `.mp4` | 30 FPS | Real-time band-filtered spectral video feed |
| **GUI Screenshots** | `.png` | $1920 \times 1080$ | High-resolution interface state capture |
