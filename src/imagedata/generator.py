"""Placeholder PNG image generator for C3 clipboard imageData."""
import base64
import io
from PIL import Image, ImageDraw

COLORS = {
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "yellow": (255, 255, 0, 255),
    "cyan": (0, 255, 255, 255),
    "magenta": (255, 0, 255, 255),
    "white": (255, 255, 255, 255),
    "black": (0, 0, 0, 255),
    "gray": (128, 128, 128, 255),
    "orange": (255, 165, 0, 255),
    "purple": (128, 0, 128, 255),
    "brown": (139, 69, 19, 255),
    "pink": (255, 192, 203, 255),
    "lime": (50, 205, 50, 255),
    "navy": (0, 0, 128, 255),
    "teal": (0, 128, 128, 255),
    "gold": (255, 215, 0, 255),
    "silver": (192, 192, 192, 255),
    "transparent": (0, 0, 0, 0),
}


def parse_color(color_str: str) -> tuple[int, int, int, int]:
    """Parse a color string into RGBA tuple.

    Args:
        color_str: Named color ('red'), hex color ('#FF8800' or '#FF880080'), or similar.

    Returns:
        RGBA tuple (r, g, b, a) with values 0-255.

    Raises:
        ValueError: If color string is invalid.
    """
    if color_str.lower() in COLORS:
        return COLORS[color_str.lower()]
    if color_str.startswith("#"):
        h = color_str[1:]
        if len(h) == 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
        if len(h) == 8:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
    raise ValueError(f"Invalid color: {color_str}")


def generate_placeholder(*, width: int = 32, height: int = 32, color: str = "gray", shape: str = "rectangle") -> str:
    """Generate a placeholder PNG image as a data URI.

    Args:
        width: Image width in pixels. Default 32.
        height: Image height in pixels. Default 32.
        color: Color as named color or hex (#RRGGBB or #RRGGBBAA). Default 'gray'.
        shape: 'rectangle' (filled) or 'circle'. Default 'rectangle'.

    Returns:
        Data URI string (data:image/png;base64,...)
    """
    rgba = parse_color(color)

    if shape == "circle":
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([0, 0, width - 1, height - 1], fill=rgba)
    else:
        img = Image.new("RGBA", (width, height), rgba)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"
