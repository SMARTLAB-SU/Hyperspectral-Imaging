# 📊 Hyperspectral & Plant Disease Datasets — User Guide & Setup

Welcome to the **Hyperspectral Imaging System** dataset directory. This guide provides a complete start-to-finish walkthrough on how to access, download, structure, and utilize the three target datasets for training and evaluation.

---

## 🌐 Dataset Overview & Clickable Access Links

| Dataset Name | Category | Description | Kaggle Link |
| :--- | :--- | :--- | :--- |
| 🌿 **Plant Disease Detection** | Raw / Benchmark | ~54,000 multi-spectral crop leaf images across disease conditions | [🔗 Open on Kaggle](https://www.kaggle.com/datasets/vedikapangavhane/plant-disease-detection-kaggle?select=valid) |
| ⚖️ **Balanced Dataset** | Preprocessed | Class-balanced dataset (~2,000 samples/class) mitigating training bias | [🔗 Open on Kaggle](https://www.kaggle.com/datasets/vedikapangavhane/balanced-dataset) |
| ✂️ **Splitted Dataset** | Partitioned | 80:10:10 Train / Validation / Test split ready for model training | [🔗 Open on Kaggle](https://www.kaggle.com/datasets/vedikapangavhane/splitted-dataset) |

---

## 📋 Step-by-Step Dataset Guide (Start to Finish)

### 🔹 Step 1: Choose Your Preferred Download Method

#### Option A: Direct Web Browser Download (Easiest)
1. Click any of the Kaggle dataset links above to open the Kaggle dataset page.
2. Log in to your Kaggle account.
3. Click the **Download (ZIP)** button at the top right of the page.
4. Extract the downloaded `.zip` file into your local `Dataset/` directory.

#### Option B: Programmatic Download via Kaggle CLI
1. Install the Kaggle CLI package:
   ```bash
   pip install kaggle
   ```
2. Place your `kaggle.json` API token into `~/.kaggle/kaggle.json` (or `%USERPROFILE%\.kaggle\kaggle.json` on Windows).
3. Run the download commands:
   ```bash
   # Download Plant Disease Detection Dataset
   kaggle datasets download -d vedikapangavhane/plant-disease-detection-kaggle -p ./Dataset --unzip

   # Download Balanced Dataset
   kaggle datasets download -d vedikapangavhane/balanced-dataset -p ./Dataset --unzip

   # Download Splitted Dataset
   kaggle datasets download -d vedikapangavhane/splitted-dataset -p ./Dataset --unzip
   ```

---

### 🔹 Step 2: Organize the Local Directory Structure

After downloading and extracting, arrange your files in the `Dataset/` folder as follows:

```text
Dataset/
├── Readme.md
├── Report.md
├── Kaggle_Datasets.md
├── plant_disease_detection/
│   ├── train/
│   └── valid/
├── balanced_dataset/
│   └── balanced_classes/
└── splitted_dataset/
    ├── train/
    ├── valid/
    └── test/
```

---

### 🔹 Step 3: Run Model Evaluation & Inference

Once the dataset is in place, you can execute the evaluation pipeline script:

1. Open a terminal or command prompt in the project root directory.
2. Run the inference script pointing to the dataset path:
   ```bash
   python Evaluation/Inference.py ./Dataset ./Output/Output_Images
   ```
3. Processed hyperspectral output maps will be saved in [`Output/Output_Images/`](../Output/Output_Images/).

---

## 🔬 Dataset Specifications Summary

- **Spatial Resolutions:** $256 \times 256$ and $512 \times 512$ pixels.
- **Spectral Bands:** 4 Wavelength Bands (Band 1: 405–435nm, Band 2: 515–555nm, Band 3: 600–650nm, Band 4: Custom).
- **Target Disease Categories:** Healthy, Bacterial Spot, Early Blight, Late Blight, Target Spot, and Leaf Mold.

---

## 📜 Associated Documentation
- 📄 [`Dataset/Report.md`](./Report.md): Detailed evaluation report, calibration formulas, and accuracy benchmarks.
- 📄 [`Dataset/Kaggle_Datasets.md`](./Kaggle_Datasets.md): Quick link reference file for all Kaggle datasets.
