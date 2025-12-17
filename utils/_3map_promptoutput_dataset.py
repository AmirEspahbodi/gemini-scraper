import json
from typing import List, Dict, Any

# --- File Paths ---
READY_PROMPTS_FILE = '_3ready_prompts_outputs.json'
INITIAL_DATASET_FILE = '_0initial_filtered_dataset.json'
FINAL_RESULT_FILE = '_4site_finall_result.json'
EXPERT_FINAL_RESULT_FILE = '_4expert_finall_result.json'

def load_json_file(filepath: str) -> Any:
    """Loads and returns the content of a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        return None

def load_and_prepare_data(ready_file: str, initial_file: str) -> tuple[List[Dict], List[Dict], Dict[str, List[Dict]]]:
    """
    Loads data from both JSON files and prepares them for mapping.

    Returns:
        A tuple containing:
        1. ready_prompts_outputs (List[Dict]): The list from the first file.
        2. initial_filtered_dataset (List[Dict]): The concatenated list of all items from the second file.
        3. initial_data_by_key (Dict[str, List[Dict]]): The structure of the second file for key preservation.
    """
    # 1. Load data from both files
    ready_prompts_outputs = load_json_file(ready_file)
    initial_data_by_key = load_json_file(initial_file)

    if ready_prompts_outputs is None or initial_data_by_key is None:
        return [], [], {}

    # 2. Prepare 'initial_filtered_dataset' by concatenating all lists
    initial_filtered_dataset = []
    for key in initial_data_by_key:
        initial_filtered_dataset.extend(initial_data_by_key[key])

    print(f"Loaded {len(ready_prompts_outputs)} items from {ready_file}")
    print(f"Loaded {len(initial_filtered_dataset)} items from {initial_file} (total across all keys)")

    return ready_prompts_outputs, initial_filtered_dataset, initial_data_by_key

def map_and_save_data(ready_prompts_outputs: List[Dict], initial_data_by_key: Dict[str, List[Dict]]):
    """
    Performs the mapping, updates the data, and saves it to two files.
    """
    # Create a dictionary for efficient lookup from 'ready_prompts_outputs'
    # Key: key, Value: value object
    value_map = {}
    for item in ready_prompts_outputs:
        if 'key' in item and 'value' in item:
            value_map[item['key']] = item['value']

    # Initialize the lists for the two output files
    final_result_list: List[Dict] = []
    expert_final_result_dict: Dict[str, List[Dict]] = {}
    mapped_count = 0

    # 1. Map and update the data
    for score_key, items in initial_data_by_key.items():
        # Initialize the list for the 'expert_final_result.json' structure
        expert_final_result_dict[score_key] = []
        
        for item in items:
            item_id = item.get('id')
            
            if item_id in value_map:
                # Get the value for the matching ID
                output = value_map[item_id]
                if not isinstance(output, dict):
                    print(f"Warning: Expected a dictionary for value, got {type(output)} for ID {item_id}")
                    continue
                
                # Perform the required mapping (Source -> Destination)
                # value.justification_reasoning -> llm_justification
                
                item['llm_justification'] = output.get('justification_reasoning', item.get('llm_justification'))
                
                # value.evidence_quote -> llm_evidence_quote
                item['llm_evidence_quote'] = output.get('evidence_quote', item.get('llm_evidence_quote'))
                
                # value.principle_id -> principle_id
                item['principle_id'] = output.get('principle_id', item.get('principle_id'))

                mapped_count += 1
            
            # Add the (potentially updated) item to both output structures
            final_result_list.append(item)
            expert_final_result_dict[score_key].append(item)

    print(f"Successfully mapped and updated {mapped_count} records.")

    # 2. Save the results to the specified files
    
    # a) Save to 'finall_result.json' (List structure)
    try:
        with open(FINAL_RESULT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_result_list, f, indent=4)
        print(f"✅ Data saved to {FINAL_RESULT_FILE} (List structure).")
    except Exception as e:
        print(f"Error saving to {FINAL_RESULT_FILE}: {e}")

    # b) Save to 'expert_finall_result.json' (Dictionary structure, preserving keys)
    try:
        with open(EXPERT_FINAL_RESULT_FILE, 'w', encoding='utf-8') as f:
            json.dump(expert_final_result_dict, f, indent=4)
        print(f"✅ Data saved to {EXPERT_FINAL_RESULT_FILE} (Original Dictionary structure).")
    except Exception as e:
        print(f"Error saving to {EXPERT_FINAL_RESULT_FILE}: {e}")

# --- Main Execution Block ---
def main():
    """Runs the full process of loading, mapping, and saving data."""
    print("🚀 Starting JSON data processing and mapping...")
    
    # Load and prepare data
    ready_prompts_outputs, _, initial_data_by_key = load_and_prepare_data(
        READY_PROMPTS_FILE, INITIAL_DATASET_FILE
    )
    
    if not ready_prompts_outputs or not initial_data_by_key:
        print("🛑 Process aborted due to data loading errors.")
        return

    # Map and save the results
    map_and_save_data(ready_prompts_outputs, initial_data_by_key)

if __name__ == "__main__":
    # Note: To run this script, ensure 'ready_prompts_outputs.json' and 
    # 'initial_filtered_dataset.json' exist in the same directory as the script.
    main()