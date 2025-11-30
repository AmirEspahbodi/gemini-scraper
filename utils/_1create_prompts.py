import json
from typing import List, Dict, Any

# result list required by your spec
prompts: List[Dict[str, Any]] = []

# read initial prompt (plain text)
with open('_0initial_prompt.txt', 'r', encoding='utf-8') as f:
    initial_prompt: str = f.read()

# load the complex json and flatten its list values into filtered_samples
with open('initial_filtered_dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

filtered_samples = []
if isinstance(data, dict):
    for v in data.values():
        if isinstance(v, list):
            filtered_samples.extend(v)
        else:
            # if some value is a single sample (not list), handle gracefully
            filtered_samples.append(v)
else:
    raise ValueError("initial_filtered_dataset.json must contain a top-level dictionary")

# create prompts for each sample
for sample in filtered_samples:
    # ensure sample is a dict
    if not isinstance(sample, dict):
        continue

    sample_id = sample.get('id')
    preceding = sample.get('preceding', '') or ''
    target = sample.get('target', '') or ''
    following = sample.get('following', '') or ''

    # Try using str.format first (works if initial_prompt uses {preceding}, {target}, {following})
    try:
        prompt_text = initial_prompt.format(
            preceding=preceding,
            target=target,
            following=following
        )
    except Exception:
        # fallback to safe manual replacement if formatting fails (e.g., braces or other placeholders exist)
        prompt_text = (initial_prompt
                       .replace('{preceding}', preceding)
                       .replace('{target}', target)
                       .replace('{following}', following))

    entry = {
        'id': sample_id,
        'prompt': prompt_text
    }
    prompts.append(entry)

# Optional: write resulting prompts to a JSON file for inspection (comment out if you don't want this)
with open('_1prompts.json', 'w', encoding='utf-8') as out_f:
    json.dump(prompts, out_f, ensure_ascii=False, indent=2)

# summary output
print(f"Loaded initial_prompt (length={len(initial_prompt)}).")
print(f"Found {len(filtered_samples)} filtered samples -> created {len(prompts)} prompts.")
if prompts:
    print("Example (first 1):")
    print(json.dumps(prompts[0], ensure_ascii=False, indent=2))
