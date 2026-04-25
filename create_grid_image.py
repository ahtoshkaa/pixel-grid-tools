from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    )


def write_png_rgb(path: Path, width: int, height: int, pixels: bytearray) -> None:
    stride = width * 3
    rows = bytearray()
    for y in range(height):
        rows.append(0)  # PNG filter type: none
        start = y * stride
        rows.extend(pixels[start : start + stride])

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", ihdr)
    png += png_chunk(b"IDAT", zlib.compress(bytes(rows), level=9))
    png += png_chunk(b"IEND", b"")
    path.write_bytes(png)


def create_grid(
    output: Path,
    size: int = 1024,
    cells: int = 64,
    line_width: int = 1,
) -> None:
    if size <= 0:
        raise ValueError("size must be positive")
    if cells <= 0:
        raise ValueError("cells must be positive")
    if line_width <= 0:
        raise ValueError("line width must be positive")

    width = height = size
    pixels = bytearray([255] * width * height * 3)

    line_positions = {round(i * (size - 1) / cells) for i in range(cells + 1)}

    for pos in line_positions:
        for offset in range(line_width):
            p = min(pos + offset, size - 1)

            row_start = p * width * 3
            for x in range(width):
                idx = row_start + x * 3
                pixels[idx : idx + 3] = b"\x00\x00\x00"

            for y in range(height):
                idx = (y * width + p) * 3
                pixels[idx : idx + 3] = b"\x00\x00\x00"

    write_png_rgb(output, width, height, pixels)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a white square PNG with a thin black grid.")
    parser.add_argument("output", nargs="?", default="grid_64x64.png", help="Output PNG path")
    parser.add_argument("--size", type=int, default=1024, help="Image width and height in pixels")
    parser.add_argument("--cells", type=int, default=64, help="Number of grid cells per side")
    parser.add_argument("--line-width", type=int, default=1, help="Grid line width in pixels")
    args = parser.parse_args()

    create_grid(Path(args.output), size=args.size, cells=args.cells, line_width=args.line_width)


if __name__ == "__main__":
    main()
