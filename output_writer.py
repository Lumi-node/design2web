"""HTML output writer module for design-to-HTML converter.

This module handles validating and writing HTML content to disk.
It validates HTML structure, creates output directories, and ensures
proper file encoding and error handling.
"""

import os
import sys
import importlib.util
from html.parser import HTMLParser
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

OutputWriteError = project_types.OutputWriteError


def write_output(html_content: str, output_dir: str = "./output") -> str:
    """
    Validate HTML and write to index.html in output directory.

    Args:
        html_content: Complete HTML string (with DOCTYPE, head, body, style tag)
        output_dir: Directory to write to (default "./output")
                   Relative paths are relative to CWD

    Returns:
        Absolute path string to written index.html file
        Format: /absolute/path/to/output/index.html (Unix-style)

    Raises:
        ValueError: If html_content is empty
            Message: "html_content cannot be empty"

        OutputWriteError: If validation or writing fails
            - HTML parse failure: "Invalid HTML: {parse_error_detail}"
            - Directory creation failure: "Failed to create output directory {path}: {os_error}"
            - File write failure: "Failed to write index.html: {os_error}"
    """
    # Step 1: Input Validation
    if not html_content:
        raise ValueError("html_content cannot be empty")

    # Step 2: HTML Parsing Validation
    parser = HTMLParser()
    try:
        parser.feed(html_content)
    except Exception as e:
        raise OutputWriteError(f"Invalid HTML: {str(e)}")

    # Step 3: Directory Creation
    try:
        abs_output_dir = os.path.abspath(output_dir)
        os.makedirs(abs_output_dir, exist_ok=True)
    except OSError as e:
        raise OutputWriteError(
            f"Failed to create output directory {output_dir}: {str(e)}"
        )

    # Step 4: File Writing
    file_path = os.path.join(abs_output_dir, "index.html")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    except OSError as e:
        raise OutputWriteError(f"Failed to write index.html: {str(e)}")

    # Step 5: Return Absolute Path
    return os.path.abspath(file_path)
