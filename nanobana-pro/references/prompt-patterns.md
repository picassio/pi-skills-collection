# Prompt Patterns for Image Generation

Proven prompt templates for common game development and creative workflows.

---

## 3D Character Creation (for Image-to-3D)

### T-Pose Character

```
A [adjective] [style] [character type] in a T-pose, arms straight out to the sides,
facing forward. Clean white background. [art style] with [proportion description].
Full body visible, feet to head. Suitable for [use case].
```

**Example:**
```
A whimsical cartoonish pirate in a T-pose, arms straight out to the sides,
facing forward. Clean white background. Colorful 3D rendered style with
exaggerated proportions and oversized hands. Full body visible, feet to head.
Suitable for a mobile adventure game character.
```

**Tips for image-to-3D:**
- Always specify T-pose for rigging compatibility
- "Clean white background" helps 3D conversion tools isolate the character
- Include "front view" or "3/4 view" for the angle you need
- Mention the game genre for style calibration

### Character Turnaround Sheet

```
Character turnaround reference sheet showing [character description] from
front view, 3/4 view, side view, and back view. All four views in a single
image, arranged left to right. Consistent proportions and style across all views.
Clean white background. [art style].
```

### Character Portrait (for voice/personality design)

```
Close-up portrait of [character], head and shoulders visible. [Expression description].
[Lighting description]. Suitable for a character card or dialogue portrait.
```

---

## Game Backgrounds and Level Art

### 2.5D Pre-rendered Background

```
A [location description] in [art style], designed as a 2.5D game background.
[Foreground details] in the front, [midground details] in the middle,
[background details] far away. Depth layers suitable for parallax scrolling.
[Lighting/time of day]. No characters present. 16:9 aspect ratio.
```

**Example:**
```
A tropical pirate cove at golden hour in whimsical cartoon 3D style, designed
as a 2.5D game background. Rocky outcroppings and palm trees in the foreground,
a wooden dock with moored ships in the midground, a distant mountain and sunset
sky in the background. Depth layers suitable for parallax scrolling. Warm golden
lighting with long shadows. No characters present. 16:9 aspect ratio.
```

### Animated Background (for video generation)

When generating backgrounds that will be animated (e.g., with Seedance, Kling, RunwayML):

```
[Scene description] with subtle elements that can animate in a seamless loop:
[element 1] gently [motion], [element 2] slowly [motion]. All motion should be
subtle enough to loop endlessly without visible seam. Camera is static.
```

**Example:**
```
A pirate tavern interior with subtle elements that can animate in a seamless loop:
candle flames gently flickering, dust motes slowly drifting through light beams,
a hanging lantern softly swaying. All motion should be subtle enough to loop
endlessly without visible seam. Camera is static. Warm indoor lighting.
```

### Parallax Layer Separation

For multi-layer parallax, generate layers separately:

```
Layer 1 (far background): "[Sky/distant landscape], [art style], wide view,
suitable for slow parallax scrolling. Solid white ground area."

Layer 2 (midground): "[Medium distance objects] on solid white background (#FFFFFF),
[art style], suitable for medium-speed parallax scrolling."

Layer 3 (foreground): "[Close objects] on solid white background (#FFFFFF),
[art style], suitable for fast parallax scrolling. Partial occlusion expected."
```

---

## UI Assets

### Game Icons

```
A [object] icon in [art style], clean edges, [color scheme], suitable for
a game UI button. [Size hint] icon style. No text. Centered composition.
Clean background with no distracting elements.
```

### Title Screen / Logo

```
Game title screen for "[Game Name]", [genre] game. [Visual theme description].
The title "[Game Name]" prominently displayed in [font style] lettering.
[Background description]. [Mood/atmosphere].
```

---

## Textures and Materials

### Seamless Tileable Texture

```
Seamless tileable [material] texture, [surface description], top-down view,
uniform lighting with no strong directional shadows. Suitable for game texture
atlas. The edges must tile seamlessly in all directions.
```

**Materials**: wood planks, stone bricks, grass, sand, metal plate, water surface

### Material Study

```
Close-up material study of [surface type]: [detail description]. PBR-ready
appearance with clear [roughness/metalness/normal] characteristics.
Evenly lit, suitable for texture reference.
```

---

## Concept Art and Exploration

### Environment Mood Board

```
Concept art exploration: 4 different [location type] designs in [art style],
arranged in a 2x2 grid. Each shows a different [variation dimension]:
[variation 1], [variation 2], [variation 3], [variation 4].
Quick painterly style, not fully rendered.
```

### Character Variations

```
Character design exploration: 4 variations of [character concept] arranged
in a 2x2 grid. Each variation explores different [variation dimension]:
[option 1], [option 2], [option 3], [option 4]. Same art style across all.
Clean backgrounds.
```

---

## Style Anchoring

To maintain consistency across multiple generations, build a style anchor phrase:

### Building a Style Anchor

1. Define core terms: `"whimsical cartoon 3D style"`
2. Add quality terms: `"high quality, detailed, polished"`
3. Add reference: `"similar to [well-known game/style]"`
4. Add technical: `"clean edges, vibrant colors, soft shadows"`

### Using Style Anchors

Include the same anchor in every prompt for a project:

```
[ANCHOR]: "Whimsical cartoon 3D style with vibrant colors, soft cel-shading,
exaggerated proportions, and clean edges. Similar to a modern mobile adventure game."

Prompt: "[ANCHOR]. A treasure chest overflowing with gold coins and gems,
sitting on a sandy beach. 1:1 aspect ratio."
```

---

## Voice and Personality Design

For generating character voice descriptions (useful for TTS or voice acting briefs):

```
For this [character description], describe the kind of voice they would have.
Include: pitch/register, accent, texture/quality, delivery style, emotional range,
and any distinctive vocal mannerisms. Format as a voice direction brief.
```

**Example output format:**
```
A youthful, high-energy tenor voice. Bright, optimistic tone with sprightly
bravado and a touch of endearing clumsiness. Soft, melodic West Country
(Cornish) lilt. Mostly clear with a subtle playful rasp when trying to sound
tough. Theatrical and rhythmic delivery with occasional pitch-cracks when
excited. Avoid deep, gravelly, or menacing tones.
```

---

## Prompt Modifiers Cheat Sheet

### Style Modifiers
- `"3D rendered"`, `"2D illustrated"`, `"pixel art"`, `"watercolor"`
- `"low-poly"`, `"voxel art"`, `"cel-shaded"`, `"flat design"`
- `"photorealistic"`, `"hyperrealistic"`, `"stylized"`, `"minimalist"`

### Lighting Modifiers
- `"golden hour"`, `"blue hour"`, `"noon harsh shadows"`
- `"soft ambient lighting"`, `"dramatic rim lighting"`, `"neon glow"`
- `"candlelit warm"`, `"moonlit cool"`, `"studio lighting"`

### Camera/Composition Modifiers
- `"close-up"`, `"medium shot"`, `"wide establishing shot"`
- `"top-down view"`, `"isometric view"`, `"3/4 perspective"`
- `"centered composition"`, `"rule of thirds"`, `"symmetrical"`

### Quality Modifiers
- `"highly detailed"`, `"clean edges"`, `"polished"`
- `"4K"`, `"high resolution"`, `"production quality"`
- `"game-ready"`, `"asset-quality"`, `"concept art quality"`

### Negative Modifiers
- `"no text"`, `"no watermark"`, `"no logo"`
- `"no characters"` (for backgrounds)
- `"no strong directional shadows"` (for textures)
- `"SOLID WHITE BACKGROUND (#FFFFFF)"` (best for sprites needing transparency — then run `remove-bg.py`)
