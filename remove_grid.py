from __future__ import annotations

import argparse
from pathlib import Path
from statistics import median

from PIL import Image


def channel_median(values: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    return tuple(int(median(pixel[i] for pixel in values)) for i in range(3))


def remove_grid(input_path: Path, output_path: Path, cells: int = 64, scale: int = 1, sample_margin_ratio: float = 0.28) -> None:
    if cells <= 0:
        raise ValueError("cells must be positive")
    if scale <= 0:
        raise ValueError("scale must be positive")

    src = Image.open(input_path).convert("RGB")
    width, height = src.size
    if width != height:
        raise ValueError(f"expected a square image, got {width}x{height}")

    pixel_map = Image.new("RGB", (cells, cells))
    source_pixels = src.load()
    output_pixels = pixel_map.load()

    cell_size = width / cells
    margin = max(1, int(cell_size * sample_margin_ratio))

    for gy in range(cells):
        y0 = int(round(gy * cell_size))
        y1 = int(round((gy + 1) * cell_size))
        sample_y0 = min(max(y0 + margin, 0), height - 1)
        sample_y1 = min(max(y1 - margin, sample_y0 + 1), height)

        for gx in range(cells):
            x0 = int(round(gx * cell_size))
            x1 = int(round((gx + 1) * cell_size))
            sample_x0 = min(max(x0 + margin, 0), width - 1)
            sample_x1 = min(max(x1 - margin, sample_x0 + 1), width)

            samples: list[tuple[int, int, int]] = []
            for y in range(sample_y0, sample_y1):
                for x in range(sample_x0, sample_x1):
                    r, g, b = source_pixels[x, y]
                    # Ignore near-black grid remnants inside the sampled area.
                    if r + g + b > 60:
                        samples.append((r, g, b))

            if not samples:
                cx = min(width - 1, int(round((gx + 0.5) * cell_size)))
                cy = min(height - 1, int(round((gy + 0.5) * cell_size)))
                samples.append(source_pixels[cx, cy])

            output_pixels[gx, gy] = channel_median(samples)

    if scale != 1:
        resample = getattr(Image.Resampling, "NEAREST", Image.NEAREST)
        pixel_map = pixel_map.resize((cells * scale, cells * scale), resample=resample)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pixel_map.save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove a known square grid from generated pixel art by sampling cell interiors.")
    parser.add_argument("input", help="Input image with grid")
    parser.add_argument("output", help="Output image without grid")
    parser.add_argument("--cells", type=int, default=64, help="Number of grid cells per side")
    parser.add_argument("--scale", type=int, default=1, help="Nearest-neighbor upscale factor for output")
    parser.add_argument("--sample-margin-ratio", type=float, default=0.28, help="How much of each cell edge to ignore while sampling")
    args = parser.parse_args()

    remove_grid(
        Path(args.input),
        Path(args.output),
        cells=args.cells,
        scale=args.scale,
        sample_margin_ratio=args.sample_margin_ratio,
    )


if __name__ == "__main__":
    main()
