import asyncio
from src.orchestrator import Orchestrator

# Sample Prompts
PROMPT_LIST = [
    {"id": "101", "prompt": "Explain Quantum Entanglement simply."},
    {"id": "102", "prompt": "Write a python function to calculate fibonacci."},
    {"id": "103", "prompt": "What is the capital of France?"},
]

async def main():
    # Initialize Orchestrator with prompt list
    orchestrator = Orchestrator(PROMPT_LIST)
    
    # Run the scraper
    await orchestrator.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Scraper stopped by user.")