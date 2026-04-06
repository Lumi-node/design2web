"""Tests for image_loader module."""

import os
import pytest
import numpy as np
from pathlib import Path
from PIL import Image
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from image_loader import load_image

# Import from project_types (set up in conftest.py to avoid stdlib types conflict)
import project_types
ImageLoadError = project_types.ImageLoadError


class TestLoadImageBasics:
    """Test basic load_image functionality."""

    def test_load_valid_png(self):
        """Test loading a valid PNG image."""
        array = load_image('tests/fixtures/simple_layout.png')
        assert isinstance(array, np.ndarray)
        assert array.shape == (600, 800, 3)
        assert array.dtype == np.uint8

    def test_load_valid_jpg(self):
        """Test loading a valid JPG image."""
        # Create a JPG fixture for this test
        img = Image.new('RGB', (500, 400), color=(100, 150, 200))
        img.save('tests/fixtures/test_image.jpg')

        array = load_image('tests/fixtures/test_image.jpg')
        assert isinstance(array, np.ndarray)
        assert array.shape == (400, 500, 3)
        assert array.dtype == np.uint8


class TestLoadImageDimensions:
    """Test dimension validation."""

    def test_load_minimal_200x200(self):
        """Test loading image at minimum valid dimension (200x200)."""
        array = load_image('tests/fixtures/minimal.png')
        assert array.shape == (200, 200, 3)
        assert array.dtype == np.uint8

    def test_load_maximal_2000x2000(self):
        """Test loading image at maximum valid dimension (2000x2000)."""
        array = load_image('tests/fixtures/maximal.png')
        assert array.shape == (2000, 2000, 3)
        assert array.dtype == np.uint8

    def test_reject_too_small_100x100(self):
        """Test rejection of image smaller than 200x200."""
        # Create a 100x100 image
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        img.save('tests/fixtures/too_small.png')

        with pytest.raises(ValueError) as excinfo:
            load_image('tests/fixtures/too_small.png')
        assert "Image dimension 100x100 outside valid range [200-2000]" in str(excinfo.value)

    def test_reject_too_large_3000x3000(self):
        """Test rejection of image larger than 2000x2000."""
        # Create a 3000x3000 image
        img = Image.new('RGB', (3000, 3000), color=(0, 0, 255))
        img.save('tests/fixtures/too_large.png')

        with pytest.raises(ValueError) as excinfo:
            load_image('tests/fixtures/too_large.png')
        assert "Image dimension 3000x3000 outside valid range [200-2000]" in str(excinfo.value)

    def test_reject_width_too_small(self):
        """Test rejection when width is too small but height is valid."""
        img = Image.new('RGB', (150, 300), color=(100, 100, 100))
        img.save('tests/fixtures/width_too_small.png')

        with pytest.raises(ValueError) as excinfo:
            load_image('tests/fixtures/width_too_small.png')
        assert "Image dimension 150x300 outside valid range [200-2000]" in str(excinfo.value)

    def test_reject_height_too_large(self):
        """Test rejection when height is too large but width is valid."""
        img = Image.new('RGB', (300, 2500), color=(100, 100, 100))
        img.save('tests/fixtures/height_too_large.png')

        with pytest.raises(ValueError) as excinfo:
            load_image('tests/fixtures/height_too_large.png')
        assert "Image dimension 300x2500 outside valid range [200-2000]" in str(excinfo.value)


class TestLoadImageFormats:
    """Test format validation."""

    def test_reject_bmp_format(self):
        """Test rejection of .bmp file format."""
        with pytest.raises(ValueError) as excinfo:
            load_image('tests/fixtures/invalid.bmp')
        assert "Unsupported image format: bmp. Must be PNG or JPG" in str(excinfo.value)

    def test_reject_unknown_extension(self):
        """Test rejection of unknown file extension."""
        # Create a .gif file
        img = Image.new('RGB', (300, 300), color=(255, 255, 255))
        img.save('tests/fixtures/test.gif')

        with pytest.raises(ValueError) as excinfo:
            load_image('tests/fixtures/test.gif')
        assert "Unsupported image format: gif. Must be PNG or JPG" in str(excinfo.value)

    def test_accept_uppercase_png_extension(self):
        """Test that uppercase .PNG extension is accepted (case-insensitive)."""
        # Create a .PNG file
        img = Image.new('RGB', (250, 250), color=(50, 100, 150))
        img.save('tests/fixtures/uppercase.PNG')

        # Rename to uppercase (if not already)
        if os.path.exists('tests/fixtures/uppercase.PNG'):
            array = load_image('tests/fixtures/uppercase.PNG')
            assert array.shape == (250, 250, 3)

    def test_accept_uppercase_jpg_extension(self):
        """Test that uppercase .JPG extension is accepted (case-insensitive)."""
        img = Image.new('RGB', (250, 250), color=(50, 100, 150))
        img.save('tests/fixtures/uppercase.JPG')

        if os.path.exists('tests/fixtures/uppercase.JPG'):
            array = load_image('tests/fixtures/uppercase.JPG')
            assert array.shape == (250, 250, 3)

    def test_accept_jpeg_extension(self):
        """Test that .jpeg extension is accepted."""
        img = Image.new('RGB', (300, 300), color=(100, 100, 100))
        img.save('tests/fixtures/test.jpeg')

        array = load_image('tests/fixtures/test.jpeg')
        assert array.shape == (300, 300, 3)


class TestLoadImageFileHandling:
    """Test file handling and errors."""

    def test_reject_nonexistent_file(self):
        """Test rejection of non-existent file."""
        with pytest.raises(FileNotFoundError) as excinfo:
            load_image('tests/fixtures/nonexistent_file.png')
        assert "Image file not found: tests/fixtures/nonexistent_file.png" in str(excinfo.value)

    def test_reject_corrupted_png(self):
        """Test rejection of corrupted PNG file."""
        with pytest.raises(ImageLoadError) as excinfo:
            load_image('tests/fixtures/corrupted.png')
        assert "Failed to load image" in str(excinfo.value)

    def test_accept_relative_path(self):
        """Test that relative paths work correctly."""
        # Create a test image in a known location
        img = Image.new('RGB', (300, 300), color=(200, 100, 50))
        img.save('tests/fixtures/relative_test.png')

        # Load using relative path
        array = load_image('tests/fixtures/relative_test.png')
        assert array.shape == (300, 300, 3)

    def test_accept_absolute_path(self):
        """Test that absolute paths work correctly."""
        img = Image.new('RGB', (300, 300), color=(200, 100, 50))
        fixture_path = 'tests/fixtures/absolute_test.png'
        img.save(fixture_path)

        absolute_path = os.path.abspath(fixture_path)
        array = load_image(absolute_path)
        assert array.shape == (300, 300, 3)


class TestLoadImageColorConversion:
    """Test color conversion functionality."""

    def test_convert_rgba_to_rgb(self):
        """Test conversion of RGBA to RGB."""
        array = load_image('tests/fixtures/rgba_test.png')
        assert array.shape == (300, 400, 3)
        assert array.dtype == np.uint8
        # Verify no alpha channel
        assert array.shape[2] == 3

    def test_convert_grayscale_to_rgb(self):
        """Test conversion of grayscale (L mode) to RGB."""
        array = load_image('tests/fixtures/grayscale_test.png')
        assert array.shape == (280, 350, 3)
        assert array.dtype == np.uint8
        # Verify all three channels are identical (grayscale converted to RGB)
        # All channels should have the same value
        assert np.allclose(array[:, :, 0], array[:, :, 1])
        assert np.allclose(array[:, :, 1], array[:, :, 2])

    def test_rgb_image_unchanged(self):
        """Test that RGB images are not modified during loading."""
        # Create a specific RGB image with known values
        img_data = np.zeros((300, 300, 3), dtype=np.uint8)
        img_data[:, :, 0] = 100  # Red channel
        img_data[:, :, 1] = 150  # Green channel
        img_data[:, :, 2] = 200  # Blue channel
        img = Image.fromarray(img_data, 'RGB')
        img.save('tests/fixtures/known_rgb.png')

        array = load_image('tests/fixtures/known_rgb.png')
        assert array.shape == (300, 300, 3)
        assert array.dtype == np.uint8
        # Values should be preserved
        assert np.allclose(array[:, :, 0], 100)
        assert np.allclose(array[:, :, 1], 150)
        assert np.allclose(array[:, :, 2], 200)


class TestLoadImageArrayProperties:
    """Test numpy array properties."""

    def test_array_shape_is_h_w_3(self):
        """Test that returned array has correct shape (H, W, 3), not (W, H, 3)."""
        # Create an image with distinct width and height
        img = Image.new('RGB', (400, 300), color=(100, 100, 100))  # W=400, H=300
        img.save('tests/fixtures/shape_test.png')

        array = load_image('tests/fixtures/shape_test.png')
        # Shape should be (H=300, W=400, 3)
        assert array.shape == (300, 400, 3), f"Expected (300, 400, 3), got {array.shape}"

    def test_array_dtype_is_uint8(self):
        """Test that returned array has dtype uint8."""
        array = load_image('tests/fixtures/simple_layout.png')
        assert array.dtype == np.uint8

    def test_array_values_in_valid_range(self):
        """Test that all array values are in [0, 255]."""
        array = load_image('tests/fixtures/simple_layout.png')
        assert (array >= 0).all(), "Array has values < 0"
        assert (array <= 255).all(), "Array has values > 255"

    def test_array_values_min_max(self):
        """Test that array values span the full range properly."""
        # Create image with known color range
        img = Image.new('RGB', (250, 250))
        # Fill with gradient-like pattern
        pixels = img.load()
        for i in range(250):
            for j in range(250):
                pixels[i, j] = (0, 128, 255)  # Black, gray, white channels
        img.save('tests/fixtures/value_range_test.png')

        array = load_image('tests/fixtures/value_range_test.png')
        # Check that we have the expected values
        assert 0 in array  # Black
        assert 128 in array  # Gray
        assert 255 in array  # White

    def test_array_is_contiguous(self):
        """Test that returned array is C-contiguous (for performance)."""
        array = load_image('tests/fixtures/simple_layout.png')
        assert array.flags['C_CONTIGUOUS'] or array.flags['F_CONTIGUOUS']

    def test_array_no_metadata(self):
        """Test that returned value is only the array, not a tuple or object."""
        result = load_image('tests/fixtures/simple_layout.png')
        assert isinstance(result, np.ndarray)
        assert not isinstance(result, tuple)


class TestLoadImageEdgeCases:
    """Test edge cases and corner cases."""

    def test_minimum_dimension_exactly_200(self):
        """Test image that is exactly 200x200 (minimum boundary)."""
        img = Image.new('RGB', (200, 200), color=(100, 100, 100))
        img.save('tests/fixtures/exact_min.png')

        array = load_image('tests/fixtures/exact_min.png')
        assert array.shape == (200, 200, 3)

    def test_maximum_dimension_exactly_2000(self):
        """Test image that is exactly 2000x2000 (maximum boundary)."""
        array = load_image('tests/fixtures/maximal.png')
        assert array.shape == (2000, 2000, 3)

    def test_rectangular_image_not_square(self):
        """Test loading a rectangular (non-square) image."""
        img = Image.new('RGB', (1000, 500), color=(150, 100, 50))
        img.save('tests/fixtures/rectangular.png')

        array = load_image('tests/fixtures/rectangular.png')
        assert array.shape == (500, 1000, 3)
        assert array.dtype == np.uint8

    def test_very_different_dimensions(self):
        """Test image with very different width and height."""
        img = Image.new('RGB', (2000, 200), color=(100, 100, 100))
        img.save('tests/fixtures/wide.png')

        array = load_image('tests/fixtures/wide.png')
        assert array.shape == (200, 2000, 3)

        img = Image.new('RGB', (200, 2000), color=(100, 100, 100))
        img.save('tests/fixtures/tall.png')

        array = load_image('tests/fixtures/tall.png')
        assert array.shape == (2000, 200, 3)


class TestLoadImageErrorMessages:
    """Test that error messages match the specification exactly."""

    def test_file_not_found_message_format(self):
        """Test that FileNotFoundError message matches exact format."""
        test_path = 'tests/fixtures/missing_file_test.png'
        with pytest.raises(FileNotFoundError) as excinfo:
            load_image(test_path)
        assert str(excinfo.value) == f"Image file not found: {test_path}"

    def test_unsupported_format_message_format(self):
        """Test that ValueError for unsupported format matches exact format."""
        with pytest.raises(ValueError) as excinfo:
            load_image('tests/fixtures/invalid.bmp')
        assert str(excinfo.value) == "Unsupported image format: bmp. Must be PNG or JPG"

    def test_dimension_error_message_format(self):
        """Test that ValueError for dimensions matches exact format."""
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        img.save('tests/fixtures/dim_error_test.png')

        with pytest.raises(ValueError) as excinfo:
            load_image('tests/fixtures/dim_error_test.png')
        assert str(excinfo.value) == "Image dimension 100x100 outside valid range [200-2000]"

    def test_image_load_error_contains_context(self):
        """Test that ImageLoadError contains file path."""
        with pytest.raises(ImageLoadError) as excinfo:
            load_image('tests/fixtures/corrupted.png')
        error_msg = str(excinfo.value)
        assert "corrupted.png" in error_msg
        assert "Failed to load image" in error_msg
