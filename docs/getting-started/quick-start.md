# Design2Web Quick Start Guide

Design2Web is a Python tool designed to automate the conversion of a static design mockup image (PNG/JPG) into a minimal, runnable HTML and CSS web page.

## 🚀 Installation

Assuming you have Python installed, you can install the package:

```bash
pip install design2web
```

## 🧩 Module Overview

The tool is composed of several specialized modules:

*   `main.py`: The primary entry point, containing the `convert_design` function.
*   `image_loader.py`: Handles reading and processing the input image file.
*   `layout_detector.py`: Analyzes the image to segment different UI areas (e.g., header, content).
*   `color_extractor.py`: Samples and extracts dominant color palettes from detected regions.
*   `html_generator.py`: Constructs the final HTML and CSS structure based on the analysis.
*   `output_writer.py`: Saves the generated HTML file to the filesystem.
*   `types.py`: Defines shared data structures used across the modules.

## ⚙️ Usage Guide

The core functionality is exposed through the `main.py` module. You will use the `convert_design` function, passing the path to your mockup image.

### Prerequisites

Ensure you have a static design mockup image (e.g., `mockup.png`) ready to process.

### Basic Workflow

1.  **Load Image**: `image_loader.load_image(path)`
2.  **Detect Layout**: `layout_detector.detect_layout_regions(image)`
3.  **Extract Colors**: `color_extractor.extract_colors(image)`
4.  **Generate & Write**: `main.convert_design(path)`

---

## 💡 Usage Examples

Here are three examples demonstrating how to use Design2Web in different scenarios.

### Example 1: Simple Conversion (Standard Use Case)

This is the most common use case: taking a single image and generating a complete HTML file.

```python
import os
from design2web.main import convert_design

# Define the path to your design mockup
MOCKUP_PATH = "assets/my_landing_page.png"
OUTPUT_FILENAME = "output/landing_page.html"

try:
    # Run the conversion process
    generated_file_path = convert_design(MOCKUP_PATH)
    
    print(f"✅ Success! Design converted.")
    print(f"Output saved to: {generated_file_path}")

except FileNotFoundError:
    print(f"❌ Error: Mockup image not found at {MOCKUP_PATH}")
except Exception as e:
    print(f"❌ An unexpected error occurred during conversion: {e}")
```

### Example 2: Inspecting Intermediate Results (Advanced Debugging)

If you need to see *what* the tool detected before generating the final HTML, you can manually chain the functions. This is useful for debugging layout detection or color sampling.

```python
from design2web.image_loader import load_image
from design2web.layout_detector import detect_layout_regions
from design2web.color_extractor import extract_colors
import numpy as np # Assuming image processing uses numpy arrays

MOCKUP_PATH = "assets/dashboard_mockup.jpg"

# 1. Load the image
design_image = load_image(MOCKUP_PATH)

# 2. Detect regions (e.g., returns a dictionary of bounding boxes)
regions = detect_layout_regions(design_image)
print("\n--- Detected Layout Regions ---")
print(regions)

# 3. Extract colors from the main content area (assuming 'content' is a key)
if 'content' in regions:
    content_region = regions['content']
    dominant_colors = extract_colors(design_image, region=content_region)
    print("\n--- Extracted Dominant Colors ---")
    print(dominant_colors)
```

### Example 3: Batch Processing Multiple Designs

To process an entire directory of mockups, you can wrap the `convert_design` function in a loop.

```python
import os
from design2web.main import convert_design

INPUT_DIR = "mockups_to_convert"
OUTPUT_DIR = "generated_htmls"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"🔍 Starting batch conversion from {INPUT_DIR}...")

for filename in os.listdir(INPUT_DIR):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        input_path = os.path.join(INPUT_DIR, filename)
        
        # Create a clean output name
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}.html")
        
        print(f"Processing {filename}...")
        
        try:
            # Convert and overwrite the default output path if necessary, 
            # or modify convert_design to accept an output path argument.
            # For this example, we assume convert_design handles naming based on input.
            final_path = convert_design(input_path)
            print(f"  -> Saved successfully to {final_path}")
        except Exception as e:
            print(f"  -> FAILED to process {filename}: {e}")

print("\n✨ Batch conversion complete.")
```