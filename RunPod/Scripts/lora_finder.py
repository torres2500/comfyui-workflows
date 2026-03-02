#!/usr/bin/env python3
import json
import urllib.request

# ── CONFIGURATION ────────────────────────────────────────────────

CIVITAI_API_KEY = "38681c453aa0a1cdf22e4526c2d9d337"

# ── ADD YOUR MODEL PAGE URLS HERE ────────────────────────────────
# Just paste as many CivitAI model URLs as you want

MODEL_URLS = [

    

    "https://civitai.com/models/1874811",
    # "https://civitai.com/models/000000",
    # "https://civitai.com/models/000000",

]

# ── FETCH AND PRINT ──────────────────────────────────────────────

def get_model_info(model_id):
    """Fetch all version info for a model from the CivitAI API."""
    url = f"https://civitai.com/api/v1/models/{model_id}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Authorization": f"Bearer {CIVITAI_API_KEY}"  # Required for API access
    })
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())  # Parse the JSON response

print("\n" + "=" * 55)
print("  COPY AND PASTE THE BLOCKS BELOW INTO lora_getter.py")
print("=" * 55 + "\n")

for model_url in MODEL_URLS:

    # Extract the model ID from the URL
    # e.g. "https://civitai.com/models/1811313" → "1811313"
    model_id = model_url.rstrip("/").split("/")[-1]

    try:
        data = get_model_info(model_id)
        model_name = data["name"]  # Human-readable name of the model

        print(f"# ── {model_name} (model ID: {model_id}) ──")

        # Loop through every version CivitAI has for this model
        for v in data["modelVersions"]:
            version_id = str(v["id"])           # The version ID
            version_name = v["name"]            # e.g. "14B HIGH", "v1.0"
            filename = v["files"][0]["name"]    # The actual .safetensors filename

            # Print a ready-to-paste block for each version
            print(f"""    {{
        "source":     "civitai",
        "filename":   "{filename}",
        "model_id":   "{model_id}",       # {model_name}
        "version_id": "{version_id}",     # {version_name}
        "api_key":    "{CIVITAI_API_KEY}",
    }},""")

        print()  # Blank line between models for readability

    except Exception as e:
        print(f"# FAILED to fetch model {model_id}: {e}\n")

print("=" * 55)
print("  END — paste the blocks above into your LORAS list")
print("=" * 55 + "\n")
