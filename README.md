# Hyperspectral Imaging System (HSI)

A comprehensive Python and PyQt6-based desktop application for real-time hyperspectral image acquisition, processing, visualization, and spectral analysis.

---

## 🌟 Key Features

- **Real-Time Camera Acquisition**: Live stream video feed with native camera support.
- **Hyperspectral Processing**: Spectral reflectance extraction, index computation, and image processing pipeline.
- **Desktop User Interface**: Modern PyQt6 GUI with interactive controls, visualization graphs, and custom dataset reporting.
- **Model Inference & Evaluation**: Spectral analysis tools for classification and feature extraction.

---

## 📁 Repository Structure

```
.
├── App/
│   ├── ISS/                   # Inno Setup installer scripts
│   └── Source Code/
│       ├── Additional Files/  # Assets, weights, and launch scripts
│       └── Py/                # Desktop application source code & UI
├── DataSet/                   # Datasets and dataset reports
├── Documentation/             # Comprehensive documentation and presentations
├── Evaluation/                # Inference and model evaluation tools
├── Outputs/                   # Output predictions and spectral maps
├── shared/                    # Shared processing libraries
├── requirements.txt           # Python dependencies
└── README.md                  # Project overview
```

---

## 🛠️ Dependencies

- **PyQt6**: Desktop GUI framework
- **OpenCV (`opencv-python`)**: Frame capture & image processing
- **NumPy**: High-performance array and spectral data matrix manipulation
- **Pandas**: Data structuring & export
- **Matplotlib**: Spectral curve plotting & visualization
- **Scikit-learn**: Machine learning model evaluation & processing

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/vedikapangavhane2007/HSI.git
cd HSI
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run the Desktop Application
```bash
python "App/Source Code/Py/desktop_app/main.py"
```

---

## 📄 License

Maintained by [@vedikapangavhane2007](https://github.com/vedikapangavhane2007).
