#!/usr/bin/env python3
import os, sys, json
import urllib.request

# ── CONFIGURATION ────────────────────────────────────────────────

GITHUB_USER  = "torres2500"
GITHUB_REPO  = "comfyui-workflows"
GITHUB_PATH  = "RunPod/Scripts"  # The subfolder path inside the repo

# Where to save the scripts on RunPod
SAVE_FOLDER  = "/workspace/runpod-slim"

# ── FETCH FILE LIST FROM GITHUB ──────────────────────────────────

def get_github_files(path):
    """Ask the GitHub API for a list of all files at the given repo path."""
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{path}"
    req = urllib.request.Request(api_url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/vnd.github.v3+json"
    })
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

# ── DOWNLOAD A SINGLE FILE ───────────────────────────────────────

def download_file(download_url, save_path):
    """Download a file from GitHub and save it to disk."""
    req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        with open(save_path, "wb") as f:
            f.write(response.read())

# ── MAIN ─────────────────────────────────────────────────────────

print(f"Fetching scripts from github.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_PATH}...\n")

try:
    files = get_github_files(GITHUB_PATH)
except Exception as e:
    print(f"ERROR: Could not reach GitHub — {e}")
    sys.exit(1)

# Filter to only .py files
py_files = [f for f in files if f["name"].endswith(".py")]

if not py_files:
    print("No .py script files found in the repo folder.")
    sys.exit(0)

print(f"Found {len(py_files)} script(s):\n")

results = {"success": [], "skipped": [], "failed": []}

for file in py_files:
    filename  = file["name"]                            # e.g. "lora_getter.py"
    save_path = os.path.join(SAVE_FOLDER, filename)     # Full path to save it
    raw_url   = file["download_url"]                    # Direct download link from GitHub

    print(f"  {filename}")

    if os.path.exists(save_path):
        existing_size = os.path.getsize(save_path)  # Size of file we already have
        github_size   = file["size"]                # Size reported by GitHub

        if existing_size == github_size:
            print(f"    No changes, skipping.")
            results["skipped"].append(filename)
            continue

        print(f"    File changed, updating...")
    else:
        print(f"    New file, downloading...")

    try:
        download_file(raw_url, save_path)
        print(f"    Done!")
        results["success"].append(filename)
    except Exception as e:
        print(f"    FAILED: {e}")
        results["failed"].append(filename)

# ── SUMMARY ─────────────────────────────────────────────────────

print("\n" + "="*45 + "\nSUMMARY\n" + "="*45)
print(f"  Downloaded / updated : {len(results['success'])}")
print(f"  Already up to date   : {len(results['skipped'])}")
print(f"  Failed               : {len(results['failed'])}")

if results["failed"]:
    print("\nFailed files:")
    for name in results["failed"]: print(f"  x {name}")

if results["success"]:
    print("\nUpdated files:")
    for name in results["success"]: print(f"  + {name}")

print(f"\nScripts saved to: {SAVE_FOLDER}")
print("Run any script with: python3 /workspace/runpod-slim/<script_name>.py")
