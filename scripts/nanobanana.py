#!/bin/sh
''''exec "$(dirname "$0")/venv/bin/python3" "$0" "$@" 2>/dev/null || exec python3 "$0" "$@" #'''

import argparse
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "gemini-2.5-flash-image"
OUTPUT_DIR = "nanobanana-output"
MAX_FILENAME_LEN = 32
SEARCH_PATHS = [
    ".",
    "./images",
    "./input",
    f"./{OUTPUT_DIR}",
    str(Path.home() / "Downloads"),
    str(Path.home() / "Desktop"),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_api_key():
    """Return API key using 4-tier fallback."""
    for var in (
        "NANOBANANA_GEMINI_API_KEY",
        "NANOBANANA_GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
    ):
        key = os.environ.get(var)
        if key:
            return key
    print(
        "Error: No API key found.\n"
        "Set one of: GEMINI_API_KEY, GOOGLE_API_KEY, "
        "NANOBANANA_GEMINI_API_KEY, or NANOBANANA_GOOGLE_API_KEY\n"
        "Get a key at: https://aistudio.google.com/apikey",
        file=sys.stderr,
    )
    sys.exit(1)


def generate_filename(prompt, ext="png"):
    """Create a filesystem-safe filename from a prompt."""
    name = prompt.lower().strip()
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", "_", name).strip("_")
    if not name:
        name = "generated_image"
    name = name[:MAX_FILENAME_LEN]

    output_dir = ensure_output_dir()
    candidate = output_dir / f"{name}.{ext}"
    counter = 1
    while candidate.exists():
        candidate = output_dir / f"{name}_{counter}.{ext}"
        counter += 1
    return candidate


def find_input_file(filename):
    """Search common locations for an input file. Return resolved Path or exit."""
    p = Path(filename)
    if p.is_absolute():
        if p.exists():
            return p
        print(f"Error: File not found: {filename}", file=sys.stderr)
        sys.exit(1)

    for base in SEARCH_PATHS:
        candidate = Path(base) / filename
        if candidate.exists():
            return candidate.resolve()

    print(
        f"Error: Could not find '{filename}' in any of:\n"
        + "\n".join(f"  {d}/" for d in SEARCH_PATHS),
        file=sys.stderr,
    )
    sys.exit(1)


def ensure_output_dir():
    """Create and return the output directory path."""
    d = Path(OUTPUT_DIR)
    d.mkdir(parents=True, exist_ok=True)
    return d


def open_preview(filepath):
    """Open file with the platform default viewer."""
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["open", str(filepath)])
        elif system == "Windows":
            os.startfile(str(filepath))
        else:
            subprocess.Popen(["xdg-open", str(filepath)])
    except Exception as e:
        print(f"Could not open preview: {e}", file=sys.stderr)


def result_json(success, files=None, message=""):
    """Return a structured JSON string."""
    return json.dumps(
        {"success": success, "files": files or [], "message": message},
        indent=2,
    )


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------


def generate_image(client, model, prompt, references, size, output, ext, preview, as_json):
    """Text-to-image generation with optional reference images."""
    contents = [prompt]

    for ref_path in references or []:
        resolved = find_input_file(ref_path)
        try:
            contents.append(Image.open(resolved))
            if not as_json:
                print(f"Using reference image: {resolved}")
        except Exception as e:
            print(f"Error loading reference image: {e}", file=sys.stderr)
            sys.exit(1)

    if output:
        out_path = Path(output)
        out_dir = out_path.parent
        if out_dir and str(out_dir) != ".":
            out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_path = generate_filename(prompt, ext)

    if not as_json:
        print(f"Generating image ({size})...")

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(image_size=size)
            ),
        )
    except Exception as e:
        if as_json:
            print(result_json(False, message=str(e)))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    saved_files = _save_response(response, out_path, preview, as_json)
    if not saved_files:
        if as_json:
            print(result_json(False, message="No image was generated in the response."))
        else:
            print("Warning: No image was generated in the response.", file=sys.stderr)
        sys.exit(1)

    if as_json:
        print(result_json(True, files=saved_files, message="Image generated successfully."))


def edit_image(client, model, prompt, input_file, size, output, ext, preview, as_json):
    """Edit an existing image using a text prompt."""
    resolved = find_input_file(input_file)
    try:
        img = Image.open(resolved)
    except Exception as e:
        print(f"Error loading input image: {e}", file=sys.stderr)
        sys.exit(1)

    contents = [prompt, img]

    if output:
        out_path = Path(output)
        out_dir = out_path.parent
        if out_dir and str(out_dir) != ".":
            out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_path = generate_filename(prompt, ext)

    if not as_json:
        print(f"Editing image ({size})...")

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(image_size=size)
            ),
        )
    except Exception as e:
        if as_json:
            print(result_json(False, message=str(e)))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    saved_files = _save_response(response, out_path, preview, as_json)
    if not saved_files:
        if as_json:
            print(result_json(False, message="No image was generated in the response."))
        else:
            print("Warning: No image was generated in the response.", file=sys.stderr)
        sys.exit(1)

    if as_json:
        print(result_json(True, files=saved_files, message="Image edited successfully."))


def restore_image(client, model, prompt, input_file, size, output, ext, preview, as_json):
    """Restore / enhance an image. Semantic alias for edit with restoration-oriented defaults."""
    if not prompt:
        prompt = "Restore and enhance this image. Fix any artifacts, improve clarity and quality."
    edit_image(client, model, prompt, input_file, size, output, ext, preview, as_json)


# ---------------------------------------------------------------------------
# Response handling
# ---------------------------------------------------------------------------


def _save_response(response, out_path, preview, as_json):
    """Extract images from API response and save. Returns list of saved file paths."""
    saved = []
    for part in response.parts:
        if part.text is not None and not as_json:
            print(f"Model: {part.text}")
        elif part.inline_data is not None:
            image = part.as_image()
            image.save(str(out_path))
            saved.append(str(out_path))
            if not as_json:
                print(f"Image saved to: {out_path}")
            if preview:
                open_preview(out_path)
    return saved


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        prog="nanobanana",
        description="Generate, edit, and restore images using Google Gemini.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  %(prog)s --mode generate --prompt "A banana in space"
  %(prog)s --mode generate --prompt "Cyberpunk city" --size 2K --preview
  %(prog)s --mode edit --input photo.jpg --prompt "Make it a watercolor painting"
  %(prog)s --mode restore --input old_photo.jpg
  %(prog)s --mode generate --prompt "Logo design" --reference style.png --json
""",
    )

    parser.add_argument(
        "--mode",
        required=True,
        choices=["generate", "edit", "restore"],
        help="Operation mode: generate (text-to-image), edit (modify existing), restore (enhance/fix)",
    )
    parser.add_argument("--prompt", help="Text prompt describing the desired image")
    parser.add_argument("--input", help="Input image path (required for edit and restore modes)")
    parser.add_argument(
        "--reference",
        action="append",
        help="Reference image(s) for style guidance (generate mode). Can be repeated.",
    )
    parser.add_argument("--output", help="Output file path. Defaults to auto-named file in nanobanana-output/")
    parser.add_argument(
        "--size",
        default="1K",
        choices=["1K", "2K", "4K"],
        help="Output image size (default: 1K)",
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        default="png",
        choices=["png", "jpeg"],
        help="Output image format (default: png)",
    )
    parser.add_argument("--preview", action="store_true", help="Open image after generation")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Output structured JSON for agent parsing")

    args = parser.parse_args()

    # Validation
    if args.mode == "generate" and not args.prompt:
        parser.error("--prompt is required for generate mode")
    if args.mode in ("edit", "restore") and not args.input:
        parser.error("--input is required for edit and restore modes")

    api_key = get_api_key()
    model = os.environ.get("NANOBANANA_MODEL", DEFAULT_MODEL)
    client = genai.Client(api_key=api_key)

    if args.mode == "generate":
        generate_image(
            client, model, args.prompt, args.reference,
            args.size, args.output, args.fmt, args.preview, args.as_json,
        )
    elif args.mode == "edit":
        edit_image(
            client, model, args.prompt or "Edit this image", args.input,
            args.size, args.output, args.fmt, args.preview, args.as_json,
        )
    elif args.mode == "restore":
        restore_image(
            client, model, args.prompt, args.input,
            args.size, args.output, args.fmt, args.preview, args.as_json,
        )


if __name__ == "__main__":
    main()
