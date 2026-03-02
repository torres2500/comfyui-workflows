#!/usr/bin/env python3
import os, sys, subprocess, time

# ── ADD ALL YOUR LORAS HERE ──────────────────────────────────────
# Each {} block = one LoRA. Copy/paste a block to add more.

LORAS = [

    # From CivitAI — with version ID
    {
        "source":     "civitai",
        "filename":   "DR34ML4Y_I2V_14B_HIGH.safetensors",
        "model_id":   "1811313",
        "version_id": "2553151",
        "api_key":    "38681c453aa0a1cdf22e4526c2d9d337",
    },

    # From CivitAI — with version ID
    {
        "source":     "civitai",
        "filename":   "DR34ML4Y_I2V_14B_LOW.safetensors",
        "model_id":   "1811313",
        "version_id": "2553271",
        "api_key":    "38681c453aa0a1cdf22e4526c2d9d337",
    },
    
    {
        "source":     "civitai",
        "filename":   "wan22-ultimatedeepthroat-i2v-102epoc-high-k3nk.safetensors",
        "model_id":   "1874811",       # Ultimate DeepThroat I2V Wan2.2 Video LoRa - K3NK
        "version_id": "2325788",     # High noise - v1.1
        "api_key":    "38681c453aa0a1cdf22e4526c2d9d337",
    },
    {
        "source":     "civitai",
        "filename":   "wan22-ultimatedeepthroat-I2V-101epoc-low-k3nk.safetensors",
        "model_id":   "1874811",       # Ultimate DeepThroat I2V Wan2.2 Video LoRa - K3NK
        "version_id": "2191446",     # Low Noise - v1.1
        "api_key":    "38681c453aa0a1cdf22e4526c2d9d337",
    },
   
    # ── Ultimate DeepThroat I2V Wan2.2 Video LoRa - K3NK (model ID: 1874811) ──
    {
        "source":     "civitai",
        "filename":   "wan22-ultimatedeepthroat-i2v-102epoc-high-k3nk.safetensors",
        "model_id":   "1874811",       # Ultimate DeepThroat I2V Wan2.2 Video LoRa - K3NK
        "version_id": "2325788",     # High noise - v1.1
        "api_key":    "38681c453aa0a1cdf22e4526c2d9d337",
    },
    {
        "source":     "civitai",
        "filename":   "wan22-ultimatedeepthroat-I2V-101epoc-low-k3nk.safetensors",
        "model_id":   "1874811",       # Ultimate DeepThroat I2V Wan2.2 Video LoRa - K3NK
        "version_id": "2191446",     # Low Noise - v1.1
        "api_key":    "38681c453aa0a1cdf22e4526c2d9d337",
    },
    # ── WAN DR34MJOB - Double/Single/Handy Blowjob (model ID: 1395313) ──
    {
        "source":     "civitai",
        "filename":   "DR34MJOB_I2V_14b_LowNoise.safetensors",
        "model_id":   "1395313",       # WAN DR34MJOB - Double/Single/Handy Blowjob
        "version_id": "2235288",     # v1.0_I2V_14B_LOW
        "api_key":    "38681c453aa0a1cdf22e4526c2d9d337",
    },
    {
        "source":     "civitai",
        "filename":   "DR34MJOB_I2V_14b_HighNoise.safetensors",
        "model_id":   "1395313",       # WAN DR34MJOB - Double/Single/Handy Blowjob
        "version_id": "2235299",     # v1.0_I2V_14B_HIGH
        "api_key":    "38681c453aa0a1cdf22e4526c2d9d337",
    },



]

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
    print("Searching filesystem for loras folder...")
    result = subprocess.run(["find", "/", "-name", "loras", "-type", "d"],
                            capture_output=True, text=True)
    matches = [m for m in result.stdout.strip().split("\n") if m]
    return matches[0] if matches else None

lora_folder = find_lora_folder()
if not lora_folder:
    print("ERROR: Can't find LoRA folder.")
    sys.exit(1)

print(f"LoRA folder: {lora_folder}\n")

# ── DOWNLOAD FUNCTIONS ───────────────────────────────────────────

def download_civitai(lora, save_path):
    import urllib.request

    if lora.get("version_id"):
        id_to_use = lora["version_id"]
        print(f"  Downloading from CivitAI (model {lora['model_id']}, version {lora['version_id']})...")
    else:
        id_to_use = lora["model_id"]
        print(f"  Downloading from CivitAI (model {lora['model_id']}, latest version)...")

    url = f"https://civitai.com/api/download/models/{id_to_use}?token={lora['api_key']}"

    # Add a User-Agent header — CivitAI blocks Python's default requests without it
    # curl works fine because it sends headers automatically, urllib doesn't by default
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        with open(save_path, "wb") as f:
            f.write(response.read())  # Write the downloaded bytes directly to the file

def download_huggingface(lora, save_path):
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "huggingface_hub", "-q"], check=True)
        from huggingface_hub import hf_hub_download
    print(f"  Downloading from HuggingFace...")
    hf_hub_download(repo_id=lora["repo"], filename=lora["file"], local_dir=lora_folder)

def download_direct(lora, save_path):
    import urllib.request
    print(f"  Downloading from URL...")
    urllib.request.urlretrieve(lora["url"], save_path)

# ── LOOP THROUGH ALL LORAS ───────────────────────────────────────

results = {"success": [], "failed": []}

for i, lora in enumerate(LORAS):
    print(f"[{i+1}/{len(LORAS)}] {lora['filename']}")
    save_path = os.path.join(lora_folder, lora["filename"])

    if os.path.exists(save_path):
        print("  Already exists, skipping.")
        results["success"].append(lora["filename"] + " (skipped)")
        continue

    try:
        if   lora["source"] == "civitai":      download_civitai(lora, save_path)
        elif lora["source"] == "huggingface":  download_huggingface(lora, save_path)
        elif lora["source"] == "direct":       download_direct(lora, save_path)
        else: raise ValueError(f"Unknown source '{lora['source']}'")

        size_mb = os.path.getsize(save_path) / (1024 * 1024)
        print(f"  Done! {size_mb:.1f} MB")
        results["success"].append(lora["filename"])

    except Exception as e:
        print(f"  FAILED: {e}")
        results["failed"].append(lora["filename"])

    if i < len(LORAS) - 1:
        time.sleep(1)

# ── SUMMARY ─────────────────────────────────────────────────────

print("\n" + "="*40 + "\nSUMMARY\n" + "="*40)
for name in results["success"]: print(f"  + {name}")
for name in results["failed"]:  print(f"  x {name}")
if not results["failed"]: print("\nAll done! Restart ComfyUI to see your new LoRAs.")
