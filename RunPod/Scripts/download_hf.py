import os
import sys
import re
from huggingface_hub import hf_hub_download

def download_from_hf(url, custom_dir=None):
    # Regex to extract repo_id and filename from HF URL
    # Supports: https://huggingface.co/repo_owner/repo_name/blob/main/path/to/file.safetensors
    pattern = r"huggingface\.co/([^/]+/[^/]+)/(?:blob|resolve)/([^/]+)/(.+)"
    match = re.search(pattern, url)
    
    if not match:
        print("❌ Invalid Hugging Face URL. Make sure it's a direct link to a file.")
        return

    repo_id = match.group(1)
    revision = match.group(2)
    filename = match.group(3)
    
    # Auto-detect folder based on file extension if no custom_dir provided
    if not custom_dir:
        if "vae" in filename.lower() or "vae" in repo_id.lower():
            target_subfolder = "models/vae"
        elif any(ext in filename for ext in ["clip", "t5"]):
            target_subfolder = "models/clip"
        elif "controlnet" in filename.lower():
            target_subfolder = "models/controlnet"
        elif "lora" in filename.lower():
            target_subfolder = "models/loras"
        else:
            target_subfolder = "models/checkpoints"
        
        # Use ComfyUI base path if it exists
        base_path = "/workspace/ComfyUI" if os.path.exists("/workspace/ComfyUI") else "."
        custom_dir = os.path.join(base_path, target_subfolder)

    print(f"🚀 Downloading: {filename}")
    print(f"📦 From Repo: {repo_id}")
    print(f"📂 Saving to: {custom_dir}")

    try:
        hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            revision=revision,
            local_dir=custom_dir,
            local_dir_use_symlinks=False
        )
        print("✅ Download Complete!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_hf.py <HF_URL> [optional_target_directory]")
    else:
        download_url = sys.argv[1]
        target = sys.argv[2] if len(sys.argv) > 2 else None
        download_from_hf(download_url, target)