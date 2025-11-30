import json

def parse_nested_json(file_path):
    """
    Loads a JSON file containing a list of objects, where the 'prompt_output'
    field is a JSON string. It parses this string into a dictionary for each item.

    Args:
        file_path (str): The path to the input JSON file.

    Returns:
        list: The transformed list of dictionaries, or None if an error occurs.
    """
    print(f"--- Loading data from {file_path} ---")

    try:
        # 1. Load the main JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding main JSON structure: {e}")
        return None

    # 2. Iterate and parse the nested JSON string
    transformed_data = []

    for i, item in enumerate(data):
        prompt_output_string = item.get("prompt_output")

        if prompt_output_string is None:
            print(f"Warning: Item {i} is missing the 'prompt_output' field. Skipping.")
            transformed_data.append(item)
            continue

        try:
            # Convert the JSON string into a Python dictionary
            parsed_output = json.loads(prompt_output_string)

            # Replace the string value with the actual dictionary
            item["prompt_output"] = parsed_output

            transformed_data.append(item)

        except json.JSONDecodeError as e:
            print(f"Error decoding nested JSON in item {i} (Prompt ID: {item.get('prompt_id', 'N/A')}): {e}")
            print(f"Problematic string segment: {prompt_output_string[:100]}...") # Print first 100 chars for context
            transformed_data.append(item) # Keep original data if parsing failed

    print("\n--- Transformation Complete ---")
    return transformed_data

def save_json_data(data, file_path):
    """
    Saves the given Python list/dictionary to a JSON file.

    Args:
        data (list or dict): The data structure to save.
        file_path (str): The path to the output JSON file.
    """
    print(f"--- Saving data to {file_path} ---")
    try:
        # Use indent=4 for pretty-printing the output file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully saved {len(data)} items to {file_path}")
    except IOError as e:
        print(f"Error saving file '{file_path}': {e}")


# Define the file paths
input_file_name = '_2initial_prompts_outputs.json'
output_file_name = '_3ready_prompts_outputs.json'

# Execute the parsing function
final_data = parse_nested_json(input_file_name)

if final_data:
    # Save the transformed data to the new file
    save_json_data(final_data, output_file_name)

    # Print the structure of the first item to show the change
    print("\n--- Transformed Data Structure (First Item) ---")
    # Use json.dumps to pretty-print the Python dictionary for clarity
    print(json.dumps(final_data[0], indent=4))

    # Verify the type of the nested field
    print(f"\nType of 'prompt_output' in the first item: {type(final_data[0]['prompt_output'])}")

    # Show that you can now access nested fields directly
    print(f"Accessing nested field 'is_ableist': {final_data[0]['prompt_output']['is_ableist']}")