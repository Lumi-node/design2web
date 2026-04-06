# Design2Web API Reference

Design2Web is a Python CLI tool designed to transform a structured JSON design specification into a complete, runnable web application (HTML, CSS, and basic JavaScript).

---

## Core Modules

### `types.py`

Defines the core data structures used throughout the application to ensure type safety and consistency when handling design specifications.

**Key Classes/Types:**

*   **`DesignSpec` (TypedDict/Dataclass)**
    *   **Signature:** `DesignSpec`
    *   **Description:** The root structure representing the entire design. It contains metadata, global styles, and a list of components.
    *   **Example Usage:**
        ```python
        from types import DesignSpec
        spec_data: DesignSpec = {
            "metadata": {"title": "My Awesome Site"},
            "global_styles": {"primary_color": "#007bff", "font_family": "Arial"},
            "components": [...]
        }
        ```

### `image_loader.py`

Handles the loading, processing, and path management for assets referenced in the design specification (e.g., background images, icons).

**Key Functions:**

*   **`load_asset(asset_path: str, target_dir: str) -> str`**
    *   **Signature:** `load_asset(asset_path: str, target_dir: str) -> str`
    *   **Description:** Copies an external asset file from the source path to the designated output directory and returns the relative path to the copied file.
    *   **Example Usage:**
        ```python
        from image_loader import load_asset
        # Copies 'assets/logo.png' into the 'static/' folder and returns 'static/logo.png'
        image_path = load_asset("assets/logo.png", "static/")
        ```

### `layout_detector.py`

Analyzes the component structure within the design specification to infer optimal CSS layout strategies (e.g., determining if a section should use Flexbox or Grid).

**Key Functions:**

*   **`analyze_component_layout(component: dict) -> dict`**
    *   **Signature:** `analyze_component_layout(component: dict) -> dict`
    *   **Description:** Takes a single component definition and returns an augmented dictionary containing layout hints (e.g., `layout_type: "flex"`, `direction: "row"`).
    *   **Example Usage:**
        ```python
        from layout_detector import analyze_component_layout
        component_def = {"type": "navbar", "children": [...]}
        layout_hints = analyze_component_layout(component_def)
        # layout_hints might contain {"layout_type": "flex", "justify_content": "space-between"}
        ```

### `color_extractor.py`

Parses the color definitions from the design specification and generates a standardized CSS variable map for easy use in the generated stylesheet.

**Key Functions:**

*   **`extract_color_palette(spec: DesignSpec) -> dict`**
    *   **Signature:** `extract_color_palette(spec: DesignSpec) -> dict`
    *   **Description:** Scans `global_styles` and component-specific styles to compile a comprehensive dictionary of CSS variables (e.g., `--color-primary: #007bff;`).
    *   **Example Usage:**
        ```python
        from color_extractor import extract_color_palette
        palette = extract_color_palette(design_spec)
        # palette = {"--color-primary": "#007bff", "--color-text": "#333"}
        ```

### `html_generator.py`

Responsible for constructing the semantic HTML structure (`index.html`) based on the parsed design specification.

**Key Functions:**

*   **`generate_html(spec: DesignSpec, static_path: str) -> str`**
    *   **Signature:** `generate_html(spec: DesignSpec, static_path: str) -> str`
    *   **Description:** Renders the entire design into a complete HTML string, embedding necessary links to CSS and JS, and inserting component markup.
    *   **Example Usage:**
        ```python
        from html_generator import generate_html
        html_content = generate_html(design_spec, "static/")
        # html_content is a string containing the full index.html content
        ```

### `generate_css.py` (Implied/Combined with `html_generator.py` for simplicity, but conceptually separate)

Generates the styling rules (`style.css`) by combining global styles, extracted color variables, and layout rules.

**Key Functions:**

*   **`generate_css(spec: DesignSpec, color_map: dict) -> str`**
    *   **Signature:** `generate_css(spec: DesignSpec, color_map: dict) -> str`
    *   **Description:** Creates the CSS content, applying flexbox/grid rules derived from `layout_detector` and utilizing variables from `color_extractor`.
    *   **Example Usage:**
        ```python
        from generate_css import generate_css
        css_content = generate_css(design_spec, palette)
        # css_content is a string containing the full style.css content
        ```

### `output_writer.py`

Manages the final persistence of the generated files (HTML, CSS, JS, assets) into the target output directory.

**Key Functions:**

*   **`write_file(file_path: str, content: str)`**
    *   **Signature:** `write_file(file_path: str, content: str)`
    *   **Description:** Writes the provided string content to the specified file path, creating directories if necessary.
    *   **Example Usage:**
        ```python
        from output_writer import write_file
        write_file("dist/index.html", html_content)
        write_file("dist/style.css", css_content)
        ```

### `main.py` (Entry Point)

The primary executable script that orchestrates the entire conversion pipeline.

**Key Functions:**

*   **`main(json_path: str, output_dir: str)`**
    *   **Signature:** `main(json_path: str, output_dir: str)`
    *   **Description:** The main CLI entry point. It reads the spec, runs all processing modules in sequence, and writes the final output.
    *   **Example Usage (CLI):**
        ```bash
        python main.py design_spec.json ./dist
        ```

---

## Testing Infrastructure

### `tests/__init__.py`

(Empty module, used to mark the directory as a Python package.)

### `tests/conftest.py`

Contains pytest fixtures that are automatically discovered and shared across test modules.

**Key Fixtures:**

*   **`mock_design_spec`**
    *   **Description:** A pre-defined, valid `DesignSpec` object used for testing generation logic without needing external files.
    *   **Example Usage:** Used implicitly by tests.

### `tests/fixtures/__init__.py`

(Empty module, used to mark the directory as a Python package.)