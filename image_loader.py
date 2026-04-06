"""Image loading and validation module for design-to-HTML converter.

This module provides the load_image function to load PNG/JPG images,
validate their properties, and convert them to RGB numpy arrays.
"""

import os
from pathlib import Path
import numpy as np
from PIL import Image
import sys
import importlib.util

# Import ImageLoadError from types module
# We need to handle the name conflict with stdlib types module
# First, check if it's already loaded (in test environment)
if 'project_types' in sys.modules:
    # Already loaded by conftest or test setup
    ImageLoadError = sys.modules['project_types'].ImageLoadError
else:
    # Load it ourselves with a unique namespace
    _types_path = os.path.join(os.path.dirname(__file__), 'types.py')
    _spec = importlib.util.spec_from_file_location("_project_types_loader", _types_path)
    _project_types = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_project_types)
    ImageLoadError = _project_types.ImageLoadError


def load_image(path: str) -> np.ndarray:
    """
    Load PNG or JPG image and validate dimensions.

    Args:
        path: Absolute or relative path to PNG/JPG image.

    Returns:
        Image as numpy array of shape (H, W, 3) with dtype uint8 in RGB order.

    Raises:
        FileNotFoundError: If file doesn't exist
            Message format: "Image file not found: {path}"

        ValueError: If file format is not PNG or JPG
            Message format: "Unsupported image format: {ext}. Must be PNG or JPG"
            (extensions checked case-insensitive)

        ValueError: If image dimensions < 200×200 or > 2000×2000
            Message format: "Image dimension {width}x{height} outside valid range [200-2000]"

        ImageLoadError: If image can't be decoded
            Message format: "Failed to load image {path}: {PIL_error}"

    Implementation Details:
    - Use Pillow (PIL.Image) to load image
    - Convert to RGB if necessary (handle RGBA, grayscale, CMYK, etc.)
    - Convert to numpy array (H, W, 3) uint8
    - Validate file extension (case-insensitive, accept .png, .jpg, .jpeg)
    - Validate dimensions before returning
    - Do NOT return metadata—only image array
    """
    # Step 1: Check file exists
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")

    # Step 2: Validate extension (case-insensitive)
    file_ext = os.path.splitext(path)[1].lower()
    if file_ext not in ['.png', '.jpg', '.jpeg']:
        # Extract extension without the dot for error message
        ext_display = file_ext.lstrip('.')
        raise ValueError(f"Unsupported image format: {ext_display}. Must be PNG or JPG")

    # Step 3: Load with PIL
    try:
        image = Image.open(path)
        # Force load of image data to catch corruption errors
        image.load()
    except Exception as e:
        raise ImageLoadError(f"Failed to load image {path}: {str(e)}")

    # Step 4: Validate dimensions before conversion
    # PIL returns (width, height)
    try:
        width, height = image.size
    except Exception as e:
        raise ImageLoadError(f"Failed to load image {path}: {str(e)}")

    if width < 200 or width > 2000 or height < 200 or height > 2000:
        raise ValueError(f"Image dimension {width}x{height} outside valid range [200-2000]")

    # Step 5: Convert to RGB if necessary
    # Handle various image modes: RGBA, L (grayscale), P (palette), CMYK, etc.
    try:
        if image.mode != 'RGB':
            # For RGBA, convert directly to RGB (PIL drops alpha)
            # For L (grayscale), convert to RGB (PIL duplicates channel)
            # For other modes (P, CMYK, etc.), convert to RGB
            image = image.convert('RGB')
    except Exception as e:
        raise ImageLoadError(f"Failed to load image {path}: {str(e)}")

    # Step 6: Convert to numpy array (H, W, 3) uint8
    try:
        array = np.asarray(image, dtype=np.uint8)
    except Exception as e:
        raise ImageLoadError(f"Failed to load image {path}: {str(e)}")

    # Validate array shape and dtype
    if array.ndim != 3 or array.shape[2] != 3:
        raise ImageLoadError(f"Failed to convert image to RGB: unexpected shape {array.shape}")

    return array
