import asyncio
import json
import aiofiles  # Optional, but standard open() is fine for small files. We use standard here for simplicity.
from typing import List, Dict
from loguru import logger
from src.domain import PromptTask
from src.browser_core import BrowserCore
from src.page_handler import GeminiTabHandler
from src.config import Config

class Orchestrator:
    def __init__(self, prompts: List[Dict]):
        self.queue = asyncio.Queue()
        self.raw_prompts = prompts
        self.browser_core = BrowserCore()
        self.file_lock = asyncio.Lock()

    async def _initialize_file(self):
        """Creates the file with an empty JSON list []"""
        logger.info(f"Initializing {Config.OUTPUT_FILE}...")
        try:
            with open(Config.OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        except Exception as e:
            logger.error(f"Failed to init file: {e}")
            raise

    async def _append_result_to_file(self, result_entry: Dict):
        """
        Safely reads the current list, appends new data, and rewrites the file.
        This uses a Lock to ensure no two workers write at the same time.
        """
        async with self.file_lock:
            try:
                # 1. Read existing data
                current_data = []
                try:
                    with open(Config.OUTPUT_FILE, 'r', encoding='utf-8') as f:
                        current_data = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    current_data = []

                # 2. Append new result
                current_data.append(result_entry)

                # 3. Write back to file
                with open(Config.OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(current_data, f, ensure_ascii=False, indent=4)
                    
            except Exception as e:
                logger.error(f"Failed to write result to file: {e}")

    async def _worker(self, worker_id: int):
        """The lifecycle of a single tab."""
        page = await self.browser_core.context.new_page()
        handler = GeminiTabHandler(page, worker_id)
        
        # Initial setup (open page, enable temp chat)
        await handler.initialize()
        
        while not self.queue.empty():
            task: PromptTask = await self.queue.get()
            
            # Enable thinking mode (optional/per prompt)
            await handler.enable_thinking_mode()
            
            # Process the prompt
            result = await handler.process_prompt(task)
            
            # Formate data as requested
            output_entry = {
                "prompt_id": result.unique_id,
                "prompt_output": result.output
            }
            
            # WRITE IMMEDIATELY
            await self._append_result_to_file(output_entry)
            logger.success(f"Saved result for ID {task.unique_id}")
            
            # Reset chat for next prompt (inc. temp mode)
            await handler.start_new_chat()
            
            self.queue.task_done()
        
        await page.close()

    async def run(self):
        # 1. Initialize the empty JSON file
        await self._initialize_file()

        # 2. Populate Queue
        for p in self.raw_prompts:
            await self.queue.put(PromptTask(unique_id=p['id'], text=p['prompt']))

        # 3. Connect Browser
        await self.browser_core.connect()

        # 4. Spawn Workers
        workers = []
        num_workers = min(Config.CONCURRENCY_LIMIT, len(self.raw_prompts))
        
        logger.info(f"Spawning {num_workers} worker tabs...")
        
        for i in range(num_workers):
            workers.append(asyncio.create_task(self._worker(i+1)))

        # 5. Wait for completion
        await self.queue.join()
        await asyncio.gather(*workers)
        
        # 6. Stop Playwright (but don't close Chrome)
        await self.browser_core.close()
        logger.success("All tasks completed.")
