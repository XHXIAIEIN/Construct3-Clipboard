"""Print a placeholder PNG as a data URI for use in imageData arrays.

Usage:
    python scripts/imagedata.py --color red --width 32 --height 32
    python scripts/imagedata.py --color "#3366FF" --width 16 --height 16 --shape circle

Colors are the names in src/imagedata/generator.py or #RRGGBB / #RRGGBBAA.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.imagedata.generator import COLORS, generate_placeholder  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--color", default="gray", help=f"named color ({', '.join(COLORS)}) or hex")
    parser.add_argument("--width", type=int, default=32)
    parser.add_argument("--height", type=int, default=32)
    parser.add_argument("--shape", choices=["rectangle", "circle"], default="rectangle")
    args = parser.parse_args(argv)
    try:
        uri = generate_placeholder(width=args.width, height=args.height, color=args.color, shape=args.shape)
    except ValueError as exc:
        sys.exit(str(exc))
    print(uri)
    return 0


if __name__ == "__main__":
    sys.exit(main())
