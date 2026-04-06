# Design2Web API Reference

Design2Web is a Python tool designed to convert a static design mockup image (PNG/JPG) into a minimal, runnable HTML+CSS web page by analyzing the image structure and color palette.

---

## 📂 `types.py`

Defines core data structures used across the application.

### `DesignRegion`
*   **Signature:** `class DesignRegion(dataclass):`
*   **Description:** Represents a detected, bounded area of the design mockup (e.g., Header, Content).
*   **Attributes:**
    *   `name: str`: The semantic name of the region (e.g., "header").
    *   `bounding_box: tuple[int, int, int, int]`: `(x_min, y_min, x_max, y_max)` coordinates.
    *   `dominant_colors: list[tuple[int, int, int]]`: A list of sampled RGB colors from this region.
*   **Example Usage:**
    ```python
    from types import DesignRegion
    header = DesignRegion(
        name="header",
        bounding_box=(0, 0, 1920, 100),
        dominant_colors=[(255, 255, 255), (0, 0, 0)]
    )
    ```

---

## 🖼️ `image_loader.py`

Handles the loading and basic manipulation of input image files.

### `load_image`
*   **Signature:** `load_image(path: str) -> Image.Image`
*   **Description:** Reads an image file from the specified path into a PIL Image object.
*   **Parameters:**
    *   `path` (`str`): The file path to the input PNG or JPG.
*   **Returns:**
    *   `Image.Image`: The loaded image object.
*   **Example Usage:**
    ```python
    from PIL import Image
    from image_loader import load_image

    img = load_image("mockup.png")
    # img is now a PIL Image object ready for processing
    ```

---

## 📐 `layout_detector.py`

Analyzes the loaded image to segment it into meaningful UI regions.

### `detect_layout_regions`
*   **Signature:** `detect_layout_regions(image: Image.Image) -> list[DesignRegion]`
*   **Description:** Performs basic edge and color analysis to identify major structural components (Header, Sidebar, Content, Footer) and returns them as `DesignRegion` objects.
*   **Parameters:**
    *   `image` (`Image.Image`): The input image loaded by `image_loader.py`.
*   **Returns:**
    *   `list[DesignRegion]`: A list of detected regions with bounding boxes.
*   **Example Usage:**
    ```python
    from PIL import Image
    from layout_detector import detect_layout_regions
    from image_loader import load_image
    from types import DesignRegion

    img = load_image("mockup.png")
    regions = detect_layout_regions(img)
    # regions might contain multiple DesignRegion objects
    ```

---

## 🎨 `color_extractor.py`

Samples and extracts the dominant color palettes from specific image regions.

### `extract_colors`
*   **Signature:** `extract_colors(image: Image.Image, region: DesignRegion) -> list[tuple[int, int, int]]`
*   **Description:** Samples pixels within the boundaries of a given `DesignRegion` and returns a list of the most dominant RGB colors found in that area.
*   **Parameters:**
    *   `image` (`Image.Image`): The original, full-size image.
    *   `region` (`DesignRegion`): The region to sample from.
*   **Returns:**
    *   `list[tuple[int, int, int]]`: A list of dominant RGB color tuples.
*   **Example Usage:**
    ```python
    from PIL import Image
    from color_extractor import extract_colors
    from types import DesignRegion

    # Assume 'img' is the full image and 'header_region' is a detected region
    colors = extract_colors(img, header_region)
    print(f"Header colors found: {colors}")
    ```

---

## 📄 `html_generator.py`

Takes the structural and color data and constructs the final HTML and CSS content.

### `generate_html_and_css`
*   **Signature:** `generate_html_and_css(regions: list[DesignRegion], palette: dict[str, list[tuple[int, int, int]]]) -> tuple[str, str]`
*   **Description:** Constructs a complete HTML string and a corresponding CSS string based on the detected regions and their associated color palettes.
*   **Parameters:**
    *   `regions` (`list[DesignRegion]`): The list of structural regions.
    *   `palette` (`dict[str, list[tuple[int, int, int]]]`) : A dictionary mapping region names to their extracted colors.
*   **Returns:**
    *   `tuple[str, str]`: A tuple containing `(html_content, css_content)`.
*   **Example Usage:**
    ```python
    from html_generator import generate_html_and_css
    # Assume 'all_regions' and 'region_colors' are prepared
    html, css = generate_html_and_css(all_regions, region_colors)
    # html and css are now strings ready to be written to files
    ```

---

## 💾 `output_writer.py`

Handles saving the generated HTML and CSS content to disk.

### `write_output`
*   **Signature:** `write_output(html_content: str, css_content: str, output_path: str) -> str`
*   **Description:** Writes the generated HTML and CSS into a structured directory, returning the path to the final HTML file.
*   **Parameters:**
    *   `html_content` (`str`): The complete HTML markup.
    *   `css_content` (`str`): The complete CSS styles.
    *   `output_path` (`str`): The base directory where files should be saved.
*   **Returns:**
    *   `str`: The absolute path to the generated `index.html` file.
*   **Example Usage:**
    ```python
    from output_writer import write_output

    final_path = write_output(html, css, "./output")
    print(f"Design successfully saved to: {final_path}")
    ```

---

## 🚀 `main.py` (Entry Point)

The primary interface for the Design2Web tool.

### `convert_design`
*   **Signature:** `convert_design(image_path: str) -> str`
*   **Description:** Orchestrates the entire conversion pipeline: loading the image, detecting layout, extracting colors, generating code, and writing the final files.
*   **Parameters:**
    *   `image_path` (`str`): The file path to the input design mockup image.
*   **Returns:**
    *   `str`: The file path to the generated `index.html`.
*   **Example Usage:**
    ```python
    from main import convert_design

    try:
        html_file = convert_design("my_new_mockup.jpg")
        print(f"Conversion complete! Check {html_file}")
    except FileNotFoundError:
        print("Error: Input image not found.")
    ```

---

## 🧪 Testing Modules

These modules are for internal testing and are not part of the primary runtime API.

### `tests/__init__.py`
*   **Description:** Initializes the testing package.

### `tests/conftest.py`
*   **Description:** Contains pytest fixtures used across tests (e.g., mock image loaders, standard configuration objects).

### `tests/fixtures/__init__.py`
*   **Description:** Stores reusable test data fixtures.