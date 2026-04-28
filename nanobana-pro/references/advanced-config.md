# Advanced Configuration

Detailed API options, model selection, batch workflows, and integration patterns.

---

## Model Selection Guide

### When to Use Each Model

| Model | Strengths | Weaknesses | Best For |
|-------|-----------|------------|----------|
| `google/gemini-3.1-flash-image-preview` | **Default** — fast + high quality | New, preview | Most tasks, game assets, icons |
| `google/gemini-3-pro-image-preview` | Max quality, good instruction following | Slower, more expensive | Final character art, detailed scenes |
| `google/gemini-2.5-flash-image` | Legacy, cheapest | Less detailed | Bulk drafts, iteration |
| `openai/gpt-5-image-mini` | Good text rendering, balanced | Medium speed | UI mockups, assets with text |
| `openai/gpt-5-image` | Highest quality, best photorealism | Slowest, most expensive | Hero images, marketing assets |

### Model Capabilities

```bash
# List all image-capable models from OpenRouter
OPENROUTER_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.pi/agent/auth.json')).get('openrouter',{}).get('key',''))")
curl -s https://openrouter.ai/api/v1/models | python3 -c "
import json, sys
data = json.load(sys.stdin)
for m in data.get('data', []):
    out = m.get('architecture', {}).get('output_modalities', [])
    if 'image' in out:
        inp = m.get('architecture', {}).get('input_modalities', [])
        print(f'{m[\"id\"]:55s} | in: {\",\".join(inp)} | out: {\",\".join(out)}')
"
```

---

## Full Request Schema

### Text-to-Image

```json
{
  "model": "google/gemini-3.1-flash-image-preview",
  "modalities": ["image", "text"],
  "image_config": {
    "aspect_ratio": "16:9",
    "image_size": "2K"
  },
  "messages": [
    {
      "role": "user",
      "content": "Your prompt here"
    }
  ]
}
```

### Image-to-Image (Edit/Refine)

For models that accept image input (Gemini, GPT):

```json
{
  "model": "google/gemini-3.1-flash-image-preview",
  "modalities": ["image", "text"],
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,<BASE64_DATA>"
          }
        },
        {
          "type": "text",
          "text": "Modify this image: change the sky to sunset colors and add a pirate ship in the distance"
        }
      ]
    }
  ]
}
```

### Image-Only Output (Flux/Sourceful)

Some models only output images (no text):

```json
{
  "model": "sourceful/riverflow-v2-fast",
  "modalities": ["image"],
  "messages": [
    {
      "role": "user",
      "content": "Your prompt here"
    }
  ]
}
```

---

## Aspect Ratio Reference

| Ratio | Pixels | Visual |
|-------|--------|--------|
| `1:1` | 1024×1024 | □ Square |
| `2:3` | 832×1248 | ▯ Tall portrait |
| `3:2` | 1248×832 | ▭ Wide landscape |
| `3:4` | 864×1184 | ▯ Portrait |
| `4:3` | 1184×864 | ▭ Landscape |
| `4:5` | 896×1152 | ▯ Slightly tall |
| `5:4` | 1152×896 | ▭ Slightly wide |
| `9:16` | 768×1344 | ▯ Phone portrait |
| `16:9` | 1344×768 | ▭ Widescreen |
| `21:9` | 1536×672 | ▭ Ultra-wide |

---

## Batch Generation Pattern

Generate multiple variations efficiently:

```bash
#!/bin/bash
OPENROUTER_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.pi/agent/auth.json')).get('openrouter',{}).get('key',''))")

PROMPTS=(
  "Pirate character idle pose, cartoon 3D style"
  "Pirate character running pose, cartoon 3D style"
  "Pirate character jumping pose, cartoon 3D style"
  "Pirate character attacking pose, cartoon 3D style"
)

for i in "${!PROMPTS[@]}"; do
  echo "Generating $i: ${PROMPTS[$i]}"
  curl -s https://openrouter.ai/api/v1/chat/completions \
    -H "Authorization: Bearer $OPENROUTER_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"google/gemini-3.1-flash-image-preview\",
      \"modalities\": [\"image\", \"text\"],
      \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPTS[$i]}\"}]
    }" | python3 -c "
import json, sys, base64
data = json.load(sys.stdin)
images = data.get('choices',[{}])[0].get('message',{}).get('images',[])
for j, img in enumerate(images):
    b64 = img.split(',',1)[-1] if ',' in img else img
    with open(f'batch_${i}_{j}.png', 'wb') as f:
        f.write(base64.b64decode(b64))
    print(f'Saved: batch_${i}_{j}.png')
" &
  # Small delay to avoid rate limits
  sleep 1
done
wait
echo "All done!"
```

---

## Streaming Support

For long-running generations, use streaming to get early feedback:

```bash
curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/gemini-3.1-flash-image-preview",
    "modalities": ["image", "text"],
    "stream": true,
    "messages": [{"role": "user", "content": "A sunset over a pirate harbor"}]
  }'
```

---

## Integration with Three.js Pipeline

### Character → 3D Model → Scene Workflow

1. **Generate character image** (Nanobana Pro):
   ```
   Prompt: "Whimsical 3D pirate in T-pose, white background"
   → Save as pirate_reference.png
   ```

2. **Convert to 3D model** (external tool):
   - Use Meshy, Tripo, or Rodin for image-to-3D
   - Export as GLB with skeleton/rig

3. **Generate background** (Nanobana Pro):
   ```
   Prompt: "Pirate cove background matching the character style, 2.5D, 16:9"
   → Save as background.png
   ```

4. **Generate animation video** (external tool):
   ```
   Prompt for Seedance/Kling: "[Background image] with subtle looping animation:
   water gently lapping, flags softly fluttering, clouds slowly moving"
   → Export as looping video
   ```

5. **Build Three.js scene** (use threejs-builder skill):
   - Load GLB character with animations
   - Use background as scene backdrop
   - Set up OrbitControls and animation UI

### Asset Index Generation

After generating all assets, create an `assets_index.json`:

```json
{
  "schemaVersion": 1,
  "characters": {
    "pirate": {
      "id": "pirate",
      "displayName": "Pirate",
      "skeleton": { "url": "/assets/glb/pirate/pirate_skeleton.glb" },
      "animationSource": { "url": "/assets/glb/pirate/pirate_animations.glb" },
      "referenceImage": "/assets/img/pirate_reference.png",
      "animations": [
        { "id": "idle", "displayName": "Idle", "sourceClipName": "...", "loop": "repeat" },
        { "id": "run", "displayName": "Run", "sourceClipName": "...", "loop": "repeat" }
      ],
      "defaults": { "defaultAnimationId": "idle", "crossFadeSec": 0.2 }
    }
  },
  "backgrounds": {
    "cove": { "url": "/assets/img/pirate_cove_bg.png", "animated": "/assets/video/cove_loop.mp4" }
  }
}
```

---

## Cost Management

### Estimated Costs per Image

| Model | ~Cost/Image |
|-------|-------------|
| `gemini-3.1-flash-image-preview` | ~$0.001-0.005 |
| `gemini-3-pro-image-preview` | ~$0.01-0.03 |
| `gemini-2.5-flash-image` | ~$0.001-0.003 |
| `gpt-5-image-mini` | ~$0.01-0.02 |
| `gpt-5-image` | ~$0.03-0.10 |

### Cost Optimization

1. **Draft with default model → gemini-3.1-flash-image-preview
2. **Refine prompt** based on drafts
3. **Generate final** with premium model
4. **Batch similar requests** to reduce overhead
5. **Cache results** — never regenerate what you've already saved

---

## Authentication

The skill reads the OpenRouter API key following pi's standard auth pattern:

### 1. Pi Auth File (Preferred)

Store in `~/.pi/agent/auth.json`:

```json
{
  "openrouter": { "type": "api_key", "key": "sk-or-v1-..." }
}
```

The `key` field supports pi's key resolution formats:
- **Literal**: `"sk-or-v1-..."` — used directly
- **Shell command**: `"!op read 'op://vault/openrouter/credential'"` — executes and uses stdout
- **Env var name**: `"MY_OR_KEY"` — reads from that environment variable

### 2. Environment Variable (Fallback)

```bash
export OPENROUTER_API_KEY=sk-or-v1-...
```

### Optional Overrides

Set in your project's `.env` if needed:

```bash
NANOBANA_DEFAULT_MODEL=google/gemini-3.1-flash-image-preview
NANOBANA_DEFAULT_ASPECT=1:1
NANOBANA_DEFAULT_SIZE=1K
NANOBANA_OUTPUT_DIR=./generated
```
