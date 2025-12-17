import pandas as pd
import json
import numpy as np

# 1. Read the dataset
df = pd.read_csv('utils/AUTALIC.csv')

# 2. Filter out rows where 'target' is empty
# This removes NaN values AND empty strings

results = []
counter = 0

import pandas as pd
from typing import Any

def _replace_in_struct(x: Any) -> Any:
    if isinstance(x, dict):
        return {k: _replace_in_struct(v) if isinstance(v, (dict, list, tuple)) else ('' if pd.isna(v) else v)
                for k, v in x.items()}

    if isinstance(x, list):
        return [_replace_in_struct(v) if isinstance(v, (dict, list, tuple)) else ('' if pd.isna(v) else v)
                for v in x]
    if isinstance(x, tuple):
        return tuple(_replace_in_struct(v) if isinstance(v, (dict, list, tuple)) else ('' if pd.isna(v) else v)
                     for v in x)
    return '' if pd.isna(x) else x

def replace_nans_with_empty(p: Any) -> Any:
    if isinstance(p, pd.DataFrame):
        return p.fillna('')

    if isinstance(p, pd.Series):
        if p.apply(lambda x: isinstance(x, (dict, list, tuple))).all():
            return p.apply(lambda x: _replace_in_struct(x) if pd.notna(x) else '')
        else:
            return p.fillna('')

    if isinstance(p, list):
        return [_replace_in_struct(x) for x in p]

    return '' if pd.isna(p) else p


df_clean = df[df['target'].notna() & (df['target'] != "")]
df_clean = replace_nans_with_empty(df_clean)

selected_rows = df_clean.to_dict(orient='records')

for i in selected_rows:
    i
    results.append({
        "id": f"P{counter}",
        **i,
        "principle_id":"",
        "llm_justification":"",
        "llm_evidence_quote":"",
        "expert_opinion":"",
    })
    counter+=1

# 5. Save to JSON
with open('_0initial_filtered_dataset.json', 'w') as f:
    json.dump(results, f, indent=4)

print("Processing complete. Rows with empty targets were excluded.")
