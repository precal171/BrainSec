# BrainSec Program Outputs Documentation

## Overview

The BrainSec pipeline performs **automated grey and white matter segmentation** and **amyloid-β (Aβ) plaque detection** in digitized human brain tissue Whole Slide Images (WSI). The pipeline consists of three main stages, each producing specific outputs.

---

## Pipeline Stages and Outputs

### Stage 1: Preprocessing (`1_preprocessing.py` / `1_preprocessing_czi.py`)

**Purpose:** Color normalization and WSI tiling

**Input:**
- `.svs` files (whole slide images) or `.czi` files
- Reference image for color normalization (first image in directory)

**Outputs:**

#### 1.1 Tiled Image Patches
- **Location:** `{save_dir}/{wsi_name}/0/{row}/{col}.jpg`
- **Format:** JPG images
- **Size:** 1536 × 1536 pixels per tile
- **Description:** The WSI is divided into a grid of tiles for processing
- **Naming:** Organized by row/column coordinates

#### 1.2 Color Normalization Statistics (Optional)
- **Location:** `{save_dir}/stats.csv`
- **Format:** CSV file
- **Content:** Mean and standard deviation statistics for color normalization
- **Columns:**
  - `means` - Color channel mean values
  - `stds` - Color channel standard deviation values
- **Generated when:** `--normalize True` flag is used

**Example Directory Structure:**
```
data/norm_tiles/
├── Sample001/
│   └── 0/
│       ├── 0/
│       │   ├── 0.jpg
│       │   ├── 1.jpg
│       │   └── ...
│       ├── 1/
│       │   ├── 0.jpg
│       │   └── ...
│       └── ...
└── stats.csv
```

---

### Stage 2: Inference (`2_inference.py` / `2_inference_czi.py`)

**Purpose:** Deep learning inference for brain tissue segmentation and plaque detection

**Models Used:**
- **Segmentation Model:** Classifies pixels into Background (0), White Matter (1), Grey Matter (2)
- **Plaque Detection Model:** Detects three types of plaques (cored, diffuse, CAA)

**Outputs:**

#### 2.1 Brain Segmentation - NumPy Arrays
- **Location:** `{save_np_dir}/{wsi_name}.npy`
- **Format:** NumPy binary file (.npy)
- **Data Type:** `uint8`
- **Shape:** (height, width)
- **Values:**
  - `0` = Background (black)
  - `1` = White Matter (WM)
  - `2` = Grey Matter (GM)
- **Description:** Raw segmentation mask from the neural network

#### 2.2 Brain Segmentation - Visualization Images
- **Location:** `{save_img_dir}/{wsi_name}.png`
- **Format:** PNG image (RGB)
- **Size:** Full WSI resolution
- **Color Coding:**
  - **Black (0,0,0)** = Background
  - **Yellow (255,255,0)** = White Matter (WM)
  - **Cyan (0,255,255)** = Grey Matter (GM)
- **Description:** Human-readable visualization of segmentation

#### 2.3 Plaque Detection - Confidence Heatmaps
- **Location:** `{save_plaq_dir}/{wsi_name}.npy`
- **Format:** NumPy binary file (.npy)
- **Data Type:** `float32`
- **Shape:** (3, height, width)
- **Channels:**
  - Channel 0: Cored plaques confidence [0.0-1.0]
  - Channel 1: Diffuse plaques confidence [0.0-1.0]
  - Channel 2: CAA (Cerebral Amyloid Angiopathy) confidence [0.0-1.0]
- **Description:** Pixel-level confidence scores for each plaque type

**Example Directory Structure:**
```
data/
├── brainseg/
│   ├── images/
│   │   ├── Sample001.png    # Colored segmentation visualization
│   │   └── Sample002.png
│   └── numpy/
│       ├── Sample001.npy    # Segmentation mask {0,1,2}
│       └── Sample002.npy
└── outputs/
    └── heatmaps/
        ├── Sample001.npy    # Plaque confidence [0,1]
        └── Sample002.npy
```

---

### Stage 3: Post-processing (`3_postprocessing.py`)

**Purpose:** Refine segmentation masks, count plaques by region, and generate quantitative results

**Outputs:**

#### 3.1 Post-processed Brain Segmentation - NumPy Arrays
- **Location:** `{data_dir}/postprocess/numpy/{wsi_name}.npy`
- **Format:** NumPy binary file (.npy)
- **Data Type:** `uint8`
- **Shape:** (height, width)
- **Values:** 0 (Background), 1 (WM), 2 (GM)
- **Description:** Cleaned segmentation after morphological operations
- **Post-processing Applied (method_6):**
  - Downsampling (4x)
  - Area opening (removes small false positives)
  - GM/WM swap and area opening (bilateral smoothing)
  - Area closing (fills small holes)
  - Morphological opening (smooths boundaries)
  - Upsampling back to original resolution

#### 3.2 Post-processed Brain Segmentation - Visualization Images
- **Location:** `{data_dir}/postprocess/images/{wsi_name}.png`
- **Format:** PNG image (RGB)
- **Color Coding:** Same as Stage 2.2
  - **Black** = Background
  - **Yellow** = White Matter
  - **Cyan** = Grey Matter
- **Description:** Cleaned, human-readable segmentation

#### 3.3 Plaque Detection Masks - NumPy Arrays (by Type and WSI)
- **Location:** `{data_dir}/outputs/masked_plaque/numpy/{wsi_name}_{plaque_type}.npy`
- **Plaque Types:**
  - `{wsi_name}_cored.npy` - Cored plaques
  - `{wsi_name}_diffuse.npy` - Diffuse plaques
  - `{wsi_name}_caa.npy` - CAA plaques
- **Format:** NumPy binary file (.npy)
- **Data Type:** `uint16`
- **Shape:** (height, width)
- **Values:** Unique label ID for each detected plaque (0 = background)
- **Description:** Each plaque has a unique integer label for tracking

#### 3.4 Plaque Detection - Colored Visualization Images
- **Location:** `{data_dir}/outputs/masked_plaque/images/{wsi_name}_{plaque_type}.png`
- **Plaque Types:**
  - `{wsi_name}_cored.png`
  - `{wsi_name}_diffuse.png`
  - `{wsi_name}_caa.png`
- **Format:** PNG image (RGB)
- **Size:** Full WSI resolution
- **Color Coding:** HSV-based unique colors for each plaque
  - Each plaque gets a unique color based on its label
  - More color diversity indicates higher plaque density
- **Description:** Visual representation where different colors = different plaques

#### 3.5 Plaque Quantification CSV - Main Results File ⭐
- **Location:** `{data_dir}/outputs/CNNscore/CNN_vs_CERAD.csv`
- **Format:** CSV (Comma-Separated Values)
- **Description:** **Primary quantitative output** with plaque counts per WSI and region

**CSV Columns:**

| Column Name | Description |
|------------|-------------|
| `WSI_ID` | Whole Slide Image identifier/filename |
| **Cored Plaques:** | |
| `CNN_cored_count` | Total number of cored plaques detected |
| `BG_cored_count` | Cored plaques in background (tissue artifacts) |
| `WM_cored_count` | Cored plaques in white matter |
| `GM_cored_count` | Cored plaques in grey matter |
| `cored_no-count` | Unclassified cored plaques |
| **Diffuse Plaques:** | |
| `CNN_diffuse_count` | Total number of diffuse plaques detected |
| `BG_diffuse_count` | Diffuse plaques in background |
| `WM_diffuse_count` | Diffuse plaques in white matter |
| `GM_diffuse_count` | Diffuse plaques in grey matter |
| `diffuse_no-count` | Unclassified diffuse plaques |
| **CAA Plaques:** | |
| `CNN_caa_count` | Total number of CAA plaques detected |
| `BG_caa_count` | CAA plaques in background |
| `WM_caa_count` | CAA plaques in white matter |
| `GM_caa_count` | CAA plaques in grey matter |
| `caa_no-count` | Unclassified CAA plaques |

**Detection Thresholds:**
- **Cored plaques:** confidence > 0.1, size > 100 pixels
- **Diffuse plaques:** confidence > 0.95, size > 1 pixel
- **CAA plaques:** confidence > 0.9, size > 200 pixels

#### 3.6 WSI Index CSV
- **Location:** `{data_dir}/outputs/CNNscore/WSI_CERAD_AREA.csv`
- **Format:** CSV file
- **Content:** List of WSI_ID values processed
- **Description:** Index file for tracking which slides were analyzed

**Example Post-processing Directory Structure:**
```
data/
├── postprocess/
│   ├── images/
│   │   ├── Sample001.png    # Cleaned segmentation (colored)
│   │   └── Sample002.png
│   └── numpy/
│       ├── Sample001.npy    # Cleaned segmentation masks
│       └── Sample002.npy
└── outputs/
    ├── CNNscore/
    │   ├── CNN_vs_CERAD.csv           # ⭐ MAIN OUTPUT: Plaque counts
    │   └── WSI_CERAD_AREA.csv         # WSI index
    └── masked_plaque/
        ├── images/
        │   ├── Sample001_cored.png    # Colored plaque visualizations
        │   ├── Sample001_diffuse.png
        │   ├── Sample001_caa.png
        │   └── ...
        └── numpy/
            ├── Sample001_cored.npy    # Labeled plaque masks
            ├── Sample001_diffuse.npy
            ├── Sample001_caa.npy
            └── ...
```

---

## Additional Pipeline Outputs (From src/ scripts)

### TensorFlow-based Pipeline (`src/predict.py` + `src/postproc.py`)

The original TensorFlow-based pipeline produces similar outputs with some variations:

#### Predicted Masks
- **Location:** `{save_dir}/{model_name}/{svs_name}_mask.png`
- **Format:** PNG image (indexed color, palette mode)
- **Values:** 0 (Background), 1 (GM), 2 (WM)

#### Post-processed Masks
- **Location:** `{mask_dir}/{svs_name}_mask_method{N}.png`
- **Format:** PNG image
- **Methods:** 6 different post-processing methods available (default: method_6)

#### ImageScope XML Annotations
- **Location:** `{mask_dir}/{svs_name}_mask_method{N}.xml`
- **Format:** ImageScope-compatible XML
- **Description:** Annotations viewable in Aperio ImageScope software
- **Content:** Polygon boundaries for GM and WM regions
- **Downsample Rate:** 50x (configurable)

#### Boundary Masks
- **Location:** `{mask_dir}/{svs_name}_mask_method{N}_boundary.png`
- **Format:** PNG image
- **Description:** Extracted boundaries between tissue types

---

## Output Summary Table

| Stage | Output Type | File Format | Primary Use |
|-------|-------------|-------------|-------------|
| **1. Preprocessing** | Image tiles | `.jpg` | Neural network input |
| | Normalization stats | `.csv` | Quality control |
| **2. Inference** | Segmentation masks | `.npy` | Quantitative analysis |
| | Segmentation visualization | `.png` | Visual inspection |
| | Plaque heatmaps | `.npy` | Plaque confidence scores |
| **3. Post-processing** | Cleaned segmentation | `.npy`, `.png` | Final segmentation |
| | Plaque masks (labeled) | `.npy` | Individual plaque tracking |
| | Plaque visualizations | `.png` | Visual inspection |
| | **Plaque count CSV** | `.csv` | **📊 Primary research output** |

---

## Key Output for Researchers

### 🎯 Primary Research Output: `CNN_vs_CERAD.csv`

This CSV file is the **most important output** for neuropathological analysis. It contains:

1. **Quantitative plaque counts** for each WSI
2. **Regional distribution** of plaques (WM vs GM)
3. **Plaque type classification** (cored, diffuse, CAA)
4. Data ready for statistical analysis and correlation with clinical outcomes

**Typical Use Cases:**
- Correlating plaque burden with Alzheimer's disease severity
- Comparing plaque distribution across brain regions
- Statistical analysis of plaque types vs. cognitive scores (CERAD scale)
- Machine learning features for disease prediction

---

## File Size Expectations

### Typical File Sizes (for a 50,000 × 50,000 pixel WSI):

- **Preprocessing:**
  - Image tiles: ~2-5 MB per WSI (distributed across many .jpg files)
  - Stats CSV: < 1 KB

- **Inference:**
  - Segmentation .npy: ~2.5 GB (uncompressed uint8 array)
  - Segmentation .png: ~50-200 MB (compressed)
  - Plaque heatmaps .npy: ~30 GB (3-channel float32 array, uncompressed)

- **Post-processing:**
  - Post-processed segmentation: ~2.5 GB (.npy) + ~50-200 MB (.png)
  - Plaque masks: ~5 GB (.npy, uint16) + ~100-300 MB (.png) per type
  - **CNN_vs_CERAD.csv**: < 1 MB (typically 10-100 KB)

**Note:** Actual sizes depend on WSI resolution and tissue coverage.

---

## Visualization Color Schemes

### Brain Segmentation
- **Background:** Black (RGB: 0,0,0)
- **White Matter:** Yellow (RGB: 255,255,0)
- **Grey Matter:** Cyan (RGB: 0,255,255)

### Plaque Detection
- **Binary mask:** Cyan plaques on black background
- **Labeled mask:** HSV-based color coding
  - Each plaque gets a unique color
  - Hue varies with label number
  - High color diversity = high plaque density

### Confidence Heatmaps
- **Colormap:** Viridis (purple-blue-green-yellow)
- **Range:** 0.0 (low confidence) to 1.0 (high confidence)

---

## Quality Control Outputs

### Recommended QC Checks:

1. **Preprocessing:**
   - Verify tiles are correctly generated (`{save_dir}/{wsi_name}/0/`)
   - Check stats.csv for consistent normalization parameters

2. **Inference:**
   - Inspect segmentation PNGs for obvious misclassifications
   - Verify plaque heatmaps have reasonable confidence distributions

3. **Post-processing:**
   - Compare pre- and post-processed segmentation images
   - Check CNN_vs_CERAD.csv for outliers (abnormally high/low counts)
   - Verify plaque counts match visual inspection of colored masks

---

## Software for Viewing Outputs

| Output Type | Recommended Software |
|-------------|---------------------|
| `.png` images | ImageJ, QuPath, GIMP, any image viewer |
| `.npy` arrays | Python (numpy.load), MATLAB |
| `.csv` files | Excel, Google Sheets, R, Python (pandas) |
| `.xml` annotations | Aperio ImageScope, QuPath |
| `.svs` files | QuPath, Aperio ImageScope, OpenSlide |

---

## Citation

If using this pipeline, please cite:

> Z. Lai, L. Cerny Oliveira, R. Guo, W. Xu, Z. Hu, K. Mifflin, C. DeCarlie, S-C. Cheung, C-N. Chuah, and B. N. Dugger, "BrainSec: Automated Brain Tissue Segmentation Pipeline for Scalable Neuropathological Analysis," IEEE Access, 2022.

---

## Contact

For questions about outputs or pipeline usage:
- **GitHub Issues:** Submit issues at the BrainSec repository
- **Email:** biohpc-help@utsouthwestern.edu (for UTSW BioHPC users)

---

**Last Updated:** January 14, 2026
