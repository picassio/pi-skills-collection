# Getting True Transparency from AI-Generated Images

AI image models always output RGB — never real RGBA with alpha. To get proper transparency for sprites, icons, and game assets, you need the right prompting strategy and post-processing.

---

## The Golden Rule

> **Prompt for SOLID WHITE BACKGROUND, then remove the white.**

❌ Don't: `"transparent background"` → baked checker pattern, variable colors, hard to remove  
✅ Do: `"SOLID WHITE BACKGROUND (#FFFFFF)"` → trivial flood-fill removal

---

## Why "Transparent Background" Fails

When you prompt for "transparent background", Gemini models render a **fake checker pattern** baked into the RGB pixels:

- The pattern alternates between two gray tones (e.g., `(48,48,48)` and `(104,104,104)`)
- The checker colors **vary per image** — light subjects get light checkers, dark subjects get dark checkers
- Dark character elements (hair, clothing, accessories) blend into dark checker squares
- The checker square size varies (10px–32px) across images
- There is **no actual alpha channel** — just painted gray squares

This makes automated removal extremely fragile. You'd need to detect variable checker colors, handle different square sizes, and risk eating into character details.

---

## The Solution: White Background + `remove-bg.py`

### Step 1: Prompt Correctly

Include this in every prompt that needs transparency:

```
SOLID WHITE BACKGROUND (#FFFFFF). Do NOT use a checkerboard or gradient background.
```

Full example:
```
Cute chibi character in cartoon style. Big round head, dot eyes with sparkle 
highlights, rosy cheeks. SOLID WHITE BACKGROUND (#FFFFFF). Do NOT use a 
checkerboard or gradient background. Clean black outlines. Game-ready sprite.
```

### Step 2: Remove the White

```bash
# Install requirements (one-time)
pip install Pillow numpy scipy

# Single file — overwrites in place
python3 ~/.pi/agent/skills/nanobana-pro/scripts/remove-bg.py sprite.png

# Batch — whole directory
python3 ~/.pi/agent/skills/nanobana-pro/scripts/remove-bg.py --dir ./characters/

# Preview without overwriting
python3 ~/.pi/agent/skills/nanobana-pro/scripts/remove-bg.py --preview sprite.png
# → saves sprite_transparent.png

# Dry run
python3 ~/.pi/agent/skills/nanobana-pro/scripts/remove-bg.py --dry-run *.png
```

### Step 3: Verify

```python
from PIL import Image
img = Image.open("sprite.png")
print(img.mode)  # Should be "RGBA"
```

---

## `remove-bg.py` Reference

### How It Works

1. Find all near-white pixels (within color distance tolerance of `#FFFFFF`)
2. Label connected components using scipy `ndimage.label` (8-connected)
3. **Only remove components touching the image border** — this preserves white elements inside the character (eyes, teeth, paper, highlights)
4. Smooth alpha edges with Gaussian blur + threshold for clean anti-aliasing

### Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--color` / `-c` | `255,255,255` | Background color to remove (R,G,B or #RRGGBB) |
| `--tolerance` / `-t` | 30 | Color distance threshold |
| `--preview` | off | Save as `*_transparent.png` instead of overwriting |
| `--dry-run` | off | Report results without modifying files |
| `--quiet` / `-q` | off | Only print errors |
| `--dir` / `-d` | — | Process all image files in a directory |

### Non-White Backgrounds

For other solid backgrounds, specify the color:

```bash
# Remove black background
python3 remove-bg.py --color 0,0,0 sprite.png

# Remove hex color
python3 remove-bg.py --color "#336699" sprite.png

# Remove green screen
python3 remove-bg.py --color 0,255,0 --tolerance 40 sprite.png
```

### Tolerance Tuning

| Tolerance | Effect |
|-----------|--------|
| 15-20 | Conservative — tight match, may leave faint halo |
| **30** | **Default — good balance for white backgrounds** |
| 40-50 | Aggressive — catches off-white shadows but may eat into pale character edges |

---

## Pipeline Integration

### Generate + Fix in One Step

```bash
# Generate with white background
python3 ~/.pi/agent/skills/nanobana-pro/scripts/generate-image.py \
  --prompt "A cute robot character, chibi style, SOLID WHITE BACKGROUND" \
  --output robot.png

# Remove white background
python3 ~/.pi/agent/skills/nanobana-pro/scripts/remove-bg.py robot.png
```

### Batch Character Generation

```bash
#!/bin/bash
NAMES=("warrior" "mage" "archer" "healer")
STYLE="chibi style, SOLID WHITE BACKGROUND (#FFFFFF), clean black outlines, game sprite"

for name in "${NAMES[@]}"; do
  python3 ~/.pi/agent/skills/nanobana-pro/scripts/generate-image.py \
    --prompt "A $name character, $STYLE" \
    --output "characters/${name}.png"
done

# Remove white backgrounds from all
python3 ~/.pi/agent/skills/nanobana-pro/scripts/remove-bg.py --dir characters/
```

### Programmatic Use

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.pi/agent/skills/nanobana-pro/scripts"))
from remove_bg import remove_background

result = remove_background("sprite.png", tolerance=30)
print(f"Removed {result['transparent_pct']:.0f}% background")
```

---

## Troubleshooting

### White Halo Around Character

**Cause**: Off-white pixels at edges not caught by tolerance.  
**Fix**: Raise tolerance: `--tolerance 40`

### White Parts of Character Becoming Transparent

**Cause**: White teeth, eyes, or paper touching the image border.  
**Fix**: Lower tolerance `--tolerance 20`, or add padding to the image so the character doesn't touch edges.

### Model Still Produces Checkers

Some prompts override the white background instruction. Reinforce with:
```
SOLID WHITE BACKGROUND (#FFFFFF). Do NOT use a checkerboard pattern. 
Do NOT use a gradient. The background must be pure flat white.
```

### Already Have Checker Images?

The legacy `remove-checker-bg.py` script attempts to detect and remove checker patterns, but it's unreliable for images with dark subjects. **Prefer regenerating with white backgrounds** — it costs the same and produces clean results every time.

---

## Models and Background Behavior

| Model | "transparent bg" | "white bg" | Notes |
|-------|-----------------|------------|-------|
| `gemini-3.1-flash-image-preview` | Baked checker (RGB) | Clean white (RGB) | ✅ **Default** — white bg works great |
| `gemini-3-pro-image-preview` | Baked checker (RGB) | Clean white (RGB) | ✅ White bg works great |
| `gemini-2.5-flash-image` | Baked checker (RGB) | Clean white (RGB) | ✅ White bg works great |
| `gpt-5-image` | Sometimes real RGBA | Clean white | Check `.mode` first |
| `gpt-5-image-mini` | Sometimes real RGBA | Clean white | Check `.mode` first |
| Flux models | Solid color bg | Solid color bg | Always needs removal |

**Bottom line**: Always prompt for white background. Always run `remove-bg.py`. It's fast, reliable, and works with every model.
