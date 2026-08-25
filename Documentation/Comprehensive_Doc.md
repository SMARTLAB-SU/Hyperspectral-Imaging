# 📚 Spectrum-Aided Vision Enhancer (SAVE) & Hyperspectral Imaging System — Comprehensive Documentation

This document provides a comprehensive technical, mathematical, and operational guide for the **Spectrum-Aided Vision Enhancer (SAVE)** and **Hyperspectral Imaging System**. It covers the theoretical foundation, spectral reconstruction algorithm, color calibration matrices, narrow-band imaging (NBI) simulation, quantitative performance evaluation (SSIM, PSNR, Entropy), and the complete desktop application user manual.

---

# PART I: MATHEMATICAL & THEORETICAL FOUNDATION (SAVE ALGORITHM)

## 1. Overview of Spectrum-Aided Vision Enhancer (SAVE)
The **Spectrum-Aided Vision Enhancer (SAVE)** algorithm transforms a standard White-Light Image (WLI) captured from an RGB camera or endoscope into:
1. A reconstructed **Hyperspectral Image (HSI)** across wavelengths from **380 nm to 780 nm** (1 nm spectral resolution).
2. A simulated **Narrow Band Imaging (NBI)** image (similar to Olympus NBI and Video Capsule Endoscopy - VCE).

---

## 2. sRGB to CIE 1931 XYZ Color Space Conversion

### 2.1 Gamma Linearization
Raw sRGB pixel channel values ($R_{\text{sRGB}}, G_{\text{sRGB}}, B_{\text{sRGB}} \in [0, 255]$) are normalized to $[0, 1]$ and linearized using the inverse gamma function:

$$f(n) = \begin{cases} \left( \frac{n + 0.055}{1.055} \right)^{2.4}, & n > 0.04045 \\ \frac{n}{12.92}, & n \le 0.04045 \end{cases} \tag{4}$$

### 2.2 Tristimulus Transformation
Linearized sRGB values are converted to CIE 1931 XYZ tristimulus values ($XYZ_{\text{camera}}$):

$$\begin{bmatrix} X \\ Y \\ Z \end{bmatrix} = [M_A] [T] \begin{bmatrix} f(R_{\text{sRGB}}) \\ f(G_{\text{sRGB}}) \\ f(B_{\text{sRGB}}) \end{bmatrix} \times 100, \quad 0 \le R_{\text{sRGB}}, G_{\text{sRGB}}, B_{\text{sRGB}} \le 1 \tag{1}$$

where the transformation matrix $[T]$ is:

$$[T] = \begin{bmatrix} 0.4104 & 0.3576 & 0.1805 \\ 0.2126 & 0.7152 & 0.0722 \\ 0.0193 & 0.1192 & 0.9505 \end{bmatrix} \tag{2}$$

and the adaptation matrix $[M_A]$ accounts for reference white balance calibration:

$$[M_A] = \begin{bmatrix} X_{SW} / X_{CW} & 0 & 0 \\ 0 & Y_{SW} / Y_{CW} & 0 \\ 0 & 0 & Z_{SW} / Z_{CW} \end{bmatrix} \tag{3}$$

---

## 3. Spectrophotometer Integration & Spectral XYZ Conversion

Given the light source spectrum $S(\lambda)$ and CIE color matching functions $\bar{x}(\lambda), \bar{y}(\lambda), \bar{z}(\lambda)$ across wavelengths $\lambda \in [400\text{nm}, 700\text{nm}]$:

$$X = k \int_{400\text{nm}}^{700\text{nm}} S(\lambda) R(\lambda) \bar{x}(\lambda) d\lambda \tag{5}$$

$$Y = k \int_{400\text{nm}}^{700\text{nm}} S(\lambda) R(\lambda) \bar{y}(\lambda) d\lambda \tag{6}$$

$$Z = k \int_{400\text{nm}}^{700\text{nm}} S(\lambda) R(\lambda) \bar{z}(\lambda) d\lambda \tag{7}$$

where the normalization factor $k$ is defined as:

$$k = \frac{100}{\int_{400\text{nm}}^{700\text{nm}} S(\lambda) \bar{y}(\lambda) d\lambda} \tag{8}$$

---

## 4. Color Correlation & Error Correction

To correlate spectrophotometer spectral values ($XYZ_{\text{Spectrum}}$) with camera values ($V$):

$$[C] = [XYZ_{\text{Spectrum}}] \times \text{pinv}([V]) \tag{9}$$

$$[XYZ_{\text{Correct}}] = [C] \times [V] \tag{10}$$

### 4.1 Non-Linearity & Dark Current Modification
To account for non-linear response, dark current noise, and color distortion:

$$V_{\text{Non-linear}} = \begin{bmatrix} X^3 & Y^3 & Z^3 & X^2 & Y^2 & Z^2 & X & Y & Z & 1 \end{bmatrix}^T \tag{11}$$

$$V_{\text{Dark}} = [a] \tag{12}$$

$$V_{\text{Color}} = \begin{bmatrix} XYZ & XY & XZ & YZ & X & Y & Z \end{bmatrix}^T \tag{13}$$

$$V = \begin{bmatrix} X^3 & Y^3 & Z^3 \\ X^2 Y & X^2 Z & Y^2 Z \\ X Y^2 & X Z^2 & Y Z^2 \\ X Y Z & X^2 & Y^2 & Z^2 \\ X Y & X Z & Y Z & X & Y & Z & a \end{bmatrix}^T \tag{14}$$

---

## 5. CIE Lab & CIEDE 2000 Color Difference Metrics

$XYZ_{\text{Correct}}$ values are transformed to CIE $L^*a^*b^*$ color space:

$$L^* = 116 f\left(\frac{Y}{Y_n}\right) - 16 \tag{15}$$

$$a^* = 500 \left[ f\left(\frac{X}{X_n}\right) - f\left(\frac{Y}{Y_n}\right) \right]$$

$$b^* = 200 \left[ f\left(\frac{Y}{Y_n}\right) - f\left(\frac{Z}{Z_n}\right) \right]$$

where:

$$f(n) = \begin{cases} n^{1/3}, & n > 0.008856 \\ 7.787 n + 0.137931, & \text{otherwise} \end{cases} \tag{16}$$

---

## 6. Principal Component Analysis (PCA) & Spectral Reconstruction

1. The reflectance matrix $(R(\lambda))_{401 \times 24}$ is constructed for 24 Macbeth Color Checker blocks across 401 wavelengths ($380\text{nm} - 780\text{nm}$).
2. Eigenvector basis matrix $(E)_{12 \times 401}$ is derived using PCA.
3. The 6 most significant principal components account for **99.64% of total variance**.
4. Corresponding eigenvalues matrix $[\alpha]_{12 \times 24}$ is computed via:

$$[\alpha]^T = [R(\lambda)]^T \text{pinv}([E]) \tag{17}$$

5. The transformation matrix $[M]$ is derived via multivariate regression:

$$[M] = [\text{Score}] \times \text{pinv}([V_{\text{Color}}]) \tag{18}$$

6. Reconstructed analog hyperspectral spectrum $[S_{\text{Spectrum}}]_{380-780\text{nm}}$ is synthesized via:

$$[S_{\text{Spectrum}}]_{380-780\text{nm}} = [EV] [M] [V_{\text{Color}}] \tag{19}$$

---

## 7. Narrow Band Imaging (NBI) & VCE Spectrum Calibration

NBI enhances diagnostic mucosal detail using specific light absorption wavelengths:
- **Blue Band (415 nm):** Peak hemoglobin light absorption for superficial mucosal capillary networks.
- **Green Band (540 nm):** Submucosal blood vessel visualization.
- Additional spectrum bands at **600 nm, 700 nm, and 780 nm**.

Lighting spectrum optimization between Olympus NBI and Video Capsule Endoscopy (VCE) utilizes the Cauchy-Lorentz visiting distribution:

$$f(x; x_0, \gamma) = \frac{1}{\pi \gamma \left[ 1 + \left(\frac{x - x_0}{\gamma}\right)^2 \right]} = \frac{1}{\pi} \left[ \frac{\gamma}{(x - x_0)^2 + \gamma^2} \right] \tag{20}$$

---

## 8. Quantitative Evaluation Metrics & Benchmark Performance

| Evaluation Metric | Olympus Endoscope | Video Capsule Endoscopy (VCE) | Significance |
| :--- | :--- | :--- | :--- |
| **SSIM (Structural Similarity)** | **93.992%** (Peak: 94.88%) | **90.680%** (Peak: 96.65%) | High structural accuracy of reconstructed NBI imagery |
| **PSNR (Peak Signal-to-Noise)** | **27.675 dB** (Peak: 28.02 dB) | **27.931 dB** (Peak: 28.51 dB) | High fidelity & low signal distortion |
| **Entropy Difference** | **0.37%** (0.03% baseline) | **1.17%** | Minimal texture disorder and preserved spatial information |
| **Mean Color Error (RMSE)** | **0.056** | **0.056** | Negligible chromatic disparity across 24 color blocks |
| **Chromatic Aberration Error** | **0.63** (reduced from 10.76) | **0.63** | 94% reduction in chromatic aberration after calibration |

### Major Advantages of SAVE Modality:
- 🌟 **Enhanced Image Contrast** for micro-vascular inspection.
- 🎯 **Accurate Pathological Diagnoses** without physical optical filter changes.
- 🩺 **Early Pathological Detection** of early-stage lesions.
- 💉 **Reduced Invasive Procedures**.
- ⏱️ **Time-Efficient Diagnosis**.

---

# PART II: SYSTEM OPERATIONAL USER MANUAL

## 9. System Setup & Installation

### On Windows
1. Double-click `HyperspectralImaging.exe` in `App/exe/` or run `App/ISS/Launch_App.bat`.

### On Linux / Raspberry Pi
1. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install -y python3-pyqt6 python3-opencv python3-numpy python3-pandas python3-matplotlib python3-sklearn
   ```
2. Run launcher:
   ```bash
   chmod +x App/ISS/Launch_App.sh
   ./App/ISS/Launch_App.sh
   ```

---

## 10. User Interface Layout & Controls

```text
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

### Controls Summary:
- **Gain Settings (1.0x - 50.0x):** Controls multiplication gain factor of spectral projection.
- **Band Settings (380nm - 780nm):** Min/Max wavelength bounds for 4 spectral filters.
- **Sample Settings:** Auto-names session directory inside `HyperspectralImaging_Data`.
- **Photo / Video / Upload Modes:** Switches live capture, recording replay, or static image batch processing.

---

## 11. Saved Data Structure

Exported output sessions are saved into `Output/HyperspectralImaging_Data/`:

```text
Output/HyperspectralImaging_Data/sample[SampleNo]_[YYYYMMDD_HHMMSS]/
├── original.png            # Raw RGB spatial image
├── processed.png           # Reconstructed hyperspectral image
├── original_video.avi      # Raw recorded video stream
└── processed_video.avi     # Reconstructed spectral video stream
```
