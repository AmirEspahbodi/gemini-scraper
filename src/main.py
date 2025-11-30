import asyncio
import json
import os
import sys
from loguru import logger
from src.orchestrator import Orchestrator

# File path for prompts
PROMPTS_FILE = "prompts.json"

def load_prompts(file_path: str):
    if not os.path.exists(file_path):
        logger.error(f"File '{file_path}' not found. Please create it.")
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if not isinstance(data, list):
                logger.error(f"Invalid format in '{file_path}'. Expected a JSON list.")
                sys.exit(1)
                
            logger.info(f"Successfully loaded {len(data)} prompts from {file_path}.")
            return data

    except json.JSONDecodeError:
        logger.error(f"Could not decode JSON in '{file_path}'. Check syntax.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error reading prompts: {e}")
        sys.exit(1)

async def main():
    PROMPT_LIST = load_prompts(PROMPTS_FILE)
    
    orchestrator = Orchestrator(PROMPT_LIST)
    
    await orchestrator.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Scraper stopped by user.")