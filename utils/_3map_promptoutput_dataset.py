import json

id_dataset = {}
with open("_0initial_filtered_dataset.json", "r") as fp:
    temp = json.load(fp)
    for t in temp:
        id_dataset[t["id"]] = {
            "preceding": t["preceding"],
            "target": t["target"],
            "following": t["following"],
            "A1_Score": t["A1_Score"],
            "A2_Score": t["A2_Score"],
            "A3_Score": t["A3_Score"],
            "principle_id": t["principle_id"],
            "llm_justification": t["llm_justification"],
            "llm_evidence_quote": t["llm_evidence_quote"],
            "expert_opinion": t["expert_opinion"],
        }

key_ready_prompts_outputs = {}
with open("_3ready_prompts_outputs.json", "r") as fp:
    temp = json.load(fp)
    for t in temp:
        key_ready_prompts_outputs[t["key"]] = t["value"]
finall_output = []
for id, dataset_value in id_dataset.items():
    if id in key_ready_prompts_outputs:
        llm_value = key_ready_prompts_outputs[id]
        finall_output.append(
            {
                "id": id,
                "preceding": dataset_value["preceding"],
                "target": dataset_value["target"],
                "following": dataset_value["following"],
                "A1_Score": dataset_value["A1_Score"],
                "A2_Score": dataset_value["A2_Score"],
                "A3_Score": dataset_value["A3_Score"],
                "principle_id": llm_value["principle_id"],
                "llm_justification": llm_value["justification_reasoning"],
                "llm_evidence_quote": llm_value["evidence_quote"],
                "expert_opinion": "",
                "isRevised": False,
                "reviserName": "",
                "revisionTimestamp": None,
            }
        )
    else:
        print(id)
