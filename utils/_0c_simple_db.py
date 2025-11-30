import pandas as pd
import json
import numpy as np

# 1. Read the dataset
df = pd.read_csv('utils/AUTALIC.csv')

# 2. Filter out rows where 'target' is empty
# This removes NaN values AND empty strings
df_clean = df[df['target'].notna() & (df['target'] != "")]

# 3. Define the target conditions based on counts of [1, -1, 0]
target_conditions = [
    (3, 0, 0), # All 1s
    (0, 3, 0), # All -1s
    (0, 0, 3), # All 0s
    (2, 1, 0), # Two 1s, one -1
    (1, 2, 0), # Two -1s, one 1
    (2, 0, 1), # Two 1s, one 0
    (1, 0, 2), # Two 0s, one 1
    (0, 2, 1), # Two -1s, one 0
    (0, 1, 2)  # Two 0s, one -1
]

results = {}
counter = 0
# 4. Iterate and collect rows
for target in target_conditions:
    n_1, n_neg_1, n_0 = target
    
    # Helper to check score distribution
    def check_row_scores(row):
        scores = [row['A1_Score'], row['A2_Score'], row['A3_Score']]
        return (scores.count(1) == n_1 and 
                scores.count(-1) == n_neg_1 and 
                scores.count(0) == n_0)

    # Apply score filter on the CLEANED dataframe
    mask = df_clean.apply(check_row_scores, axis=1)
    filtered_rows = df_clean[mask]
    
    # Get top 5
    selected_rows = filtered_rows.head(5).to_dict(orient='records')
    
    key = f"1:{n_1}, -1:{n_neg_1}, 0:{n_0}"
    key_result = []
    for i in selected_rows:
        key_result.append({
            "id": f"P{counter}",
            **i,
            "principle_id":"",
            "llm_justification":"",
            "llm_evidence_quote":"",
            "expert_opinion":"",
        })
        counter+=1
    results[key] = key_result

# 5. Save to JSON
with open('initial_filtered_dataset.json', 'w') as f:
    json.dump(results, f, indent=4)

print("Processing complete. Rows with empty targets were excluded.")