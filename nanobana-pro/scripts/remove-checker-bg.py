#!/usr/bin/env python3
"""
Nanobana Pro — Remove Baked Checker Backgrounds

AI image models (especially Gemini) often render a fake transparency checker
pattern baked into the RGB pixels instead of producing actual alpha. This script
detects and removes that pattern, producing proper RGBA PNGs.

Algorithm:
  1. Sample checker colors from corner pixels (top-left 2×2 grid)
  2. Find all pixels within color tolerance of either checker color
  3. Label connected components (scipy ndimage)
  4. Only remove components touching the image border (flood-fill logic)
     — this preserves character pixels that happen to be similar gray tones
  5. Smooth alpha edges with Gaussian blur + threshold

Usage:
  # Single file
  python3 remove-checker-bg.py image.png

  # Multiple files
  python3 remove-checker-bg.py *.png

  # Entire directory
  python3 remove-checker-bg.py --dir ./generated/

  # Custom tolerance (default: 35, raise for stubborn backgrounds)
  python3 remove-checker-bg.py --tolerance 45 image.png

  # Preview mode — don't overwrite, save as *_transparent.png
  python3 remove-checker-bg.py --preview image.png

  # Dry run — report what would change without modifying files
  python3 remove-checker-bg.py --dry-run *.png

Requirements:
  pip install Pillow numpy scipy
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage


def detect_checker_colors(data, sample_offset=4, sample_spacing=16):
    """Sample the two alternating checker colors from corner pixels.

    Args:
        data: numpy array (H, W, 3) float32
        sample_offset: pixels from edge to sample (avoids anti-aliased borders)
        sample_spacing: expected checker square size (typically 16px)

    Returns:
        (color1, color2) as numpy arrays of shape (3,)
    """
    o = sample_offset
    s = sample_spacing
    c1 = data[o, o, :3].copy()
    c2 = data[o, o + s, :3].copy()

    # If the two samples are nearly identical, the grid might be offset —
    # try sampling vertically instead
    if np.sqrt(np.sum((c1 - c2) ** 2)) < 8:
        c2 = data[o + s, o, :3].copy()

    # Still identical? Try diagonal
    if np.sqrt(np.sum((c1 - c2) ** 2)) < 8:
        c2 = data[o + s, o + s, :3].copy()

    return c1, c2


def remove_checker_background(
    img_path,
    output_path=None,
    tolerance=35,
    blur_radius=1.2,
    alpha_high=200,
    alpha_low=30,
    dry_run=False,
):
    """Remove baked checker background from an image.

    Args:
        img_path: path to input PNG
        output_path: path to save result (defaults to overwriting input)
        tolerance: color distance threshold for checker detection (0-255)
        blur_radius: Gaussian blur radius for alpha edge smoothing
        alpha_high: threshold above which alpha becomes 255 (opaque)
        alpha_low: threshold below which alpha becomes 0 (transparent)
        dry_run: if True, only report results without saving

    Returns:
        dict with 'transparent_pct', 'checker_colors', 'already_rgba'
    """
    img = Image.open(img_path)
    result = {"already_rgba": img.mode == "RGBA", "path": img_path}

    # Convert to RGB for processing (ignore existing alpha if any)
    rgb = img.convert("RGB")
    data = np.array(rgb).astype(np.float32)
    h, w = data.shape[:2]

    # Detect checker colors from corners
    c1, c2 = detect_checker_colors(data)
    result["checker_colors"] = (c1.tolist(), c2.tolist())

    # Distance to nearest checker color for every pixel
    d1 = np.sqrt(np.sum((data[:, :, :3] - c1) ** 2, axis=2))
    d2 = np.sqrt(np.sum((data[:, :, :3] - c2) ** 2, axis=2))
    near_checker = np.minimum(d1, d2) < tolerance

    # Label connected components of checker-like pixels
    labeled, num_features = ndimage.label(near_checker)

    # Find which components touch any border edge — only those are background
    border_labels = set()
    border_labels.update(labeled[0, :].tolist())  # top row
    border_labels.update(labeled[-1, :].tolist())  # bottom row
    border_labels.update(labeled[:, 0].tolist())  # left column
    border_labels.update(labeled[:, -1].tolist())  # right column
    border_labels.discard(0)  # label 0 = not part of any component

    # Background mask: only border-connected checker components
    bg_mask = np.isin(labeled, list(border_labels))

    # Build alpha channel
    alpha = np.where(bg_mask, np.uint8(0), np.uint8(255))

    # Smooth alpha edges for clean anti-aliasing
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


def main():
    parser = argparse.ArgumentParser(
        description="Remove baked checker-pattern backgrounds from AI-generated images"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Image files to process",
    )
    parser.add_argument(
        "--dir",
        "-d",
        help="Process all PNGs in a directory",
    )
    parser.add_argument(
        "--tolerance",
        "-t",
        type=int,
        default=35,
        help="Color distance threshold for checker detection (default: 35)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Save as *_transparent.png instead of overwriting",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without modifying files",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only print errors",
    )

    args = parser.parse_args()

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

    # Process each file
    processed = 0
    for path in files:
        if not os.path.exists(path):
            print(f"Warning: {path} not found, skipping", file=sys.stderr)
            continue

        # Determine output path
        if args.preview:
            base, ext = os.path.splitext(path)
            output = f"{base}_transparent.png"
        else:
            output = None  # overwrite in place

        result = remove_checker_background(
            path,
            output_path=output,
            tolerance=args.tolerance,
            dry_run=args.dry_run,
        )

        processed += 1
        if not args.quiet:
            c1, c2 = result["checker_colors"]
            c1_str = f"({c1[0]:.0f},{c1[1]:.0f},{c1[2]:.0f})"
            c2_str = f"({c2[0]:.0f},{c2[1]:.0f},{c2[2]:.0f})"
            status = "DRY RUN" if args.dry_run else "saved"
            target = result.get("saved_to", path)
            print(
                f"{os.path.basename(path)}: "
                f"checker {c1_str}/{c2_str} → "
                f"{result['transparent_pct']:.0f}% transparent "
                f"[{status}]"
            )

    if not args.quiet:
        print(f"\nDone! Processed {processed} file(s).")


if __name__ == "__main__":
    main()
