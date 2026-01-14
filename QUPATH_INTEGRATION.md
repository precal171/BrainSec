# Importing BrainSec Segmentations into QuPath

## Overview

Yes! BrainSec segmentations can be imported into QuPath for visualization, manual refinement, and further analysis. BrainSec includes built-in tools to export segmentations in QuPath-compatible formats.

---

## Method 1: ImageScope XML Annotations (Recommended)

### What This Does
Converts your brain segmentation masks into **vector annotations** (polygons) that QuPath can load as editable regions.

### Step 1: Export Segmentations to XML

Use the `postproc.py` script with the `--only-convert-xml` flag:

```bash
cd /path/to/BrainSec/src

# Convert existing masks to XML annotations
python postproc.py \
    /path/to/data/outputs/UNet_model \
    --only-convert-xml \
    --xml-downsample-rate 50
```

**Parameters:**
- First argument: Directory containing your `.png` mask files
- `--only-convert-xml`: Skip post-processing, only generate XML
- `--xml-downsample-rate`: Contour simplification factor (default: 50)
  - Lower values = more detailed polygons but larger file sizes
  - Higher values = simpler polygons but faster loading
  - Recommended: 20-100 depending on your needs

**Output:**
```
/path/to/data/outputs/UNet_model/xml_annotations/
├── Sample001.xml
├── Sample002.xml
└── ...
```

### Step 2: Import XML into QuPath

1. **Open your WSI in QuPath:**
   - File → Open → Select your `.svs` file

2. **Run the import script:**
   - Automate → Show script editor
   - Open the script: `/path/to/BrainSec/qupath/scripts/LoadAperioXMLAnnotation.groovy`
   - Click **Run** (or press Ctrl+R)

3. **Select your XML file:**
   - A file dialog will appear
   - Navigate to your XML annotation file (e.g., `Sample001.xml`)
   - Click Open

4. **View annotations:**
   - Your segmentations will appear as polygon annotations
   - Each region (GM/WM) is a separate annotation group

### XML Format Details

The exported XML contains:
- **Gray Matter annotations** (Annotation Id="1")
- **White Matter annotations** (Annotation Id="2")
- **Polygon vertices** for each region contour
- Compatible with Aperio ImageScope and QuPath

---

## Method 2: Direct PNG/TIFF Overlay

### Option A: Simple Overlay (Read-only visualization)

1. **Open WSI in QuPath**

2. **Add overlay image:**
   - Automate → Show script editor
   - Run this script:

```groovy
import qupath.lib.images.servers.ImageServerProvider
import qupath.lib.gui.viewer.overlays.BufferedImageOverlay

def overlayPath = '/path/to/data/postprocess/images/Sample001.png'
def overlayServer = ImageServerProvider.buildServer(overlayPath)
def overlay = new BufferedImageOverlay(overlayServer)

// Add to viewer
def viewer = getCurrentViewer()
viewer.setCustomPixelLayerOverlay(overlay)
```

3. **Adjust opacity:**
   - View → Brightness/Contrast
   - Adjust overlay transparency

**Pros:**
- Quick visualization
- No conversion needed

**Cons:**
- Not editable
- Masks are raster, not vector

### Option B: Convert PNG to Classifications

For pixel-level classification overlays:

```groovy
import qupath.lib.images.servers.ImageServerProvider
import qupath.lib.objects.classes.PathClassFactory
import qupath.lib.regions.RegionRequest

// Load your segmentation PNG
def maskPath = '/path/to/data/postprocess/images/Sample001.png'
def maskServer = ImageServerProvider.buildServer(maskPath)

// Define classes matching your color scheme
def bgClass = PathClassFactory.getPathClass("Background")
def wmClass = PathClassFactory.getPathClass("White Matter")
def gmClass = PathClassFactory.getPathClass("Gray Matter")

// Read mask and create pixel classifier
def mask = maskServer.readBufferedImage(RegionRequest.createInstance(maskServer))

// TODO: Implement pixel-by-pixel classification based on color
// This is a more advanced script - consider using XML export instead
```

---

## Method 3: Export from QuPath's Pixel Classifier Format

If you want to use BrainSec segmentations as **training data** for QuPath's own pixel classifier:

### Step 1: Convert Segmentations to GeoJSON

Create a Python script to export contours:

```python
import numpy as np
from skimage import measure
from PIL import Image
import json

def mask_to_geojson(mask_path, output_path):
    """Convert segmentation mask to GeoJSON for QuPath"""
    mask = np.array(Image.open(mask_path))

    features = []

    # Extract GM contours
    gm_contours = measure.find_contours(mask == 1, 0.5)
    for contour in gm_contours:
        coords = [[float(x), float(y)] for y, x in contour]
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [coords]},
            "properties": {"classification": {"name": "Gray Matter"}}
        })

    # Extract WM contours
    wm_contours = measure.find_contours(mask == 2, 0.5)
    for contour in wm_contours:
        coords = [[float(x), float(y)] for y, x in contour]
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [coords]},
            "properties": {"classification": {"name": "White Matter"}}
        })

    geojson = {"type": "FeatureCollection", "features": features}

    with open(output_path, 'w') as f:
        json.dump(geojson, f)

# Usage
mask_to_geojson('data/postprocess/images/Sample001.png', 'Sample001.geojson')
```

### Step 2: Import GeoJSON into QuPath

1. Open WSI in QuPath
2. Run: `File → Object data → Import objects → GeoJSON`
3. Select your `.geojson` file
4. Annotations will appear as editable objects

---

## Method 4: Load as Image Annotation

For plaque detection results with heatmaps:

```groovy
// This creates an annotation region from your plaque detection images
import qupath.lib.images.servers.ImageServerProvider
import qupath.lib.objects.PathObjects
import qupath.lib.roi.ROIs

def plaquePath = '/path/to/data/outputs/masked_plaque/images/Sample001_cored.png'
def plaqueServer = ImageServerProvider.buildServer(plaquePath)
def plaqueImage = plaqueServer.readBufferedImage()

// Create annotation covering the plaque region
def roi = ROIs.createRectangleROI(0, 0, plaqueImage.width, plaqueImage.height, null)
def annotation = PathObjects.createAnnotationObject(roi)

getCurrentHierarchy().addPathObject(annotation)
```

---

## Recommended Workflow

### For Brain Tissue Segmentation Review:

1. **Export to XML** (Method 1)
   ```bash
   python src/postproc.py data/outputs/UNet --only-convert-xml --xml-downsample-rate 30
   ```

2. **Load in QuPath** using `LoadAperioXMLAnnotation.groovy`

3. **Manual refinement in QuPath:**
   - Use brush tool to fix misclassifications
   - Merge or split regions as needed
   - Add additional annotations

4. **Export refined annotations:**
   - File → Object data → Export as GeoJSON
   - Use for retraining or final analysis

### For Plaque Quantification:

1. **Load WSI in QuPath**

2. **Import brain segmentation XML** (GM/WM regions)

3. **Create detections from plaque masks:**
   - Use pixel classifier or import plaque coordinates
   - QuPath can count detections within each region

4. **Quantify:**
   - Measure → Show detection measurements
   - Export plaque counts per region

---

## Comparison of Methods

| Method | Import Type | Editable | Best For |
|--------|-------------|----------|----------|
| **XML (Method 1)** | Vector polygons | ✅ Yes | Manual review & refinement |
| **PNG Overlay (2A)** | Raster image | ❌ No | Quick visualization |
| **GeoJSON (Method 3)** | Vector polygons | ✅ Yes | Advanced workflows |
| **Image Annotation (4)** | Raster region | ⚠️ Limited | Plaque overlays |

---

## Tips & Best Practices

### XML Export Optimization

**For large WSIs (>100,000 × 100,000 pixels):**
- Use `--xml-downsample-rate 100` for faster loading
- QuPath may struggle with extremely detailed polygons

**For accurate boundaries:**
- Use `--xml-downsample-rate 10-20` for high precision
- Expect larger file sizes and slower loading

### Color Mapping

Match BrainSec colors in QuPath:

```groovy
// Set annotation colors to match BrainSec output
def annotations = getAnnotationObjects()
annotations.each { annotation ->
    if (annotation.getName() == "Gray Matter") {
        annotation.setColorRGB(0, 255, 255)  // Cyan
    } else if (annotation.getName() == "White Matter") {
        annotation.setColorRGB(255, 255, 0)  // Yellow
    }
}
fireHierarchyUpdate()
```

### Memory Considerations

Loading full-resolution masks for large WSIs may require:
- QuPath: 8+ GB RAM recommended
- Java heap size: `-Xmx16g` or higher

Edit QuPath's `qupath.cfg` or startup script to increase memory.

---

## Troubleshooting

### Issue: XML fails to load in QuPath

**Solution:**
- Check that XML file was generated: `ls data/outputs/UNet/xml_annotations/`
- Verify XML format: Open in text editor, should start with `<Annotations>`
- Update QuPath script to v0.2.0+ syntax if using older version

### Issue: Polygons are too simplified

**Solution:**
- Re-export with lower downsample rate:
  ```bash
  python src/postproc.py data/outputs/UNet --only-convert-xml --xml-downsample-rate 10
  ```

### Issue: QuPath crashes with large annotations

**Solution:**
- Increase downsample rate: `--xml-downsample-rate 200`
- Post-process to remove small regions first
- Load regions selectively (modify Groovy script to filter by size)

### Issue: Coordinates don't align with WSI

**Solution:**
- Check image orientation: Set `rotated = true` in `LoadAperioXMLAnnotation.groovy`
- Verify mask and WSI have same dimensions
- Ensure preprocessing didn't change image size

---

## Advanced: Round-trip Workflow

### BrainSec → QuPath → Refined Training Data

1. **Initial segmentation with BrainSec**
2. **Export to XML and load in QuPath**
3. **Manual corrections in QuPath**
4. **Export refined annotations as GeoJSON**
5. **Convert back to training masks:**

```python
import json
import numpy as np
from PIL import Image, ImageDraw

def geojson_to_mask(geojson_path, width, height, output_path):
    """Convert QuPath GeoJSON to training mask"""
    with open(geojson_path) as f:
        data = json.load(f)

    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)

    for feature in data['features']:
        coords = feature['geometry']['coordinates'][0]
        class_name = feature['properties']['classification']['name']

        # Polygon vertices
        polygon = [(x, y) for x, y in coords]

        # Draw with appropriate label
        if class_name == "Gray Matter":
            draw.polygon(polygon, fill=1)
        elif class_name == "White Matter":
            draw.polygon(polygon, fill=2)

    mask.save(output_path)

# Usage
geojson_to_mask('Sample001_refined.geojson', 50000, 50000, 'refined_mask.png')
```

6. **Retrain BrainSec models with refined data**

---

## Additional Resources

- **QuPath Documentation:** https://qupath.readthedocs.io/
- **QuPath Scripting Guide:** https://qupath.github.io/scripting/
- **BrainSec QuPath Tutorial:** See `/home/user/BrainSec/qupath/README.md` (if available)
- **Google Doc Tutorial:** [Brief tutorial](https://docs.google.com/document/d/125n8o4KQlUcEIbycHDTXV-8pBcj-CLsxISnygt0SecM/edit?usp=sharing) (mentioned in README)

---

## Summary

**✅ YES, you can import BrainSec segmentations into QuPath!**

**Recommended path:**
1. Use `python src/postproc.py --only-convert-xml` to export XML
2. Load in QuPath using the provided `LoadAperioXMLAnnotation.groovy` script
3. Manually refine as needed
4. Use for validation, visualization, or generating refined training data

The pipeline was designed with QuPath integration in mind, and includes both export tools and import scripts to make this workflow seamless.
