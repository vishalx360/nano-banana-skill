# Advanced Usage

## Prompt Engineering Patterns

### Icons

For best results with icon generation:
- Specify the style: flat design, 3D, skeuomorphic, outlined, glyph
- Mention corner style: rounded corners, sharp corners, circle
- Define background: solid color, gradient, transparent
- Include size context: "app icon", "favicon", "toolbar icon"

Example prompts:
- `"Flat design app icon for a music player, rounded corners, purple gradient background, white play button symbol"`
- `"Outlined monochrome icon of a shopping cart, thin lines, no background, 64x64 style"`

### Seamless Patterns

For tileable patterns:
- Always include "seamless" and "tileable" in the prompt
- Specify density: sparse, medium, dense, packed
- Mention intended use: fabric, wallpaper, web background
- Define color palette explicitly

Example prompts:
- `"Seamless tileable floral pattern, vintage botanical style, muted earth tones, medium density, suitable for wallpaper"`
- `"Geometric seamless pattern, art deco style, gold on dark navy, high density"`

### Story Sequences

For maintaining visual consistency across frames:
- Always reference the previous frame using `--reference`
- Include "Scene N of M" in each prompt
- Repeat key visual descriptors (art style, character descriptions) in every prompt
- Use the same `--size` across all frames

### Diagrams

For technical diagrams:
- Specify the diagram type: flowchart, architecture, sequence, ER, mind map
- Mention layout: left-to-right, top-to-bottom, radial
- Request labels and annotations explicitly
- Use "clean lines" and "professional" for cleaner output

Example prompts:
- `"Flowchart diagram: User Login flow. Steps: Enter credentials, Validate, 2FA check, Success/Failure. Clean lines, labeled boxes, top-to-bottom layout"`
- `"System architecture diagram: React frontend, Node.js API, PostgreSQL database, Redis cache. Show connections with labeled arrows"`

## API Key Configuration

The script checks these environment variables in order:

1. `NANOBANANA_GEMINI_API_KEY` - Skill-specific key (highest priority)
2. `NANOBANANA_GOOGLE_API_KEY` - Skill-specific alternate
3. `GEMINI_API_KEY` - Standard Gemini key
4. `GOOGLE_API_KEY` - General Google AI key

To persist across sessions, add to your shell profile:

```bash
# ~/.bashrc, ~/.zshrc, or equivalent
export GEMINI_API_KEY="your-api-key-here"
```

Get a free key at: https://aistudio.google.com/apikey

## Model Comparison

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `gemini-2.5-flash-image` | Fast | Good | Quick iterations, drafts, icons |
| `gemini-3-pro-image-preview` | Slower | Highest | Final outputs, detailed scenes, photo editing |

Set via environment variable:
```bash
export NANOBANANA_MODEL="gemini-3-pro-image-preview"
```

## Troubleshooting

### Quota Exceeded (429)

The free tier has per-minute and per-day limits. Solutions:
- Wait 60 seconds and retry
- Use a smaller `--size` (1K is fastest)
- Upgrade to a paid API plan for higher limits

### Safety Filter Triggered

Gemini may refuse prompts it considers unsafe. Solutions:
- Rephrase the prompt to be more specific and neutral
- Avoid ambiguous descriptions that could be misinterpreted
- Focus on artistic and descriptive language

### No Image in Response

Sometimes the model returns text instead of an image. Solutions:
- Make the prompt more visually descriptive
- Start prompts with "Generate an image of..." or "Create a photo of..."
- Try a different model (`gemini-3-pro-image-preview` is more reliable for complex prompts)

### Slow Generation

Image generation times vary by size:
- 1K: ~5-15 seconds
- 2K: ~10-25 seconds
- 4K: ~15-45 seconds

Use `--size 1K` for faster iteration during prompt refinement, then switch to higher resolution for final output.

### Virtual Environment Issues

If the script fails to find Python packages:

```bash
cd <skill-dir>/scripts
rm -rf venv
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```
