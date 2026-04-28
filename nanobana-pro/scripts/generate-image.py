#!/usr/bin/env python3
"""
Nanobana Pro — AI Image Generation via OpenRouter

Usage:
  python3 generate-image.py --prompt "A pirate ship at sunset" --output ship.png
  python3 generate-image.py --prompt "Game background" --aspect 16:9 --model google/gemini-3.1-flash-image-preview
  python3 generate-image.py --prompt "Edit this" --input reference.png --output edited.png

Auth:
  Reads OpenRouter API key from (in order):
  1. ~/.pi/agent/auth.json  {"openrouter": {"type": "api_key", "key": "sk-or-v1-..."}}
  2. OPENROUTER_API_KEY environment variable
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error


def get_api_key():
    """Read OpenRouter API key from pi auth.json or environment.

    Resolution order:
    1. ~/.pi/agent/auth.json -> openrouter -> key
       - Supports literal key, env var name, or "!command" shell execution
    2. OPENROUTER_API_KEY environment variable
    """
    # 1. Try ~/.pi/agent/auth.json
    auth_path = os.path.expanduser("~/.pi/agent/auth.json")
    if os.path.exists(auth_path):
        try:
            with open(auth_path) as f:
                auth = json.load(f)
            openrouter = auth.get("openrouter", {})
            key = openrouter.get("key", "")
            if key:
                # Handle pi key resolution formats
                if key.startswith("!"):
                    # Shell command: execute and use stdout
                    result = subprocess.run(
                        key[1:], shell=True, capture_output=True, text=True
                    )
                    resolved = result.stdout.strip()
                    if resolved:
                        return resolved
                elif not key.startswith("sk-") and os.environ.get(key):
                    # Env var name reference
                    return os.environ[key]
                else:
                    # Literal key value
                    return key
        except (json.JSONDecodeError, KeyError):
            pass

    # 2. Try environment variable
    env_key = os.environ.get("OPENROUTER_API_KEY", "")
    if env_key:
        return env_key

    print(
        "Error: OpenRouter API key not found.\n"
        "Set it in ~/.pi/agent/auth.json:\n"
        '  {"openrouter": {"type": "api_key", "key": "sk-or-v1-..."}}\n'
        "Or set OPENROUTER_API_KEY environment variable.",
        file=sys.stderr,
    )
    sys.exit(1)


def encode_image(path):
    """Encode an image file as base64 data URL"""
    ext = os.path.splitext(path)[1].lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(ext, "image/png")

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def generate_image(
    prompt,
    model="google/gemini-3.1-flash-image-preview",
    aspect_ratio=None,
    image_size=None,
    input_image=None,
):
    """Call OpenRouter API to generate an image"""
    api_key = get_api_key()

    # Build messages
    if input_image:
        content = [
            {"type": "image_url", "image_url": {"url": encode_image(input_image)}},
            {"type": "text", "text": prompt},
        ]
    else:
        content = prompt

    # Build request body
    body = {
        "model": model,
        "modalities": ["image", "text"],
        "messages": [{"role": "user", "content": content}],
    }

    # Add image config if specified
    image_config = {}
    if aspect_ratio:
        image_config["aspect_ratio"] = aspect_ratio
    if image_size:
        image_config["image_size"] = image_size
    if image_config:
        body["image_config"] = image_config

    # Make request
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "nanobana-pro",
            "X-Title": "Nanobana Pro",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)


def extract_b64(img):
    """Extract base64 data from an image entry (string or dict)"""
    if isinstance(img, str):
        # Direct base64 string or data URL
        return img.split(",", 1)[-1] if "," in img else img
    elif isinstance(img, dict):
        # Dict format: {"type": "image_url", "image_url": {"url": "data:..."}}
        url = img.get("image_url", {}).get("url", "") or img.get("url", "")
        if url:
            return url.split(",", 1)[-1] if "," in url else url
        # Try base64 field directly
        return img.get("base64", img.get("data", ""))
    return ""


def save_images(response_data, output_prefix):
    """Extract and save images from API response"""
    msg = response_data.get("choices", [{}])[0].get("message", {})
    images = msg.get("images", [])
    content = msg.get("content", "")

    if not images:
        print("Warning: No images in response", file=sys.stderr)
        if content:
            print(f"Model response: {content[:500]}", file=sys.stderr)
        return []

    saved = []
    for i, img in enumerate(images):
        b64 = extract_b64(img)
        if not b64:
            print(f"Warning: Could not extract image data from entry {i}", file=sys.stderr)
            continue

        if i == 0 and output_prefix.endswith((".png", ".jpg", ".jpeg", ".webp")):
            filename = output_prefix
        else:
            base, ext = os.path.splitext(output_prefix)
            if not ext:
                ext = ".png"
            filename = f"{base}_{i}{ext}" if i > 0 else f"{base}{ext}"

        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        with open(filename, "wb") as f:
            f.write(base64.b64decode(b64))
        saved.append(filename)
        print(f"Saved: {filename}")

    if content:
        print(f"Model note: {content[:300]}")

    return saved


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using AI via OpenRouter"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Image generation prompt")
    parser.add_argument(
        "--output", "-o", default="generated.png", help="Output filename (default: generated.png)"
    )
    parser.add_argument(
        "--model",
        "-m",
        default="google/gemini-3.1-flash-image-preview",
        help="Model to use (default: google/gemini-3.1-flash-image-preview)",
    )
    parser.add_argument(
        "--aspect",
        "-a",
        choices=[
            "1:1", "2:3", "3:2", "3:4", "4:3",
            "4:5", "5:4", "9:16", "16:9", "21:9",
        ],
        help="Aspect ratio",
    )
    parser.add_argument(
        "--size",
        "-s",
        choices=["1K", "2K", "4K"],
        help="Image resolution (1K, 2K, 4K)",
    )
    parser.add_argument(
        "--input",
        "-i",
        help="Input image for image-to-image editing",
    )

    args = parser.parse_args()

    print(f"Model: {args.model}")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    if args.aspect:
        print(f"Aspect: {args.aspect}")
    if args.size:
        print(f"Size: {args.size}")
    if args.input:
        print(f"Input: {args.input}")
    print("Generating...")

    response = generate_image(
        prompt=args.prompt,
        model=args.model,
        aspect_ratio=args.aspect,
        image_size=args.size,
        input_image=args.input,
    )

    saved = save_images(response, args.output)

    if not saved:
        print("Error: No images were generated", file=sys.stderr)
        sys.exit(1)

    print(f"\nDone! Generated {len(saved)} image(s)")


if __name__ == "__main__":
    main()
