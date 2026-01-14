# BrainSec Development Environment Recommendations

## TL;DR - Recommended Setup

**🏆 Best Choice: UTSW BioHPC Jupyter Notebook via OnDemand Portal**

**Why:** Direct access to GPUs, large storage, no timeouts, handles massive WSI files

---

## Environment Comparison for BrainSec

### ❌ Google Colab - NOT RECOMMENDED

**Why NOT to use Colab for BrainSec:**

| Issue | Impact on BrainSec |
|-------|-------------------|
| **12-hour runtime limit** | Inference on large WSIs can take hours per slide - you'll get disconnected mid-processing |
| **Limited storage (~100GB)** | A single WSI can be 1-5GB, with outputs reaching 30-50GB per slide |
| **No persistent file access** | Can't easily access BioHPC file systems where your data lives |
| **Session timeouts** | If your browser closes or network hiccups, you lose progress |
| **GPU not guaranteed** | Free tier may not give you GPU, and it's slower than BioHPC GPUs |
| **Memory constraints** | 12-25GB RAM may not be enough for full-resolution WSI processing |
| **Upload/download bottleneck** | Transferring multi-GB WSI files to/from Colab is painfully slow |

**When Colab MIGHT work:**
- Small test datasets (< 10 images)
- Experimenting with preprocessing on downsampled images
- Quick prototyping of new features
- Learning/educational purposes only

**Bottom line:** Colab is designed for small-scale ML experiments, not production medical imaging pipelines with massive files.

---

## ✅ Recommended Options

### 🥇 Option 1: UTSW BioHPC Jupyter Notebook (BEST)

**Access via BioHPC OnDemand Portal:**
- URL: `https://portal.biohpc.swmed.edu`
- Navigate to: **BioHPC OnDemand → Interactive Apps → Jupyter Notebook**

**Advantages:**
- ✅ **Direct GPU access** - Modern NVIDIA GPUs optimized for deep learning
- ✅ **No timeouts** - Run jobs for days if needed
- ✅ **Massive storage** - Access to BioHPC's petabyte-scale storage
- ✅ **Pre-installed software** - Many modules already available
- ✅ **File system integration** - Your data is already there
- ✅ **High RAM** - 128GB+ for large WSI processing
- ✅ **Fast I/O** - High-speed storage for large files
- ✅ **Collaborative** - Share notebooks with your lab
- ✅ **Free for UTSW users** - No cost limitations

**Setup Steps:**

1. **Access BioHPC OnDemand:**
   ```
   https://portal.biohpc.swmed.edu
   Login with UTSW credentials
   ```

2. **Launch Jupyter:**
   - Click "BioHPC OnDemand" (top navigation)
   - Select "Interactive Apps" → "Jupyter Notebook"
   - Configure resources:
     - **Hours:** 8-24 (for long inference jobs)
     - **Memory:** 64-128 GB
     - **GPUs:** 1-2 (for inference)
     - **Partition:** gpu
   - Click "Launch"

3. **Setup BrainSec environment:**
   ```bash
   # In Jupyter terminal
   cd /project/your_lab/
   git clone <BrainSec repo>
   cd BrainSec

   # Create conda environment
   module load python
   conda create -n brainsec python=3.11
   conda activate brainsec

   # Install dependencies (use updated requirements)
   pip install -r install/requirements-updated.txt
   pip install -r install/dev-requirements.txt
   ```

4. **Create Jupyter kernel:**
   ```bash
   conda activate brainsec
   python -m ipykernel install --user --name brainsec --display-name "BrainSec (Py3.11)"
   ```

5. **Start working:**
   - Open existing notebooks or create new ones
   - Select kernel: "BrainSec (Py3.11)"
   - You now have full access to BioHPC resources!

**Best For:**
- Interactive analysis and visualization
- Running the full pipeline with monitoring
- Exploring results and generating figures
- Iterative development and debugging

---

### 🥈 Option 2: VSCode with Remote SSH (EXCELLENT for Development)

**Setup:**

1. **Install VSCode** on your local machine
2. **Install Remote-SSH extension**
3. **Configure SSH to BioHPC:**
   ```
   Host biohpc
       HostName nucleus.biohpc.swmed.edu
       User your_username
       ForwardAgent yes
   ```

4. **Connect and develop:**
   - Cmd/Ctrl+Shift+P → "Remote-SSH: Connect to Host"
   - Select "biohpc"
   - Open BrainSec folder
   - Install Python extension in remote VSCode

**Advantages:**
- ✅ **Full IDE features** - IntelliSense, debugging, git integration
- ✅ **Jupyter notebook support** - Built-in notebook viewer
- ✅ **Multi-file editing** - Better than Jupyter for coding
- ✅ **Terminal access** - Integrated terminal for running scripts
- ✅ **Git integration** - Easy commits and pushes
- ✅ **Remote compute** - All processing happens on BioHPC

**Best For:**
- Writing and refactoring code
- Debugging complex issues
- Managing multiple Python files
- Git workflow and version control

---

### 🥉 Option 3: JupyterLab on BioHPC (Modern Alternative)

JupyterLab is the next-generation Jupyter interface with:
- Multi-document interface (work on multiple notebooks side-by-side)
- Integrated file browser
- Terminal access
- Markdown editor
- Better extension system

**Setup:**
```bash
# On BioHPC
conda activate brainsec
pip install jupyterlab

# Launch
jupyter lab --no-browser --port=8888
```

Then set up SSH tunnel from your local machine:
```bash
ssh -N -L 8888:localhost:8888 your_username@nucleus.biohpc.swmed.edu
```

Access at: `http://localhost:8888`

**Best For:**
- Users who want more than Jupyter Notebook but don't need full IDE
- Multi-notebook workflows
- Integrated data exploration

---

### 🔧 Option 4: Command Line + Scripts (Production Pipeline)

**BrainSec is designed primarily for command-line execution!**

The Python scripts in `pyscripts/` are meant to be run as batch jobs:

```bash
# Example SLURM batch script for BioHPC
#!/bin/bash
#SBATCH --job-name=brainsec_inference
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=logs/inference_%j.log

module load python cuda
conda activate brainsec

# Run pipeline
cd /project/your_lab/BrainSec

# Step 1: Preprocessing
python pyscripts/1_preprocessing.py \
    --wsi_dir data/wsi/ \
    --save_dir data/norm_tiles/ \
    --normalize True

# Step 2: Inference
python pyscripts/2_inference.py \
    --img_dir data/norm_tiles/ \
    --model_plaq models/plaque_model.pth \
    --model_seg models/seg_model.pth \
    --save_plaq_dir data/outputs/heatmaps/ \
    --save_np_dir data/brainseg/numpy/

# Step 3: Post-processing
python pyscripts/3_postprocessing.py \
    --data_dir data/
```

Submit with:
```bash
sbatch run_brainsec.sh
```

**Best For:**
- Production processing of many WSIs
- Reproducible batch processing
- Automated pipelines
- Long-running jobs that don't need monitoring

---

## Hybrid Workflow Recommendation

**The ideal setup uses MULTIPLE tools:**

### Phase 1: Development & Exploration
**Tool:** VSCode Remote SSH or BioHPC Jupyter
- Write and test code
- Debug issues
- Explore small datasets
- Generate visualizations

### Phase 2: Batch Processing
**Tool:** SLURM batch scripts
- Process entire cohorts
- Run overnight/multi-day jobs
- Automated pipeline execution

### Phase 3: Analysis & Visualization
**Tool:** Jupyter Notebook (BioHPC OnDemand)
- Load results from batch processing
- Generate figures and statistics
- Interactive analysis of CSV outputs
- Create publication-quality visualizations

### Phase 4: Manual Review
**Tool:** QuPath
- Review segmentations visually
- Manual corrections
- Quality control checks

---

## Detailed Comparison Table

| Feature | BioHPC Jupyter | VSCode Remote | Google Colab | Command Line |
|---------|---------------|---------------|--------------|--------------|
| **Setup Complexity** | Easy | Medium | Very Easy | Easy |
| **GPU Access** | ✅ Guaranteed | ✅ Yes | ⚠️ Not guaranteed | ✅ Yes |
| **Runtime Limit** | ✅ None | ✅ None | ❌ 12 hours | ✅ None |
| **Storage** | ✅ Unlimited | ✅ Unlimited | ❌ ~100GB | ✅ Unlimited |
| **File Access** | ✅ Direct | ✅ Direct | ❌ Upload/download | ✅ Direct |
| **RAM** | ✅ 64-256GB | ✅ 64-256GB | ❌ 12-25GB | ✅ 64-256GB |
| **Debugging** | ⚠️ Basic | ✅ Excellent | ⚠️ Basic | ❌ Minimal |
| **Multi-file editing** | ❌ No | ✅ Yes | ❌ No | ⚠️ Via vim/nano |
| **Visualization** | ✅ Excellent | ✅ Good | ✅ Excellent | ❌ No |
| **Collaboration** | ✅ Yes | ⚠️ Limited | ✅ Easy | ❌ No |
| **Version Control** | ⚠️ Manual | ✅ Integrated | ⚠️ Manual | ✅ Command line |
| **Cost (UTSW users)** | ✅ Free | ✅ Free | ⚠️ Free tier limited | ✅ Free |
| **Best For** | Interactive analysis | Development | ❌ Not suitable | Production runs |

---

## Specific BrainSec Workflow Example

### Using BioHPC Jupyter (Recommended)

**Notebook Structure:**

```python
# Cell 1: Setup
import sys
sys.path.append('/project/your_lab/BrainSec/pyscripts')
sys.path.append('/project/your_lab/BrainSec/src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Cell 2: Check GPU
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")

# Cell 3: Set paths
DATA_DIR = Path('/project/your_lab/data/brainsec_cohort_2024/')
WSI_DIR = DATA_DIR / 'wsi'
OUTPUT_DIR = DATA_DIR / 'outputs'

# Cell 4: Run preprocessing (for small batches)
from preprocessing import tile
tile(str(WSI_DIR), str(OUTPUT_DIR / 'tiles'), normalize=True)

# Cell 5: Or submit batch job for large cohorts
import subprocess
subprocess.run(['sbatch', 'batch_scripts/run_inference.sh'])

# Cell 6: Monitor job status
subprocess.run(['squeue', '-u', 'your_username'])

# Cell 7: Once complete, load results
results = pd.read_csv(OUTPUT_DIR / 'CNNscore' / 'CNN_vs_CERAD.csv')
print(results.head())

# Cell 8: Visualize results
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
results.plot(x='WSI_ID', y='CNN_cored_count', kind='bar', ax=axes[0], title='Cored Plaques')
results.plot(x='WSI_ID', y='CNN_diffuse_count', kind='bar', ax=axes[1], title='Diffuse Plaques')
results.plot(x='WSI_ID', y='CNN_caa_count', kind='bar', ax=axes[2], title='CAA')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'figures' / 'plaque_counts.png', dpi=300)
```

---

## Environment-Specific Tips

### For BioHPC Jupyter:

**Optimize notebook performance:**
```python
# Cell 1: Set memory limits for large arrays
import os
os.environ['MALLOC_TRIM_THRESHOLD_'] = '65536'

# Cell 2: Use garbage collection for memory-intensive operations
import gc
gc.collect()

# Cell 3: Display progress bars
from tqdm.notebook import tqdm  # Use notebook version for better display
```

**Save intermediate results:**
```python
# Don't recompute expensive operations
if not Path('cache/segmentations.npy').exists():
    # Run expensive operation
    segmentations = run_segmentation(...)
    np.save('cache/segmentations.npy', segmentations)
else:
    segmentations = np.load('cache/segmentations.npy')
```

### For VSCode:

**Recommended Extensions:**
- Python
- Pylance
- Jupyter
- Remote - SSH
- GitLens
- Better Comments

**Settings for BrainSec:**
```json
{
    "python.defaultInterpreterPath": "/home/your_username/.conda/envs/brainsec/bin/python",
    "python.terminal.activateEnvironment": true,
    "jupyter.notebookFileRoot": "${workspaceFolder}",
    "files.watcherExclude": {
        "**/data/**": true,  // Don't watch large data directories
        "**/outputs/**": true
    }
}
```

---

## Hardware Requirements

### Minimum for BrainSec:
- **RAM:** 64GB (for full-resolution WSI processing)
- **GPU:** 8GB VRAM (NVIDIA GTX 1080 or better)
- **Storage:** 500GB+ for datasets

### Recommended:
- **RAM:** 128GB+
- **GPU:** 16GB+ VRAM (NVIDIA RTX A4000, V100, or A100)
- **Storage:** 2TB+ on fast SSD/NFS

**BioHPC Resources:**
- Nucleus cluster has nodes with 256GB+ RAM
- Modern NVIDIA GPUs (V100, A100)
- High-performance storage (parallel filesystem)

---

## Getting Help

### BioHPC Support:
- **Email:** biohpc-help@utsouthwestern.edu
- **Documentation:** https://portal.biohpc.swmed.edu/content/guides/
- **Training:** Regular workshops on Jupyter, SLURM, and GPU computing

### BrainSec-Specific Issues:
- Check `DEPENDENCY_AUDIT_REPORT.md` for package issues
- Review `PROGRAM_OUTPUTS.md` for expected outputs
- See `QUPATH_INTEGRATION.md` for visualization

---

## Final Recommendation

### 🎯 For You (UTSW BioHPC User):

**Start with:** BioHPC Jupyter Notebook via OnDemand
- Easiest to get started
- Full access to GPUs and storage
- Interactive and visual
- No timeout concerns

**Add later:** VSCode Remote SSH
- When you need better code editing
- For managing multiple files
- Enhanced debugging capabilities

**Avoid:** Google Colab
- Not suitable for BrainSec's requirements
- Too many limitations for medical imaging

**Use for production:** SLURM batch scripts
- When processing large cohorts
- Automated overnight processing
- Reproducible pipelines

---

## Quick Start Commands

### Launch Jupyter on BioHPC OnDemand:
1. Go to: https://portal.biohpc.swmed.edu
2. BioHPC OnDemand → Interactive Apps → Jupyter Notebook
3. Request: 8 hours, 64GB RAM, 1 GPU, gpu partition
4. Launch and wait for session to start
5. Open terminal in Jupyter and setup BrainSec environment

### First Jupyter Notebook:
Create `test_brainsec.ipynb`:
```python
# Test BrainSec setup
import torch
import tensorflow as tf
import cv2
import pyvips

print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"TensorFlow: {tf.__version__}")
print(f"OpenCV: {cv2.__version__}")
print(f"PyVips: {pyvips.__version__}")

# Test GPU
if torch.cuda.is_available():
    x = torch.rand(1000, 1000).cuda()
    print(f"GPU test successful: {x.device}")
```

You're all set! 🚀

---

**Last Updated:** January 14, 2026
