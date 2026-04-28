#!/usr/bin/env python3
"""
Nanobana Pro — Remove Solid Backgrounds from AI-Generated Images

AI image models output RGB (no alpha channel). To get proper transparency:
  1. Prompt for "SOLID WHITE BACKGROUND (#FFFFFF)" (not "transparent background")
  2. Run this script to flood-fill remove the white and add real alpha

This is far more reliable than trying to detect variable checker patterns,
which models produce when you ask for "transparent background".

Algorithm:
  1. Find all near-white pixels (within tolerance of #FFFFFF)
  2. Label connected components (scipy ndimage, 8-connected)
  3. Only remove components touching the image border (background)
     — preserves white elements inside the character (eyes, teeth, etc.)
  4. Smooth alpha edges with Gaussian blur for clean anti-aliasing

Usage:
  python3 remove-bg.py sprite.png                     # overwrite in place
  python3 remove-bg.py *.png                           # batch
  python3 remove-bg.py --dir ./generated/              # whole directory
  python3 remove-bg.py --color 0,0,0 dark_bg.png      # remove black bg
  python3 remove-bg.py --tolerance 45 image.png        # wider threshold
  python3 remove-bg.py --preview image.png             # save as *_transparent.png
  python3 remove-bg.py --dry-run *.png                 # report without modifying

Requirements:
  pip install Pillow numpy scipy
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage


def remove_background(
    img_path,
    output_path=None,
    bg_color=(255, 255, 255),
    tolerance=30,
    blur_radius=1.2,
    alpha_high=200,
    alpha_low=30,
    dry_run=False,
):
    """Remove a solid-color background from an image via border flood fill.

    Args:
        img_path: path to input image
        output_path: path to save result (defaults to overwriting input)
        bg_color: background color to remove as (R, G, B) tuple
        tolerance: color distance threshold (0-255)
        blur_radius: Gaussian blur radius for alpha edge smoothing
        alpha_high: alpha values above this become 255 (fully opaque)
        alpha_low: alpha values below this become 0 (fully transparent)
        dry_run: if True, only report results without saving

    Returns:
        dict with 'transparent_pct', 'bg_color', 'saved_to'
    """
    img = Image.open(img_path).convert("RGB")
    data = np.array(img).astype(np.float32)
    h, w = data.shape[:2]

    result = {"path": img_path, "bg_color": bg_color}

    # Distance from target background color
    target = np.array(bg_color, dtype=np.float32)
    dist = np.sqrt(np.sum((data[:, :, :3] - target) ** 2, axis=2))
    near_bg = dist < tolerance

    # 8-connected component labeling
    struct = ndimage.generate_binary_structure(2, 2)
    labeled, num_features = ndimage.label(near_bg, structure=struct)

    # Only remove components touching any image border
    border_labels = set()
    border_labels.update(labeled[0, :].tolist())     # top
    border_labels.update(labeled[-1, :].tolist())    # bottom
    border_labels.update(labeled[:, 0].tolist())     # left
    border_labels.update(labeled[:, -1].tolist())    # right
    border_labels.discard(0)

    bg_mask = np.isin(labeled, list(border_labels))

    # Build alpha channel
    alpha = np.where(bg_mask, np.uint8(0), np.uint8(255))

    # Smooth edges for anti-aliasing
    rgba = np.dstack([data.astype(np.uint8), alpha])
    pil_rgba = Image.fromarray(rgba)
    r, g, b, a = pil_rgba.split()
    a = a.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    a_arr = np.array(a)
    a_arr = np.where(
        a_arr > alpha_high, 255, np.where(a_arr < alpha_low, 0, a_arr)
    ).astype(np.uint8)
    a = Image.fromarray(a_arr)
    pil_rgba = Image.merge("RGBA", (r, g, b, a))

    transparent_pct = (a_arr < 128).sum() / a_arr.size * 100
    result["transparent_pct"] = transparent_pct

    if not dry_run:
        save_path = output_path or img_path
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        pil_rgba.save(save_path)
        result["saved_to"] = save_path

    return result


def parse_color(s):
    """Parse color string like '255,255,255' or '#FFFFFF'."""
    s = s.strip()
    if s.startswith("#"):
        s = s[1:]
        return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
    parts = [int(x.strip()) for x in s.split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected R,G,B or #RRGGBB, got: {s}")
    return tuple(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Remove solid-color backgrounds from AI-generated images"
    )
    parser.add_argument("files", nargs="*", help="Image files to process")
    parser.add_argument("--dir", "-d", help="Process all images in a directory")
    parser.add_argument(
        "--color", "-c", default="255,255,255",
        help="Background color to remove: R,G,B or #RRGGBB (default: 255,255,255 white)",
    )
    parser.add_argument(
        "--tolerance", "-t", type=int, default=30,
        help="Color distance threshold (default: 30)",
    )
    parser.add_argument(
        "--preview", action="store_true",
        help="Save as *_transparent.png instead of overwriting",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report what would change without modifying files",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Only print errors",
    )

    args = parser.parse_args()
    bg_color = parse_color(args.color)

    # Collect files
    files = list(args.files or [])
    if args.dir:
        for fname in sorted(os.listdir(args.dir)):
            if fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                files.append(os.path.join(args.dir, fname))

    if not files:
        parser.print_help()
        print("\nError: No files specified. Provide files or use --dir.", file=sys.stderr)
        sys.exit(1)

    processed = 0
    for path in files:
        if not os.path.exists(path):
            print(f"Warning: {path} not found, skipping", file=sys.stderr)
            continue

        output = None
        if args.preview:
            base, ext = os.path.splitext(path)
            output = f"{base}_transparent.png"

        result = remove_background(
            path,
            output_path=output,
            bg_color=bg_color,
            tolerance=args.tolerance,
            dry_run=args.dry_run,
        )

        processed += 1
        if not args.quiet:
            status = "DRY RUN" if args.dry_run else "✓"
            print(
                f"{status} {os.path.basename(path)}: "
                f"{result['transparent_pct']:.0f}% transparent"
            )

    if not args.quiet:
        print(f"\nDone! Processed {processed} file(s).")


if __name__ == "__main__":
    main()
