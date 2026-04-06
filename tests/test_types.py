"""Test suite for exception types and error hierarchy.

Tests verify:
1. All exception classes exist and are importable
2. All exceptions inherit correctly from DesignToHTMLError
3. Exception hierarchy is complete (all 6 types)
4. Exceptions can be instantiated with messages
5. Exception messages are preserved and retrievable
6. All exceptions are proper Exception subclasses
"""

import pytest

# Use the project_types module configured in conftest.py
import project_types as types_module

DesignToHTMLError = types_module.DesignToHTMLError
ImageLoadError = types_module.ImageLoadError
LayoutDetectionError = types_module.LayoutDetectionError
ColorExtractionError = types_module.ColorExtractionError
HTMLGenerationError = types_module.HTMLGenerationError
OutputWriteError = types_module.OutputWriteError


class TestDesignToHTMLError:
    """Test base exception class."""

    def test_base_exception_is_exception(self):
        """DesignToHTMLError should be an Exception subclass."""
        assert issubclass(DesignToHTMLError, Exception)

    def test_base_exception_instantiation(self):
        """DesignToHTMLError should be instantiable."""
        exc = DesignToHTMLError("test message")
        assert isinstance(exc, Exception)
        assert isinstance(exc, DesignToHTMLError)

    def test_base_exception_message(self):
        """DesignToHTMLError should preserve and return message."""
        message = "Test error message"
        exc = DesignToHTMLError(message)
        assert str(exc) == message

    def test_base_exception_empty_message(self):
        """DesignToHTMLError should handle empty messages."""
        exc = DesignToHTMLError("")
        assert str(exc) == ""

    def test_base_exception_can_be_raised_and_caught(self):
        """DesignToHTMLError should be raisable and catchable."""
        with pytest.raises(DesignToHTMLError):
            raise DesignToHTMLError("test")


class TestImageLoadError:
    """Test ImageLoadError exception."""

    def test_image_load_error_is_design_to_html_error(self):
        """ImageLoadError should inherit from DesignToHTMLError."""
        assert issubclass(ImageLoadError, DesignToHTMLError)

    def test_image_load_error_is_exception(self):
        """ImageLoadError should be an Exception subclass."""
        assert issubclass(ImageLoadError, Exception)

    def test_image_load_error_instantiation(self):
        """ImageLoadError should be instantiable."""
        exc = ImageLoadError("Image file not found")
        assert isinstance(exc, ImageLoadError)
        assert isinstance(exc, DesignToHTMLError)
        assert isinstance(exc, Exception)

    def test_image_load_error_message(self):
        """ImageLoadError should preserve message."""
        message = "Image file not found: /path/to/file.png"
        exc = ImageLoadError(message)
        assert str(exc) == message

    def test_image_load_error_can_be_caught_as_design_to_html_error(self):
        """ImageLoadError should be catchable as DesignToHTMLError."""
        with pytest.raises(DesignToHTMLError):
            raise ImageLoadError("test")

    def test_image_load_error_can_be_caught_specifically(self):
        """ImageLoadError should be catchable specifically."""
        with pytest.raises(ImageLoadError):
            raise ImageLoadError("test")


class TestLayoutDetectionError:
    """Test LayoutDetectionError exception."""

    def test_layout_detection_error_is_design_to_html_error(self):
        """LayoutDetectionError should inherit from DesignToHTMLError."""
        assert issubclass(LayoutDetectionError, DesignToHTMLError)

    def test_layout_detection_error_is_exception(self):
        """LayoutDetectionError should be an Exception subclass."""
        assert issubclass(LayoutDetectionError, Exception)

    def test_layout_detection_error_instantiation(self):
        """LayoutDetectionError should be instantiable."""
        exc = LayoutDetectionError("Layout detection failed")
        assert isinstance(exc, LayoutDetectionError)
        assert isinstance(exc, DesignToHTMLError)
        assert isinstance(exc, Exception)

    def test_layout_detection_error_message(self):
        """LayoutDetectionError should preserve message."""
        message = "Layout detection failed: invalid image data"
        exc = LayoutDetectionError(message)
        assert str(exc) == message

    def test_layout_detection_error_can_be_caught_as_design_to_html_error(self):
        """LayoutDetectionError should be catchable as DesignToHTMLError."""
        with pytest.raises(DesignToHTMLError):
            raise LayoutDetectionError("test")

    def test_layout_detection_error_can_be_caught_specifically(self):
        """LayoutDetectionError should be catchable specifically."""
        with pytest.raises(LayoutDetectionError):
            raise LayoutDetectionError("test")


class TestColorExtractionError:
    """Test ColorExtractionError exception."""

    def test_color_extraction_error_is_design_to_html_error(self):
        """ColorExtractionError should inherit from DesignToHTMLError."""
        assert issubclass(ColorExtractionError, DesignToHTMLError)

    def test_color_extraction_error_is_exception(self):
        """ColorExtractionError should be an Exception subclass."""
        assert issubclass(ColorExtractionError, Exception)

    def test_color_extraction_error_instantiation(self):
        """ColorExtractionError should be instantiable."""
        exc = ColorExtractionError("Color extraction failed")
        assert isinstance(exc, ColorExtractionError)
        assert isinstance(exc, DesignToHTMLError)
        assert isinstance(exc, Exception)

    def test_color_extraction_error_message(self):
        """ColorExtractionError should preserve message."""
        message = "Color extraction failed for region header: clustering error"
        exc = ColorExtractionError(message)
        assert str(exc) == message

    def test_color_extraction_error_can_be_caught_as_design_to_html_error(self):
        """ColorExtractionError should be catchable as DesignToHTMLError."""
        with pytest.raises(DesignToHTMLError):
            raise ColorExtractionError("test")

    def test_color_extraction_error_can_be_caught_specifically(self):
        """ColorExtractionError should be catchable specifically."""
        with pytest.raises(ColorExtractionError):
            raise ColorExtractionError("test")


class TestHTMLGenerationError:
    """Test HTMLGenerationError exception."""

    def test_html_generation_error_is_design_to_html_error(self):
        """HTMLGenerationError should inherit from DesignToHTMLError."""
        assert issubclass(HTMLGenerationError, DesignToHTMLError)

    def test_html_generation_error_is_exception(self):
        """HTMLGenerationError should be an Exception subclass."""
        assert issubclass(HTMLGenerationError, Exception)

    def test_html_generation_error_instantiation(self):
        """HTMLGenerationError should be instantiable."""
        exc = HTMLGenerationError("HTML generation failed")
        assert isinstance(exc, HTMLGenerationError)
        assert isinstance(exc, DesignToHTMLError)
        assert isinstance(exc, Exception)

    def test_html_generation_error_message(self):
        """HTMLGenerationError should preserve message."""
        message = "HTML generation failed: invalid region data"
        exc = HTMLGenerationError(message)
        assert str(exc) == message

    def test_html_generation_error_can_be_caught_as_design_to_html_error(self):
        """HTMLGenerationError should be catchable as DesignToHTMLError."""
        with pytest.raises(DesignToHTMLError):
            raise HTMLGenerationError("test")

    def test_html_generation_error_can_be_caught_specifically(self):
        """HTMLGenerationError should be catchable specifically."""
        with pytest.raises(HTMLGenerationError):
            raise HTMLGenerationError("test")


class TestOutputWriteError:
    """Test OutputWriteError exception."""

    def test_output_write_error_is_design_to_html_error(self):
        """OutputWriteError should inherit from DesignToHTMLError."""
        assert issubclass(OutputWriteError, DesignToHTMLError)

    def test_output_write_error_is_exception(self):
        """OutputWriteError should be an Exception subclass."""
        assert issubclass(OutputWriteError, Exception)

    def test_output_write_error_instantiation(self):
        """OutputWriteError should be instantiable."""
        exc = OutputWriteError("File write failed")
        assert isinstance(exc, OutputWriteError)
        assert isinstance(exc, DesignToHTMLError)
        assert isinstance(exc, Exception)

    def test_output_write_error_message(self):
        """OutputWriteError should preserve message."""
        message = "Failed to write index.html: permission denied"
        exc = OutputWriteError(message)
        assert str(exc) == message

    def test_output_write_error_can_be_caught_as_design_to_html_error(self):
        """OutputWriteError should be catchable as DesignToHTMLError."""
        with pytest.raises(DesignToHTMLError):
            raise OutputWriteError("test")

    def test_output_write_error_can_be_caught_specifically(self):
        """OutputWriteError should be catchable specifically."""
        with pytest.raises(OutputWriteError):
            raise OutputWriteError("test")


class TestExceptionHierarchy:
    """Test the complete exception hierarchy."""

    def test_all_exceptions_inherit_from_design_to_html_error(self):
        """All specialized exceptions should inherit from DesignToHTMLError."""
        specialized_exceptions = [
            ImageLoadError,
            LayoutDetectionError,
            ColorExtractionError,
            HTMLGenerationError,
            OutputWriteError,
        ]
        for exc_class in specialized_exceptions:
            assert issubclass(exc_class, DesignToHTMLError)

    def test_all_exceptions_are_exception_subclasses(self):
        """All exceptions should be subclasses of Exception."""
        all_exceptions = [
            DesignToHTMLError,
            ImageLoadError,
            LayoutDetectionError,
            ColorExtractionError,
            HTMLGenerationError,
            OutputWriteError,
        ]
        for exc_class in all_exceptions:
            assert issubclass(exc_class, Exception)

    def test_catch_all_via_base_exception(self):
        """All exceptions should be catchable via DesignToHTMLError."""
        exceptions_to_raise = [
            ImageLoadError("test"),
            LayoutDetectionError("test"),
            ColorExtractionError("test"),
            HTMLGenerationError("test"),
            OutputWriteError("test"),
        ]
        for exc in exceptions_to_raise:
            with pytest.raises(DesignToHTMLError):
                raise exc

    def test_specific_exception_not_caught_by_sibling(self):
        """Specific exceptions should not be caught by unrelated exception types."""
        with pytest.raises(ImageLoadError):
            try:
                raise ImageLoadError("test")
            except LayoutDetectionError:
                pass

    def test_base_exception_not_caught_by_specialized(self):
        """Base exception should not be caught by specialized handlers."""
        with pytest.raises(DesignToHTMLError):
            try:
                raise DesignToHTMLError("test")
            except ImageLoadError:
                pass


class TestImportability:
    """Test that all exceptions are properly importable."""

    def test_import_all_from_types(self):
        """All exceptions should be importable from types module."""
        # This test verifies the imports at the top of the file work
        assert DesignToHTMLError is not None
        assert ImageLoadError is not None
        assert LayoutDetectionError is not None
        assert ColorExtractionError is not None
        assert HTMLGenerationError is not None
        assert OutputWriteError is not None

    def test_direct_import_from_types(self):
        """Each exception should be directly importable."""
        import project_types
        assert project_types.DesignToHTMLError is not None
        assert project_types.ImageLoadError is not None
        assert project_types.LayoutDetectionError is not None
        assert project_types.ColorExtractionError is not None
        assert project_types.HTMLGenerationError is not None
        assert project_types.OutputWriteError is not None
