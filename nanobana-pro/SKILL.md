---
name: nanobana-pro
description: >
  Generate images using AI models via OpenRouter API. Use when the user asks to
  generate, create, or make an image, picture, artwork, character design, background,
  texture, icon, or any visual asset. Supports text-to-image, image editing,
  multiple aspect ratios, and various models (Gemini, GPT, Flux). Reads API key
  from ~/.pi/agent/auth.json.
---

# Nanobana Pro — AI Image Generation

Generate images from text prompts using OpenRouter's unified API. Supports multiple image generation models through a single interface.

## Reference Files

> **Important**: Read the appropriate reference file when working on specific topics.

| Topic | File | Use When |
|-------|------|----------|
| **Prompt Patterns** | [prompt-patterns.md](references/prompt-patterns.md) | Crafting effective prompts for characters, scenes, game assets |
| **Advanced Config** | [advanced-config.md](references/advanced-config.md) | Aspect ratios, resolution, model selection, batch generation |
| **Transparency Fix** | [transparency.md](references/transparency.md) | Removing baked checker backgrounds from AI-generated images |

---

## Philosophy: Prompt-Driven Asset Pipeline

Image generation is most effective when treated as part of a creative pipeline, not a one-shot tool.

**Before generating, ask:**
- What is the **end use**? (game asset, UI element, concept art, texture)
- What **style** is needed? (photorealistic, cartoon, pixel art, whimsical 3D)
- What **dimensions/aspect ratio**? (square icon, 16:9 background, portrait character)
- Does it need to be **consistent** with existing assets? (reference previous style)

**Core principles:**
1. **Detailed prompts produce better results** — be specific about style, lighting, pose, camera angle
2. **Iterate with refinement** — generate, evaluate, adjust prompt, regenerate
3. **Pipeline thinking** — character → background → animation is a workflow, not isolated steps
4. **Save everything** — always save generated images with descriptive filenames

---

## Quick Start: Generate an Image

### API Key Setup

The OpenRouter API key is read from pi's auth file `~/.pi/agent/auth.json`:

```json
{
  "openrouter": { "type": "api_key", "key": "sk-or-v1-..." }
}
```

The `key` field supports pi's standard key resolution formats:
- **Literal value**: `"sk-or-v1-..."` — used directly
- **Shell command**: `"!security find-generic-password -ws 'openrouter'"` — executes and uses stdout
- **Env var name**: `"MY_OPENROUTER_KEY"` — reads from that environment variable

Falls back to the `OPENROUTER_API_KEY` environment variable if auth.json is not configured.

### Basic Generation (curl)

```bash
OPENROUTER_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.pi/agent/auth.json')).get('openrouter',{}).get('key',''))")

curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/gemini-3.1-flash-image-preview",
    "modalities": ["image", "text"],
    "messages": [
      {
        "role": "user",
        "content": "A whimsical 3D cartoon pirate character in a T-pose, clean white background, suitable for game asset"
      }
    ]
  }' | python3 -c "
import json, sys, base64
data = json.load(sys.stdin)
msg = data['choices'][0]['message']
images = msg.get('images', [])
for i, img in enumerate(images):
    # Remove data URL prefix if present
    b64 = img.split(',', 1)[-1] if ',' in img else img
    with open(f'generated_{i}.png', 'wb') as f:
        f.write(base64.b64decode(b64))
    print(f'Saved: generated_{i}.png')
if msg.get('content'):
    print(f'Model note: {msg[\"content\"][:200]}')
"
```

### Using the Helper Script

A convenience script is provided for common workflows:

```bash
python3 ~/.pi/agent/skills/nanobana-pro/scripts/generate-image.py \
  --prompt "A magical forest at sunset, 2.5D game background" \
  --output forest_bg.png \
  --aspect 16:9
```

---

## Available Models

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| `google/gemini-3.1-flash-image-preview` | **Default** — fast + high quality | ⚡ Fast | $ Low |
| `google/gemini-3-pro-image-preview` | Max quality, complex scenes | 🔵 Medium | $$ Medium |
| `google/gemini-2.5-flash-image` | Legacy, cheapest drafts | ⚡ Fast | $ Low |
| `openai/gpt-5-image-mini` | Good balance, text in images | 🔵 Medium | $$ Medium |
| `openai/gpt-5-image` | Best quality, photorealism | 🐢 Slow | $$$ High |

**Default recommendation**: `google/gemini-3.1-flash-image-preview` — best balance of speed and quality. Use `gemini-3-pro-image-preview` for max quality, `gpt-5-image` for photorealism.

---

## Image Configuration

### Aspect Ratios

Specify `image_config.aspect_ratio` in the request:

| Ratio | Dimensions | Use Case |
|-------|-----------|----------|
| `1:1` | 1024×1024 | Icons, avatars, textures (default) |
| `16:9` | 1344×768 | Game backgrounds, landscapes |
| `9:16` | 768×1344 | Character portraits, mobile wallpapers |
| `3:2` | 1248×832 | Scene establishing shots |
| `2:3` | 832×1248 | Character full-body |
| `4:3` | 1184×864 | UI panels, cards |
| `21:9` | 1536×672 | Ultra-wide panoramas |

### Resolution

Set `image_config.image_size` for higher resolution:

| Size | Quality | Notes |
|------|---------|-------|
| `1K` | Standard | Default, good for drafts |
| `2K` | High | Better detail, slower |
| `4K` | Maximum | Production assets, slowest |

### Example with Config

```bash
OPENROUTER_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.pi/agent/auth.json')).get('openrouter',{}).get('key',''))")

curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/gemini-3.1-flash-image-preview",
    "modalities": ["image", "text"],
    "image_config": {
      "aspect_ratio": "16:9",
      "image_size": "2K"
    },
    "messages": [
      {
        "role": "user",
        "content": "A tropical pirate cove at golden hour, 2.5D pre-rendered game background with subtle depth layers"
      }
    ]
  }'
```

---

## Getting True Transparency

> **Critical**: AI models (especially Gemini) always output RGB — never real alpha. Asking for "transparent background" produces a **baked checker pattern** that is extremely hard to remove cleanly (variable colors, different square sizes per image).

### The Right Way: White Background + Remove

**Always prompt for a solid white background**, then strip it:

```
SOLID WHITE BACKGROUND (#FFFFFF). Do NOT use a checkerboard or gradient background.
```

Then remove the white:

```bash
# Single image
python3 ~/.pi/agent/skills/nanobana-pro/scripts/remove-bg.py sprite.png

# Batch — all PNGs in a directory
python3 ~/.pi/agent/skills/nanobana-pro/scripts/remove-bg.py --dir ./generated/

# Non-white background (e.g. black)
python3 ~/.pi/agent/skills/nanobana-pro/scripts/remove-bg.py --color 0,0,0 sprite.png

# Preview mode (save as *_transparent.png, don't overwrite)
python3 ~/.pi/agent/skills/nanobana-pro/scripts/remove-bg.py --preview sprite.png
```

**Requires**: `pip install Pillow numpy scipy`

### Why Not "Transparent Background"?

| Prompt | What You Get | Removal Difficulty |
|--------|-------------|-------------------|
| "transparent background" | Baked checker pattern (variable gray tones) | 🔴 Hard — checker colors vary per image, dark subjects blend with dark checkers |
| "white background" | Solid #FFFFFF | 🟢 Easy — single known color, trivial flood-fill |

### How `remove-bg.py` Works

1. Find all near-white pixels (within tolerance of `#FFFFFF`)
2. Label connected components (scipy ndimage, 8-connected)
3. **Only remove components touching the image border** — preserves white inside the character (eyes, teeth, highlights)
4. Smooth alpha edges with Gaussian blur for clean anti-aliasing

### The Old Way (Checker Removal)

The `remove-checker-bg.py` script is still available for images already generated with checker backgrounds, but **prefer regenerating with white backgrounds** when possible — it's faster and more reliable.

For full details, see [transparency.md](references/transparency.md).

---

## Common Workflows

### 1. Game Character Creation

Generate a character in T-pose for image-to-3D conversion:

```
Prompt: "A whimsical cartoonish pirate character in a T-pose, arms straight out
to the sides, facing forward. Clean white background. Colorful, stylized 3D look
with exaggerated proportions. Suitable for a mobile game. Full body visible."
```

Aspect: `2:3` (portrait, full body)

### 2. Game Background / Level Art

Generate pre-rendered 2.5D backgrounds:

```
Prompt: "A tavern interior scene in whimsical cartoon 3D style, warm lighting,
wooden beams, barrels stacked along walls, a long bar counter in the middle ground.
Depth layers suitable for parallax scrolling. 2.5D game background. No characters."
```

Aspect: `16:9` (landscape)

### 3. UI Assets and Icons

```
Prompt: "A treasure chest icon, gold coins overflowing, cartoon game style,
clean edges, suitable for UI button. Solid white background."
```

Aspect: `1:1` (square)

### 4. Texture Generation

```
Prompt: "Seamless tileable wooden plank texture, old weathered pirate ship deck,
top-down view, uniform lighting, suitable for game texture atlas"
```

Aspect: `1:1`

### 5. Image Editing / Refinement

For models that support image input (Gemini, GPT), include a reference image:

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": { "url": "data:image/png;base64,..." }
        },
        {
          "type": "text",
          "text": "Given this 3D pirate character, create a background scene in the same art style for a 2.5D game. 16:9 ratio."
        }
      ]
    }
  ]
}
```

---

## Response Handling

### Response Format

Images may be returned as strings or dict objects depending on the model:

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Here is your generated image...",
      "images": [
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,iVBOR..."}, "index": 0}
      ]
    }
  }]
}
```

Some models return plain strings: `"images": ["data:image/png;base64,iVBOR..."]`

### Saving Images (Python)

Handle both string and dict formats:

```python
import json, base64

def extract_b64(img):
    """Extract base64 from string or dict image entry"""
    if isinstance(img, str):
        return img.split(',', 1)[-1] if ',' in img else img
    elif isinstance(img, dict):
        url = img.get('image_url', {}).get('url', '') or img.get('url', '')
        return url.split(',', 1)[-1] if ',' in url else url
    return ''

def save_images(response_data, prefix="image"):
    msg = response_data['choices'][0]['message']
    images = msg.get('images', [])
    saved = []
    for i, img in enumerate(images):
        b64 = extract_b64(img)
        if not b64:
            continue
        filename = f'{prefix}_{i}.png'
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(b64))
        saved.append(filename)
    return saved
```

### Saving Images (Node.js)

```javascript
const fs = require('fs');

function extractB64(img) {
    if (typeof img === 'string') {
        return img.includes(',') ? img.split(',')[1] : img;
    }
    if (typeof img === 'object') {
        const url = img?.image_url?.url || img?.url || '';
        return url.includes(',') ? url.split(',')[1] : url;
    }
    return '';
}

function saveImages(responseData, prefix = 'image') {
    const msg = responseData.choices[0].message;
    const images = msg.images || [];
    return images.map((img, i) => {
        const b64 = extractB64(img);
        if (!b64) return null;
        const filename = `${prefix}_${i}.png`;
        fs.writeFileSync(filename, Buffer.from(b64, 'base64'));
        return filename;
    }).filter(Boolean);
}
```

---

## Prompt Engineering Tips

### Be Specific
❌ `"a pirate"` → generic, unpredictable
✓ `"A whimsical cartoon 3D pirate with a red bandana, peg leg, oversized boots, holding a treasure map. Bright colors, stylized proportions, clean white background"`

### Specify Technical Requirements
- **For 3D conversion**: "T-pose, clean background, front view"
- **For game backgrounds**: "2.5D, parallax-ready depth layers, no characters"
- **For textures**: "seamless tileable, top-down, uniform lighting"
- **For UI**: "clean edges, suitable for game UI, icon style"

### Style Consistency
When generating multiple assets for the same project, repeat key style terms:
- `"whimsical cartoon 3D style"` — use consistently across all prompts
- `"matching the visual style of [previous description]"`
- `"same art direction as a [genre] mobile game"`

### Negative Guidance
Some models respond to "avoid" instructions:
- `"No text overlays, no watermarks"`
- `"Avoid photorealistic style, keep cartoon/stylized"`
- `"No characters in the background scene"`

---

## Anti-Patterns

❌ **Prompting "transparent background"** — produces baked checker patterns with variable colors that are extremely hard to remove cleanly
Better: Prompt for `"SOLID WHITE BACKGROUND (#FFFFFF)"` then run `remove-bg.py`

❌ **Vague prompts** — "make a cool picture" produces unpredictable results
Better: Be specific about subject, style, lighting, composition, and use case

❌ **Ignoring aspect ratio** — generating 1:1 for a 16:9 background
Better: Always specify the correct aspect ratio for the intended use

❌ **Not saving intermediate results** — you can't go back to a good generation
Better: Save every useful generation with descriptive filenames

❌ **One-shot generation** — expecting perfection on the first try
Better: Iterate: generate → evaluate → refine prompt → regenerate

❌ **Hardcoding API keys** — security risk
Better: Read from `~/.pi/agent/auth.json` (pi's standard auth file)

❌ **Using expensive models for drafts** — wastes money
Better: Draft with `gemini-3.1-flash-image-preview`, final with `gpt-5-image`

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Bad API key | Check `~/.pi/agent/auth.json` has valid `openrouter` key |
| 402 Payment Required | Insufficient credits | Add credits at openrouter.ai |
| 429 Rate Limited | Too many requests | Wait and retry with backoff |
| No `images` in response | Wrong model or missing `modalities` | Ensure model supports image output AND `modalities` is set |
| Empty images array | Model declined generation | Refine prompt, avoid policy violations |

---

## Remember

**Image generation is a creative tool, not a slot machine.**

Effective generation:
- Starts with clear intent (what, why, where it's used)
- Uses detailed, specific prompts
- Specifies technical requirements (aspect ratio, resolution, style)
- Iterates toward the desired result
- Saves everything worth keeping

**Default model**: `google/gemini-3.1-flash-image-preview` — fast + high quality, best default for most tasks.
**Production model**: `openai/gpt-5-image` — highest quality, use for final assets.

For detailed prompt patterns, see [prompt-patterns.md](references/prompt-patterns.md).
For advanced configuration, see [advanced-config.md](references/advanced-config.md).
