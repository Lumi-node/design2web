"""Color extraction module for dominant color analysis via k-means clustering.

This module extracts the 3 dominant colors from each detected region in a design mockup image
using k-means clustering. Colors are sampled from the center 80% of each region to reduce
edge noise, and sorted by frequency (most common first).

For regions with fewer than 10 pixels after center sampling, a random sampling fallback
is used instead of k-means clustering.
"""

import sys
import importlib.util
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans

# Load project types module, handling stdlib types.py conflict
if 'project_types' not in sys.modules:
    types_path = Path(__file__).parent / 'types.py'
    spec = importlib.util.spec_from_file_location('project_types', str(types_path))
    project_types = importlib.util.module_from_spec(spec)
    sys.modules['project_types'] = project_types
    spec.loader.exec_module(project_types)
else:
    project_types = sys.modules['project_types']

ColorExtractionError = project_types.ColorExtractionError


def extract_colors(image: np.ndarray, regions: dict) -> dict:
    """Extract 3 dominant colors from each detected region via k-means clustering.

    Args:
        image: NumPy array of shape (H, W, 3), dtype uint8, RGB 0-255.
        regions: Dict with keys 'header', 'sidebar', 'content', 'footer'.
                Each value is None or {'x': int, 'y': int, 'width': int, 'height': int}
                (output from detect_layout_regions).

    Returns:
        Dict mapping region names to lists of exactly 3 RGB tuples:
        {
            'header': [(r, g, b), (r, g, b), (r, g, b)],
            'sidebar': [(r, g, b), (r, g, b), (r, g, b)],
            'content': [...],
            'footer': [...]
        }
        Only includes regions that were detected (non-None in input).
        Each color is a tuple of integers with 0 <= r, g, b <= 255.

    Raises:
        ColorExtractionError: If clustering fails (rare).
            Message format: "Color extraction failed for region {region}: {sklearn_error}"

    Algorithm:

    1. **For each detected region in regions dict**:

    2. **Pixel Sampling** (reduce edge noise):
       - Extract region pixels: image[y:y+height, x:x+width]
       - Compute center 80% bounds (ignore 10% margins):
         * center_x_start = x + ceil(0.1 * width)
         * center_x_end = x + floor(0.9 * width)
         * center_y_start = y + ceil(0.1 * height)
         * center_y_end = y + floor(0.9 * height)
       - Extract center pixels: image[center_y_start:center_y_end, center_x_start:center_x_end]
       - Reshape to (N_pixels, 3)

    3. **Fallback for small regions** (< 10 pixels after sampling):
       - If N_pixels < 10: Use simple random sampling
         * Randomly select k unique pixels from full region
         * If < k unique colors available: repeat most common color
       - If N_pixels >= 10: Continue to k-means

    4. **K-Means Clustering** (N_pixels >= 10):
       - Use sklearn.cluster.KMeans(n_clusters=3, n_init=10, max_iter=300, random_state=42)
       - Fit on sampled pixels (N, 3) uint8
       - Extract cluster centers (3, 3) float64

    5. **Post-Processing**:
       - Convert cluster centers to uint8: round to nearest integer, clip to [0, 255]
       - Sort by frequency (cluster label counts, descending)
       - Return list of 3 RGB tuples

    Performance: < 100ms for full 800×600 image with 4 regions
    """
    result = {}

    for region_name, region_data in regions.items():
        # Skip undetected regions
        if region_data is None:
            continue

        try:
            x = region_data['x']
            y = region_data['y']
            width = region_data['width']
            height = region_data['height']

            # Extract region pixels
            region_pixels = image[y:y+height, x:x+width]

            # Compute center 80% bounds (ignore 10% margins on all sides)
            center_x_start = x + int(np.ceil(0.1 * width))
            center_x_end = x + int(np.floor(0.9 * width))
            center_y_start = y + int(np.ceil(0.1 * height))
            center_y_end = y + int(np.floor(0.9 * height))

            # Extract center pixels
            sampled_pixels = image[center_y_start:center_y_end, center_x_start:center_x_end]
            sampled_pixels_flat = sampled_pixels.reshape(-1, 3)

            n_pixels = sampled_pixels_flat.shape[0]

            if n_pixels < 10:
                # Use random sampling fallback for small regions
                colors = _random_sampling_fallback(region_pixels, n_clusters=3)
            else:
                # Use k-means clustering for larger regions
                colors = _kmeans_clustering(sampled_pixels_flat, n_clusters=3)

            result[region_name] = colors

        except Exception as e:
            raise ColorExtractionError(
                f"Color extraction failed for region {region_name}: {str(e)}"
            )

    return result


def _kmeans_clustering(pixels: np.ndarray, n_clusters: int = 3) -> list:
    """Extract dominant colors using k-means clustering.

    Args:
        pixels: NumPy array of shape (N, 3), dtype uint8, RGB values.
        n_clusters: Number of clusters (default 3).

    Returns:
        List of n_clusters RGB tuples, sorted by frequency (most common first).
    """
    # Get number of unique colors in pixels
    unique_pixels = np.unique(pixels, axis=0)
    n_unique = len(unique_pixels)

    # If fewer unique colors than clusters, use unique colors and pad
    if n_unique < n_clusters:
        colors = []
        for i in range(n_unique):
            color = tuple(unique_pixels[i].tolist())
            colors.append(color)
        # Pad with the most common color to reach n_clusters
        # Count occurrences
        color_counts = {}
        for pixel in pixels:
            pixel_tuple = tuple(pixel.tolist())
            color_counts[pixel_tuple] = color_counts.get(pixel_tuple, 0) + 1
        most_common = max(color_counts.items(), key=lambda x: x[1])[0]
        while len(colors) < n_clusters:
            colors.append(most_common)
        return colors

    # Fit k-means
    kmeans = KMeans(
        n_clusters=n_clusters,
        n_init=10,
        max_iter=300,
        random_state=42
    )
    kmeans.fit(pixels)

    # Convert cluster centers from float64 to uint8
    centers = kmeans.cluster_centers_
    centers_uint8 = np.round(centers).astype(np.uint8)
    centers_uint8 = np.clip(centers_uint8, 0, 255).astype(np.uint8)

    # Count frequency of each cluster
    labels = kmeans.labels_
    unique_labels, counts = np.unique(labels, return_counts=True)

    # Sort by frequency (descending)
    sorted_indices = np.argsort(-counts)

    # Build result list, returning colors in frequency order
    colors = []
    for idx in sorted_indices:
        cluster_idx = unique_labels[idx]
        color = tuple(centers_uint8[cluster_idx].tolist())
        colors.append(color)

    return colors


def _random_sampling_fallback(region_pixels: np.ndarray, n_clusters: int = 3) -> list:
    """Extract colors using random sampling fallback for small regions.

    Used when a region has fewer than 10 pixels after center 80% sampling.

    Args:
        region_pixels: NumPy array of shape (H, W, 3), dtype uint8 (full region, not sampled).
        n_clusters: Number of colors to extract (default 3).

    Returns:
        List of n_clusters RGB tuples. If fewer than n_clusters unique colors exist,
        the most common color is repeated.
    """
    # Reshape to (N, 3)
    pixels_flat = region_pixels.reshape(-1, 3)

    # Find unique colors
    unique_pixels = np.unique(pixels_flat, axis=0)

    colors = []

    if len(unique_pixels) >= n_clusters:
        # If we have enough unique colors, randomly select n_clusters of them
        selected_indices = np.random.choice(len(unique_pixels), n_clusters, replace=False)
        for idx in selected_indices:
            color = tuple(unique_pixels[idx].tolist())
            colors.append(color)
    else:
        # If we have fewer unique colors than n_clusters, use them all
        # and repeat the most common one
        # Count occurrences of each unique color
        color_counts = {}
        for pixel in pixels_flat:
            pixel_tuple = tuple(pixel.tolist())
            color_counts[pixel_tuple] = color_counts.get(pixel_tuple, 0) + 1

        # Sort by frequency (descending)
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)

        # Add all unique colors
        for color, _ in sorted_colors:
            colors.append(color)

        # Repeat the most common color to reach n_clusters
        most_common_color = colors[0]
        while len(colors) < n_clusters:
            colors.append(most_common_color)

    return colors
