# Hyperspectral Imaging

Repository: [SMARTLAB-SU/Hyperspectral-Imaging](https://github.com/SMARTLAB-SU/Hyperspectral-Imaging)

## 📥 Download Setup Executable
Download the latest installer for the Hyperspectral Imaging Application:
- 🔗 **[Download HyperspectralImaging_Setup.exe (Google Drive)](https://drive.google.com/file/d/18CjDtK030_QoAcgeAt0OfehtbsZY7lui/view?usp=drive_link)**

---

## Repository Structure

```
Hyperspectral-Imaging/
│
├── Dataset/
│   ├── Readme.md
│   └── Report.md
│
├── App/
│   ├── exe/
│   │   ├── HyperspectralImaging.exe
│   │   ├── HyperspectralImaging_Setup.exe
│   │   ├── README.md
│   │   └── Download_Setup_Link.md
│   ├── ISS/
│   │   └── setup.iss
│   └── Source_Code/
│       ├── Py/
│       │   ├── desktop_app/
│       │   └── processor.py
│       └── Additional_Files/
│           ├── sanjivani.ico
│           ├── sanjivani.png
│           ├── weight.npz
│           ├── cr_weights/
│           ├── Launch_App.bat
│           ├── Launch_App.sh
│           ├── HyperspectralImaging.spec
│           └── HyperspectralImaging_Data/
│
├── Output/
│   ├── Output_Images/
│   └── Readme.md
│
├── Evaluation/
│   └── Inference.py
│
├── requirements.txt
├── README.md
├── LICENSE.md
│
└── Documentation/
    ├── Comprehensive_Doc.md
    └── Presentation.pptx
```

## Overview
This repository provides desktop application software, evaluation pipelines, datasets, and comprehensive documentation for Hyperspectral Imaging processing and visualization.

## Getting Started
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application or evaluation script:
   ```bash
   python Evaluation/Inference.py
   ```
