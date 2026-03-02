#!/usr/bin/env python3
import os, sys, json
import urllib.request

# ── CONFIGURATION ────────────────────────────────────────────────

CIVITAI_API_KEY = "38681c453aa0a1cdf22e4526c2d9d337"
MODEL_ID        = "1874153"
VERSION_ID      = "2121297"

# ── FIND THE LORA FOLDER ─────────────────────────────────────────

POSSIBLE_PATHS = [
    "/workspace/runpod-slim/ComfyUI/models/loras",
    "/workspace/ComfyUI/models/loras",
    "/workspace/stable-diffusion-webui/models/Lora",
    "/comfy/ComfyUI/models/loras",
]

def find_lora_folder():
    for path in POSSIBLE_PATHS:
        if os.path.isdir(path):
            return path
    import subprocess
    result = subprocess.run(["find", "/", "-name", "loras", "-type", "d"],
                            capture_output=True, text=True)
    matches = [m for m in result.stdout.strip().split("\n") if m]
    return matches[0] if matches else None

lora_folder = find_lora_folder()
if not lora_folder:
    print("ERROR: Can't find LoRA folder.")
    sys.exit(1)

print(f"LoRA folder: {lora_folder}\n")

# ── STEP 1: FETCH FILE INFO FROM CIVITAI API ─────────────────────
# Ask CivitAI what files are available for this version
# This tells us the real filename before we download

print(f"Fetching file info for version {VERSION_ID}...")

api_url = f"https://civitai.com/api/v1/model-versions/{VERSION_ID}"
req = urllib.request.Request(api_url, headers={
    "User-Agent": "Mozilla/5.0",
    "Authorization": f"Bearer {CIVITAI_API_KEY}"
})

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())  # Parse the JSON response from CivitAI
except Exception as e:
    print(f"ERROR fetching file info: {e}")
    sys.exit(1)

# Print all files available for this version so we can see what's in it
print(f"\nFiles available in this version:")
for i, f in enumerate(data["files"]):
    print(f"  [{i+1}] {f['name']} ({f['sizeKB'] / 1024:.1f} MB) — type: {f.get('type', 'unknown')}")

# ── STEP 2: DOWNLOAD EACH FILE ───────────────────────────────────
# Some versions have multiple files — this downloads all of them

print()
for file in data["files"]:
    filename  = file["name"]                              # The real filename from CivitAI
    save_path = os.path.join(lora_folder, filename)       # Full path to save it

    if os.path.exists(save_path):
        print(f"Already exists, skipping: {filename}")
        continue

    # Build the download URL using the version ID
    # Using the download endpoint which handles the actual file delivery
    download_url = f"https://civitai.com/api/download/models/{VERSION_ID}?token={CIVITAI_API_KEY}"

    print(f"Downloading: {filename}")
    print(f"  From: {download_url}")

    try:
        # User-Agent header required — CivitAI blocks Python requests without it
        req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            with open(save_path, "wb") as f:
                f.write(response.read())  # Write the downloaded bytes to disk

        size_mb = os.path.getsize(save_path) / (1024 * 1024)  # Convert bytes to MB
        print(f"  Done! {size_mb:.1f} MB saved to: {save_path}\n")

    except Exception as e:
        print(f"  FAILED: {e}\n")

print("All done! Restart ComfyUI to see your new LoRAs.")
