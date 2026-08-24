# Hyperspectral Imaging System - User Manual

This manual provides detailed instructions on how to set up, operate, and configure the **Hyperspectral Imaging System** desktop application.

---

## 1. System Overview
The Hyperspectral Imaging System reconstructs high-dimensional hyperspectral bands from a standard RGB camera sensor in real-time. It applies color reproduction algorithms to highlight specific wavelengths of light, making it suitable for diagnostic visualization (e.g., biological tissue analysis).

---

## 2. Quick Start & Launching

### On Windows
1. Double-click `HyperspectralImaging.exe` or run `Launch_App.bat`.
2. A desktop shortcut named **Hyperspectral Imaging System** will be automatically created on your Desktop for subsequent launches.

### On Raspberry Pi / Linux
1. Open a terminal in the application folder.
2. Install the necessary dependencies if running for the first time:
   ```bash
   sudo apt update
   sudo apt install -y python3-pyqt6 python3-opencv python3-numpy python3-pandas python3-matplotlib python3-sklearn
   ```
3. Give execution permissions to the launcher script:
   ```bash
   chmod +x Launch_App.sh
   ```
4. Double-click `Launch_App.sh` and select **Execute**, or run it from the terminal:
   ```bash
   ./Launch_App.sh
   ```
   *Note: This script automatically creates a **Hyperspectral Imaging** shortcut launcher on your Raspberry Pi desktop.*

---

## 3. User Interface Layout

The interface is divided into two primary sections: the **Left Control Panel** (Configuration) and the **Right Display Panel** (Visualization & Actions).

```
 _______________________________________________________________________________
|  [LOGO]                   |                                                   |
|                           |                  VISUALIZATION                    |
|  GAIN SETTINGS            |                     CANVAS                        |
|  [Slider] [Text Input]    |            (Live Feed or Split-Screen)            |
|                           |                                                   |
|  BAND SETTINGS            |___________________________________________________|
|  Band 1 Min/Max (▲/▼)     |   THUMBNAILS (For Upload Mode)                    |
|  Band 2 Min/Max (▲/▼)     |  [Img 1] [Img 2] [Img 3]                          |
|  Band 3 Min/Max (▲/▼)     |___________________________________________________|
|  Band 4 Min/Max (▲/▼)     |   CONTROLS                                        |
|  [Clear Bands]            |  [Photo/Video] [Upload] [Resume] [Capture/Record] |
|                           |                                                   |
|  SAMPLE SETTINGS          |  STATUS: System Ready                             |
|  Sample No: [ 1 ]         |___________________________________________________|
```

### A. Left Control Panel
*   **Gain Settings:** 
    *   Adjusts the multiplication gain factor of the hyperspectral projection (from `1.0x` to `50.0x`).
    *   Move the slider or type the value manually in the text box (e.g., `2.5x`) to change the brightness of the processed spectral bands.
*   **Band Settings:**
    *   Configure up to 4 spectral band filters (Min/Max ranges from `380nm` to `780nm`).
    *   Click the **▲** and **▼** arrows to fine-tune the wavelength bounds, or type values directly.
    *   Click **Clear Bands** to view the raw RGB input.
*   **Sample Settings:**
    *   Input the **Sample No.** (e.g. `1`, `2`, `104B`). This number is used to automatically name the folder where data is saved.

### B. Right Display Panel
*   **Visualization Canvas:** 
    *   Displays the real-time live feed from the camera.
    *   Switches automatically to a side-by-side **Split View** (Original vs. Processed) when an image is captured, uploaded, or during video replay.
*   **Thumbnail Strip:**
    *   Appears only in **Upload Mode**. Allows you to cycle through multiple uploaded images by clicking their thumbnail.
*   **Bottom Action Bar:**
    *   **Photo/Video Mode Buttons:** Toggles the operational mode of the system.
    *   **Upload Image:** Select offline image files (`.png`, `.jpg`, `.jpeg`) to process them.
    *   **Resume Live:** Closes static captures/replays and returns to the real-time camera stream.
    *   **Capture / Record:** Captures a high-resolution snapshot or begins recording processed frames.
    *   **Save:** Manually saves currently frozen images or batch processes.

---

## 4. Operation Guide

### A. Live Streaming & Real-time Analysis
1. Turn on the camera. The app will search for active cameras and load the stream.
2. If no camera is connected, the app runs in **Simulation Mode** (a moving mockup of tissue cells).
3. Adjust the **Gain** and **Band Ranges** on the left. The live processed canvas updates dynamically.

### B. Photo Mode (Capturing & Exporting)
1. Ensure the mode toggle is set to **Photo**.
2. Click **Capture**.
3. The camera pauses, and the display switches to a split view of the **Original** and **Processed** image.
4. An auto-save folder is generated. A dialog box pops up saying:
   *   **OK:** Keeps the files in the default directory (`Desktop/HyperspectralImaging_Data`).
   *   **Save to Custom Location:** Prompts you to pick another folder (e.g. a USB flash drive) to copy the session results.
5. Click **Resume Live** to start streaming again.

### C. Video Mode (Recording & Replay)
1. Click the **Video** mode button.
2. Click **Record**. The status bar displays `"Recording video..."`.
3. Click **Stop** to finish recording. The camera pauses.
4. The system automatically launches a **Video Replay Loop** showing a split-screen preview of the recorded original and processed videos.
5. Click **Save** to permanently save the videos.
6. Click **Resume Live** to restart the camera.

### D. Offline Upload Mode
1. Click **Upload Image**. The live feed will pause.
2. Select one or more images from your local drive.
3. Click the thumbnail of any image in the strip to load it. 
4. Adjust the **Gain** and **Band Settings** to run the processing algorithm on the static image.
5. Click **Save** to write the original and processed images to a session folder.
6. Click **Resume Live** to return to the live camera feed.

---

## 5. Saved Data Structure

Saved data is organized inside the `HyperspectralImaging_Data` folder (located on your Desktop). Inside, a new directory is created for each capture session:

`HyperspectralImaging_Data/sample[SampleNo]_[YYYYMMDD_HHMMSS]/`

### Exported Files:
*   **For Photos:**
    *   `original.png` (Raw RGB capture)
    *   `processed.png` (Spectral reconstructed image)
*   **For Videos:**
    *   `original_video.avi` (Raw recorded video)
    *   `processed_video.avi` (Hyperspectral processed video)
*   **For Uploaded Images:**
    *   `original_1.png`, `processed_1.png`... (Batch results)

---

## 6. Troubleshooting & Warnings

*   **Low Output Warning:** If you set a band range in the UV/Blue border (`320nm - 420nm`), the status bar will warn you: `Band range 320-420nm may produce low output — try 420nm and above`.
*   **Missing weight.npz / cr_weights:** The application checks for these mathematical calibration files on startup. If you see a warning dialog, make sure these files are located inside the folder with the application executable.
*   **Camera Connection Issues:** If the camera feed fails to load, verify that:
    1. The camera is plugged in securely.
    2. No other program is currently using the camera.
    3. On Raspberry Pi, make sure you ran the script via `./Launch_App.sh`.
