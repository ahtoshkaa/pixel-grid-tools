# Pixel Grid Tools

Small Python tools for making a pixel-art prompt grid and removing that grid after an image generator fills it in.

## Example

Prompt used in ChatGPT:

```text
using the following grid create an pixel art image of a kitten playing with a ball. the colors should by contained by the grid and not bleed out.
```

Generated image on the grid:

![Generated kitten pixel art on a grid](examples/chatgpt-grid-preview.jpg)

Clean 64 by 64 pixel-art output:

![Clean 64 by 64 kitten pixel art](examples/clean-64x64.png)

Opened in Photoshop:

![Clean pixel art opened in Photoshop](examples/photoshop-preview.jpg)

## What this does

- `create_grid_image.py` creates a white square PNG with a thin black grid.
- `remove_grid.py` takes a generated image with that grid and rebuilds clean pixel art by sampling the inside of each cell.

The default grid is 64 by 64 cells.

## Install

Python is required. The grid creator uses only the Python standard library. The grid remover needs Pillow:

```powershell
pip install -r requirements.txt
```

Or install Pillow directly:

```powershell
pip install Pillow
```

## Create a blank 64 by 64 grid

```powershell
python create_grid_image.py
```

This creates:

```text
grid_64x64.png
```

You can customize it:

```powershell
python create_grid_image.py my_grid.png --size 1024 --cells 64 --line-width 1
```

## Remove the grid from a generated image

Example for an image generator output named `test1.png`:

```powershell
python remove_grid.py test1.png clean_64x64.png --cells 64
```

That creates a true 64 by 64 pixel-art image.

For an easier-to-view upscaled version:

```powershell
python remove_grid.py test1.png clean_1024.png --cells 64 --scale 16
```

`--scale 16` turns the 64 by 64 pixel map into a 1024 by 1024 preview using nearest-neighbor scaling, so the pixels stay sharp.

## Why this works

The cleanup script does not simply replace black pixels. Instead, it treats the grid as known geometry, samples the interior of each cell, ignores the grid lines, and reconstructs a clean image from the sampled colors.
