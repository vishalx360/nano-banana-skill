#!/usr/bin/env bash
set -e

# Resolve the directory where this script lives (works from any cwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Setting up Nano Banana Skill..."
echo "Script directory: $SCRIPT_DIR"

# Check for Python 3
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 not found. Install Python 3.8+ first." >&2
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Found Python $PY_VERSION"

# Create venv if it doesn't exist
VENV_DIR="$SCRIPT_DIR/venv"
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
else
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created."
fi

# Install dependencies
echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"
echo "Dependencies installed."

# Check for API key
KEY_FOUND=false
for VAR in NANOBANANA_GEMINI_API_KEY NANOBANANA_GOOGLE_API_KEY GEMINI_API_KEY GOOGLE_API_KEY; do
    if [ -n "${!VAR}" ]; then
        echo "API key found: $VAR"
        KEY_FOUND=true
        break
    fi
done

if [ "$KEY_FOUND" = false ]; then
    echo ""
    echo "No API key detected. Set one before using the skill:"
    echo "  export GEMINI_API_KEY=\"your-api-key\""
    echo "  Get a free key at: https://aistudio.google.com/apikey"
fi

echo ""
echo "Setup complete! Ready to generate images."
