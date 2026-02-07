# Nano Banana Skill

Generate, edit, and restore images using Google Gemini -- from any AI agent.

## Install

```bash
npx skills add vishalx360/nano-banana-skill
```

Or with other skill managers:

```bash
npx add-skill vishalx360/nano-banana-skill
npx openskills add vishalx360/nano-banana-skill
```

## Prerequisites

- Python 3.8+
- [Google AI Studio API key](https://aistudio.google.com/apikey) (free)

## Setup

```bash
# Set your API key
export GEMINI_API_KEY="your-api-key"

# Install Python dependencies
cd <skill-dir>/scripts
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## What It Does

- **Generate** images from text prompts with optional style references
- **Edit** existing images using natural language instructions
- **Restore** and enhance old or damaged photos
- Supports 1K, 2K, and 4K output sizes
- Smart auto-naming with duplicate prevention
- JSON output mode for agent integration
- Cross-platform image preview

## Usage

```bash
# Generate an image
nanobanana.py --mode generate --prompt "A banana in space"

# Edit an existing image
nanobanana.py --mode edit --input photo.jpg --prompt "Make it a watercolor painting"

# Restore a photo
nanobanana.py --mode restore --input old_photo.jpg

# With options
nanobanana.py --mode generate --prompt "Sunset" --size 4K --format jpeg --preview --json
```

## Compatible Agents

Works with any agent supporting the [Agent Skills](https://github.com/anthropics/agent-skills) open standard:

- Claude Code
- Cursor
- Gemini CLI
- OpenCode
- Amp
- Goose
- Cline
- Roo Code
- and more

## Models

| Model | Set With |
|-------|----------|
| `gemini-2.5-flash-image` (default) | `NANOBANANA_MODEL=gemini-2.5-flash-image` |
| `gemini-3-pro-image-preview` | `NANOBANANA_MODEL=gemini-3-pro-image-preview` |

## License

MIT
