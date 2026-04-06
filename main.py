"""Main entry point orchestrating the design-to-HTML conversion pipeline.

This module provides the convert_design function that coordinates all stages
of converting a design mockup image to semantic HTML5 with flexbox CSS.
"""

import sys
import importlib.util
from pathlib import Path

# Load types module by file path to avoid conflict with stdlib types
if 'project_types' not in sys.modules:
    types_path = Path(__file__).parent / "types.py"
    spec = importlib.util.spec_from_file_location("project_types", str(types_path))
    project_types = importlib.util.module_from_spec(spec)
    sys.modules['project_types'] = project_types
    spec.loader.exec_module(project_types)
else:
    project_types = sys.modules['project_types']

DesignToHTMLError = project_types.DesignToHTMLError


def convert_design(image_path: str) -> str:
    """
    Convert a design mockup image to HTML+CSS.

    This is the primary entry point. Given a PNG or JPG image of a design mockup,
    generates a semantic HTML5 page with flexbox CSS that approximates the layout
    and color scheme.

    Args:
        image_path: Path (absolute or relative) to PNG or JPG design mockup image.

    Returns:
        Absolute path string to generated index.html file.
        File is created in ./output/ directory (default).

    Raises:
        FileNotFoundError: If image_path file doesn't exist
            Message format: "Image file not found: {image_path}"
            Propagated from load_image()

        ValueError: If image format invalid or dimensions out of range
            Message format: "..." (from load_image())
            Propagated from load_image()

        DesignToHTMLError: If any stage after load_image fails
            Wraps specific errors with context about which stage failed

    Pipeline Stages (in order):

    1. **Image Loading**
       - Call load_image(image_path)
       - Raises FileNotFoundError, ValueError
       - Returns: numpy array (H, W, 3) uint8
       - **CRITICAL**: Extract and store image dimensions for CSS generation
         * image_height = array.shape[0]  (H = rows)
         * image_width = array.shape[1]   (W = columns)

    2. **Layout Detection**
       - Call detect_layout_regions(image)
       - Returns: dict with keys 'header', 'sidebar', 'content', 'footer'

    3. **Color Extraction**
       - Call extract_colors(image, regions)
       - Returns: dict mapping region names to [color1, color2, color3]

    4. **HTML/CSS Generation**
       - Call generate_html_structure(regions)
       - Call generate_css(regions, colors, image_width, image_height)
       - Combine into complete HTML (with <style> tag)

    5. **Output Writing**
       - Call write_output(html_content, "./output")
       - Returns: absolute path to index.html

    6. **Return**
       - Return absolute path

    Error Handling:
    - Propagate FileNotFoundError and ValueError directly
    - Catch other exceptions and wrap in DesignToHTMLError with stage context
    - Example: "Conversion failed at layout detection stage: {original_error}"

    Usage Example:

        from main import convert_design

        try:
            html_path = convert_design("mockup.png")
            print(f"Generated: {html_path}")
        except FileNotFoundError as e:
            print(f"Image not found: {e}")
        except ValueError as e:
            print(f"Invalid image: {e}")
        except DesignToHTMLError as e:
            print(f"Conversion failed: {e}")
    """
    # Import pipeline modules here to allow monkeypatching in tests
    from image_loader import load_image
    from layout_detector import detect_layout_regions
    from color_extractor import extract_colors
    from html_generator import generate_html_structure, generate_css
    from output_writer import write_output

    try:
        # Stage 1: Image Loading
        # This stage may raise FileNotFoundError or ValueError which we propagate
        image = load_image(image_path)

        # Extract image dimensions for CSS generation
        # image.shape is (height, width, 3) for a 3-channel image
        image_height = image.shape[0]  # Number of rows
        image_width = image.shape[1]   # Number of columns

    except (FileNotFoundError, ValueError):
        # Propagate file not found and value errors directly
        raise
    except Exception as e:
        # Wrap any other exceptions from image loading
        raise DesignToHTMLError(f"Conversion failed at image loading stage: {str(e)}")

    try:
        # Stage 2: Layout Detection
        regions = detect_layout_regions(image)

    except DesignToHTMLError:
        # Re-raise module-specific errors
        raise
    except Exception as e:
        raise DesignToHTMLError(f"Conversion failed at layout detection stage: {str(e)}")

    try:
        # Stage 3: Color Extraction
        colors = extract_colors(image, regions)

    except DesignToHTMLError:
        # Re-raise module-specific errors
        raise
    except Exception as e:
        raise DesignToHTMLError(f"Conversion failed at color extraction stage: {str(e)}")

    try:
        # Stage 4: HTML and CSS Generation
        # Generate HTML structure (without styles)
        html_structure = generate_html_structure(regions)

        # Generate CSS with dimensions
        css = generate_css(regions, colors, image_width, image_height)

        # Combine HTML and CSS
        # Insert CSS into the <style> tag within <head>
        combined_html = _insert_css_into_html(html_structure, css)

    except DesignToHTMLError:
        # Re-raise module-specific errors
        raise
    except Exception as e:
        raise DesignToHTMLError(f"Conversion failed at HTML/CSS generation stage: {str(e)}")

    try:
        # Stage 5: Output Writing
        output_path = write_output(combined_html, "./output")

    except Exception as e:
        raise DesignToHTMLError(f"Conversion failed at output writing stage: {str(e)}")

    # Return the absolute path to the generated HTML file
    return output_path


def _insert_css_into_html(html_structure: str, css: str) -> str:
    """
    Insert CSS into the HTML structure within a <style> tag in the <head>.

    Args:
        html_structure: HTML string generated by generate_html_structure()
        css: CSS string generated by generate_css()

    Returns:
        Complete HTML string with CSS inserted in <style> tag within <head>

    Implementation:
    - Find the closing </head> tag
    - Insert <style>css_content</style> before </head>
    - Return complete HTML
    """
    # Find the position of </head>
    head_close = html_structure.find("</head>")
    if head_close == -1:
        raise ValueError("HTML structure missing </head> tag")

    # Insert the style tag with CSS content before </head>
    style_tag = f"\n    <style>\n{css}\n    </style>"
    combined = html_structure[:head_close] + style_tag + "\n" + html_structure[head_close:]

    return combined
