"""Tests for placeholder PNG imagedata generator."""
import base64
import pytest
from io import BytesIO
from PIL import Image
from src.imagedata.generator import (
    generate_placeholder,
    parse_color,
    COLORS,
)


class TestParseColor:
    def test_named_color_red(self):
        """Test parsing named color."""
        rgb = parse_color("red")
        assert rgb == (255, 0, 0, 255)

    def test_named_color_case_insensitive(self):
        """Test case-insensitive color names."""
        rgb = parse_color("RED")
        assert rgb == (255, 0, 0, 255)

    def test_hex_color_6_digit(self):
        """Test parsing 6-digit hex color."""
        rgb = parse_color("#FF8800")
        assert rgb == (255, 136, 0, 255)

    def test_hex_color_8_digit(self):
        """Test parsing 8-digit hex color with alpha."""
        rgb = parse_color("#FF880080")
        assert rgb == (255, 136, 0, 128)

    def test_invalid_color_raises(self):
        """Test that invalid color raises ValueError."""
        with pytest.raises(ValueError, match="Invalid color"):
            parse_color("notacolor")


class TestColorsDict:
    def test_colors_dict_has_red(self):
        """Test that COLORS dict contains red."""
        assert "red" in COLORS
        assert COLORS["red"] == (255, 0, 0, 255)

    def test_colors_dict_has_blue(self):
        """Test that COLORS dict contains blue."""
        assert "blue" in COLORS
        assert COLORS["blue"] == (0, 0, 255, 255)


class TestGeneratePlaceholder:
    def test_returns_data_uri(self):
        """Test that output is a valid data URI."""
        result = generate_placeholder()
        assert result.startswith("data:image/png;base64,")

    def test_custom_color_red(self):
        """Test generating placeholder with red color."""
        result = generate_placeholder(color="red")
        assert result.startswith("data:image/png;base64,")
        # Decode and verify it's valid PNG
        b64_data = result.split(",")[1]
        png_data = base64.b64decode(b64_data)
        img = Image.open(BytesIO(png_data))
        # Red square should have red pixels
        pixel = img.getpixel((0, 0))
        assert pixel[0] > 200  # Red channel high

    def test_custom_size_64x64(self):
        """Test generating placeholder with custom size."""
        result = generate_placeholder(width=64, height=64)
        assert result.startswith("data:image/png;base64,")
        # Decode and verify PNG magic bytes and dimensions
        b64_data = result.split(",")[1]
        png_data = base64.b64decode(b64_data)
        # PNG magic bytes: 89 50 4E 47
        assert png_data[:4] == b"\x89PNG"
        # Verify dimensions
        img = Image.open(BytesIO(png_data))
        assert img.size == (64, 64)

    def test_circle_shape(self):
        """Test generating circle shape."""
        result = generate_placeholder(shape="circle", width=64, height=64)
        assert result.startswith("data:image/png;base64,")
        # Decode and verify it's a valid image
        b64_data = result.split(",")[1]
        png_data = base64.b64decode(b64_data)
        img = Image.open(BytesIO(png_data))
        assert img.size == (64, 64)
        # Circle should have transparent corners
        corner_pixel = img.getpixel((0, 0))
        assert corner_pixel[3] == 0  # Alpha channel is 0 (transparent)

    def test_hex_color(self):
        """Test generating with hex color."""
        result = generate_placeholder(color="#FF8800")
        assert result.startswith("data:image/png;base64,")
        # Verify color
        b64_data = result.split(",")[1]
        png_data = base64.b64decode(b64_data)
        img = Image.open(BytesIO(png_data))
        pixel = img.getpixel((0, 0))
        # Should be #FF8800
        assert pixel[0] == 255  # Red
        assert pixel[1] == 136  # Green
        assert pixel[2] == 0    # Blue

    def test_default_parameters(self):
        """Test that default parameters work."""
        result = generate_placeholder()
        assert result.startswith("data:image/png;base64,")
        b64_data = result.split(",")[1]
        png_data = base64.b64decode(b64_data)
        img = Image.open(BytesIO(png_data))
        # Default is 32x32
        assert img.size == (32, 32)
