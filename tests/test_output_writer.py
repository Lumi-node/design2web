"""Tests for output_writer module.

Tests validate HTML output writing with proper error handling,
file I/O verification, and path resolution.
"""

import os
import pytest
import importlib.util
from pathlib import Path

# Import OutputWriteError from project types
spec = importlib.util.spec_from_file_location(
    "project_types",
    str(Path(__file__).parent.parent / "types.py")
)
project_types = importlib.util.module_from_spec(spec)
spec.loader.exec_module(project_types)

from output_writer import write_output


class TestWriteOutputValidHTML:
    """Test writing valid HTML to new directory."""

    def test_write_valid_html_to_new_directory(self, tmp_path):
        """Write valid HTML to a new directory and verify file exists."""
        output_dir = str(tmp_path / "output")
        html_content = "<!DOCTYPE html><html><head><title>Test</title></head><body></body></html>"

        result_path = write_output(html_content, output_dir)

        # Verify file exists
        assert os.path.exists(result_path)
        # Verify path is absolute
        assert os.path.isabs(result_path)
        # Verify file contains exact content
        with open(result_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert content == html_content


class TestWriteOutputExistingDirectory:
    """Test writing valid HTML to an existing directory."""

    def test_write_valid_html_to_existing_directory(self, tmp_path):
        """Write valid HTML to a directory that already exists."""
        output_dir = str(tmp_path / "output")
        os.makedirs(output_dir, exist_ok=True)

        html_content = "<!DOCTYPE html><html><body>Hello World</body></html>"
        result_path = write_output(html_content, output_dir)

        assert os.path.exists(result_path)
        with open(result_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert content == html_content


class TestWriteOutputEmptyContent:
    """Test rejection of empty HTML content."""

    def test_reject_empty_html_content(self, tmp_path):
        """Raise ValueError when html_content is empty string."""
        output_dir = str(tmp_path / "output")

        with pytest.raises(ValueError, match="html_content cannot be empty"):
            write_output("", output_dir)

    def test_reject_none_html_content(self, tmp_path):
        """Raise ValueError when html_content is None."""
        output_dir = str(tmp_path / "output")

        with pytest.raises(ValueError, match="html_content cannot be empty"):
            write_output(None, output_dir)


class TestWriteOutputInvalidHTML:
    """Test HTML validation via HTMLParser."""

    def test_valid_html_with_unclosed_tags_is_accepted(self, tmp_path):
        """HTMLParser accepts HTML with unclosed tags (it's lenient)."""
        output_dir = str(tmp_path / "output")
        # HTMLParser is lenient and accepts unclosed divs
        html_content = "<!DOCTYPE html><html><body><div></body></html>"

        # Should not raise - HTMLParser accepts this
        result_path = write_output(html_content, output_dir)
        assert os.path.exists(result_path)

    def test_incomplete_html_is_accepted(self, tmp_path):
        """HTMLParser accepts incomplete HTML (it's lenient)."""
        output_dir = str(tmp_path / "output")
        # HTMLParser is lenient with incomplete HTML
        html_content = "<!DOCTYPE html><html><head><title>Test"

        # Should not raise - HTMLParser accepts this
        result_path = write_output(html_content, output_dir)
        assert os.path.exists(result_path)


class TestWriteOutputPathHandling:
    """Test path resolution and formatting."""

    def test_returned_path_is_absolute(self, tmp_path):
        """Verify returned path is absolute."""
        output_dir = str(tmp_path / "output")
        html_content = "<!DOCTYPE html><html><body></body></html>"

        result_path = write_output(html_content, output_dir)

        assert os.path.isabs(result_path), f"Path {result_path} is not absolute"

    def test_returned_path_includes_index_html(self, tmp_path):
        """Verify returned path includes 'index.html'."""
        output_dir = str(tmp_path / "output")
        html_content = "<!DOCTYPE html><html><body></body></html>"

        result_path = write_output(html_content, output_dir)

        assert result_path.endswith("index.html")
        assert "output" in result_path


class TestWriteOutputNestedDirectories:
    """Test nested directory creation."""

    def test_create_nested_directories(self, tmp_path):
        """Create nested directories using makedirs."""
        output_dir = str(tmp_path / "a" / "b" / "c")
        html_content = "<!DOCTYPE html><html><body></body></html>"

        result_path = write_output(html_content, output_dir)

        assert os.path.exists(result_path)
        assert result_path.endswith("index.html")


class TestWriteOutputFileContent:
    """Test file content and encoding."""

    def test_file_contains_exact_content(self, tmp_path):
        """Verify file contains exact HTML content."""
        output_dir = str(tmp_path / "output")
        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test Page</title>
    <style>
        body { color: red; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hello</h1>
    </div>
</body>
</html>"""

        result_path = write_output(html_content, output_dir)

        with open(result_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert content == html_content

    def test_utf8_encoding_is_correct(self, tmp_path):
        """Verify file uses UTF-8 encoding."""
        output_dir = str(tmp_path / "output")
        # HTML with UTF-8 characters
        html_content = "<!DOCTYPE html><html><body>Héllo Wörld™</body></html>"

        result_path = write_output(html_content, output_dir)

        # Read back with UTF-8 encoding
        with open(result_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert content == html_content
        assert "Héllo" in content
        assert "Wörld™" in content


class TestWriteOutputFileReadability:
    """Test that file exists and is readable after function returns."""

    def test_file_exists_and_is_readable(self, tmp_path):
        """Verify file exists and is readable after function returns."""
        output_dir = str(tmp_path / "output")
        html_content = "<!DOCTYPE html><html><body>Test</body></html>"

        result_path = write_output(html_content, output_dir)

        # File should exist
        assert os.path.exists(result_path)
        # File should be readable
        assert os.path.isfile(result_path)
        # Should be able to read it
        with open(result_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 0


class TestWriteOutputDefaultDirectory:
    """Test default output directory behavior."""

    def test_write_with_default_output_directory(self, tmp_path, monkeypatch):
        """Test using default output directory './output'."""
        # Change to temp directory to avoid polluting project root
        monkeypatch.chdir(str(tmp_path))

        html_content = "<!DOCTYPE html><html><body></body></html>"

        result_path = write_output(html_content)

        # Should create ./output/index.html
        assert os.path.exists(result_path)
        assert result_path.endswith("index.html")
        assert os.path.isabs(result_path)

        # Clean up
        import shutil
        output_dir = str(tmp_path / "output")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)


class TestWriteOutputRelativePaths:
    """Test relative path resolution."""

    def test_relative_path_resolved_to_absolute(self, tmp_path, monkeypatch):
        """Relative paths should be resolved to absolute."""
        monkeypatch.chdir(str(tmp_path))

        html_content = "<!DOCTYPE html><html><body></body></html>"
        result_path = write_output(html_content, "./output")

        # Result path should be absolute
        assert os.path.isabs(result_path)
        # Should contain the resolved directory
        assert "output" in result_path

        # Clean up
        import shutil
        if os.path.exists(str(tmp_path / "output")):
            shutil.rmtree(str(tmp_path / "output"))


class TestWriteOutputComplexHTML:
    """Test writing complex valid HTML documents."""

    def test_write_complex_html_with_style_tag(self, tmp_path):
        """Write HTML with embedded CSS in style tag."""
        output_dir = str(tmp_path / "output")
        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Design to HTML</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            width: 100vw;
            height: 100vh;
        }
        .container {
            display: flex;
            flex-direction: column;
            width: 100vw;
            height: 100vh;
        }
        .header {
            display: flex;
            background-color: rgb(245, 200, 150);
            height: 15vh;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header"></div>
    </div>
</body>
</html>"""

        result_path = write_output(html_content, output_dir)

        assert os.path.exists(result_path)
        with open(result_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "<!DOCTYPE html>" in content
        assert "<style>" in content
        assert "rgb(245, 200, 150)" in content
