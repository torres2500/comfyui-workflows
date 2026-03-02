#!/usr/bin/env python3
import os, sys, json
import urllib.request

# ── CONFIGURATION ────────────────────────────────────────────────

GITHUB_USER   = "torres2500"
GITHUB_REPO   = "comfyui-workflows"
GITHUB_PATH   = "RunPod/Workflows"  # The subfolder path inside the repo

# ── FIND THE WORKFLOW FOLDER ─────────────────────────────────────

POSSIBLE_PATHS = [
    "/workspace/runpod-slim/ComfyUI/user/default/workflows",
    "/workspace/ComfyUI/user/default/workflows",
    "/comfy/ComfyUI/user/default/workflows",
]

def find_workflow_folder():
    for path in POSSIBLE_PATHS:
        if os.path.isdir(path):
            return path
    import subprocess
    print("Searching for ComfyUI workflows folder...")
    result = subprocess.run(["find", "/", "-type", "d", "-name", "workflows"],
                            capture_output=True, text=True)
    matches = [m for m in result.stdout.strip().split("\n") if m and "ComfyUI" in m]
    return matches[0] if matches else None

workflow_folder = find_workflow_folder()

if not workflow_folder:
    workflow_folder = "/workspace/ComfyUI/user/default/workflows"
    print(f"Workflow folder not found — creating it at: {workflow_folder}")
    os.makedirs(workflow_folder, exist_ok=True)  # Create the folder if it doesn't exist
else:
    print(f"Workflow folder: {workflow_folder}\n")

# ── FETCH FILE LIST FROM GITHUB ──────────────────────────────────

def get_github_files(path):
    """Ask the GitHub API for a list of all files at the given repo path."""
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{path}"
    req = urllib.request.Request(api_url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/vnd.github.v3+json"  # Tell GitHub we want JSON back
    })
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

# ── DOWNLOAD A SINGLE FILE ───────────────────────────────────────

def download_file(download_url, save_path):
    """Download a file from GitHub and save it to disk."""
    req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        with open(save_path, "wb") as f:
            f.write(response.read())  # Write file contents directly to disk

# ── MAIN: FETCH AND SYNC ALL WORKFLOWS ───────────────────────────

print(f"Fetching workflows from github.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_PATH}...\n")

try:
    files = get_github_files(GITHUB_PATH)  # Fetch file list from the subfolder
except Exception as e:
    print(f"ERROR: Could not reach GitHub — {e}")
    sys.exit(1)

# Filter to only .json files — skip anything else like README.md
json_files = [f for f in files if f["name"].endswith(".json")]

if not json_files:
    print("No .json workflow files found in the repo folder.")
    sys.exit(0)

print(f"Found {len(json_files)} workflow file(s):\n")

results = {"success": [], "skipped": [], "failed": []}

for file in json_files:
    filename  = file["name"]                             # e.g. "my_workflow.json"
    save_path = os.path.join(workflow_folder, filename)  # Full path to save it
    raw_url   = file["download_url"]                     # Direct download link from GitHub API

    print(f"  {filename}")

    if os.path.exists(save_path):
        existing_size = os.path.getsize(save_path)  # Size of the file we already have
        github_size   = file["size"]                # Size reported by GitHub API

        if existing_size == github_size:
            print(f"    No changes, skipping.")
            results["skipped"].append(filename)
            continue  # Nothing to update, move on

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

print(f"\nWorkflows saved to: {workflow_folder}")
print("Refresh ComfyUI in your browser to see them!")
