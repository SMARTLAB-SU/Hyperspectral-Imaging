# Hyperspectral Imaging

Repository: [SMARTLAB-SU/Hyperspectral-Imaging](https://github.com/SMARTLAB-SU/Hyperspectral-Imaging)

## 📊 Kaggle Datasets

- 🌿 **[Plant Disease Detection Kaggle Dataset](https://www.kaggle.com/datasets/vedikapangavhane/plant-disease-detection-kaggle?select=valid)**
- ⚖️ **[Balanced Dataset](https://www.kaggle.com/datasets/vedikapangavhane/balanced-dataset)**
- ✂️ **[Splitted Dataset](https://www.kaggle.com/datasets/vedikapangavhane/splitted-dataset)**

## 📥 Download & Launch Guide

- 🔗 **[Click Here to Download & Run Launch_App.bat (Google Drive)](https://drive.google.com/file/d/15TcDZuNGD3Cu81OjIz_G94IX02aJqkjK/view?usp=drive_link)**
- 🔗 **[Click Here to Download & Run Launch_App.sh (Google Drive)](https://drive.google.com/file/d/1r98-Xi5oIY5FQlEpG-3-fmzJGQVb_Eqc/view?usp=drive_link)**
- 🔗 **[Click Here to Download & Run HyperspectralImaging.exe (Google Drive)](https://drive.google.com/file/d/1HoCol66_ExuojPXvfUXJMjDM9vCpZ0zL/view?usp=drive_link)**
- 🔗 **[Click Here to Download & Run HyperspectralImaging_Setup.exe (Google Drive)](https://drive.google.com/file/d/1HoCol66_ExuojPXvfUXJMjDM9vCpZ0zL/view?usp=drive_link)**
- 📄 **[setup.iss Download Guide](./App/ISS/Download_Setup_Iss_Link.md)**
- 📄 **[Launch_App.bat Download Guide](./App/ISS/Download_Launch_Bat_Link.md)**
- 📄 **[Launch_App.sh Download Guide](./App/ISS/Download_Launch_Sh_Link.md)**
- 📄 **[App Executable Readme](./App/exe/README.md)**
- ⚡ **[Launch Instructions (BAT & SH)](./App/ISS/Launch_App_Instructions.md)**

---

## Repository Structure

```
Hyperspectral-Imaging/
│
├── Dataset/
│   ├── Readme.md
│   ├── Report.md
│   └── Kaggle_Datasets.md
│
├── App/
│   ├── exe/
│   │   ├── HyperspectralImaging.exe
│   │   ├── HyperspectralImaging_Setup.exe
│   │   ├── README.md
│   │   ├── Download_Setup_Link.md
│   │   └── Download_App_Link.md
│   ├── ISS/
│   │   ├── setup.iss
│   │   ├── README.md
│   │   ├── Download_Launch_Sh_Link.md
│   │   ├── Download_Launch_Bat_Link.md
│   │   └── Download_Setup_Iss_Link.md
│   └── Source_Code/
│       ├── Py/
│       │   ├── desktop_app/
│       │   └── processor.py
│       └── Additional_Files/
│           ├── sanjivani.ico
│           ├── sanjivani.png
│           ├── weight.npz
│           ├── cr_weights/
│           └── HyperspectralImaging.spec
│
├── Output/
│   ├── Output_Images/
│   ├── HyperspectralImaging_Data/
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
