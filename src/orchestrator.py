import asyncio
import json
from typing import List, Dict
from loguru import logger
from src.domain import PromptTask, ScrapeResult
from src.browser_core import BrowserCore
from src.page_handler import GeminiTabHandler
from src.config import Config

class Orchestrator:
    def __init__(self, prompts: List[Dict]):
        self.queue = asyncio.Queue()
        self.raw_prompts = prompts
        self.results: Dict[str, str] = {} # The finall_result dict
        self.browser_core = BrowserCore()

    async def _worker(self, worker_id: int):
        """The lifecycle of a single tab."""
        page = await self.browser_core.context.new_page()
        handler = GeminiTabHandler(page, worker_id)
        
        await handler.initialize()
        
        while not self.queue.empty():
            task: PromptTask = await self.queue.get()
            
            # Enable thinking mode (optional/per prompt)
            await handler.enable_thinking_mode()
            
            # Process
            result = await handler.process_prompt(task)
            
            # Store Result
            self.results[task.unique_id] = result.output
            logger.success(f"Task {task.unique_id} completed.")
            
            # Reset for next prompt
            await handler.start_new_chat()
            
            self.queue.task_done()
        
        # Cleanup page when done
        await page.close()

    async def run(self):
        # 1. Populate Queue
        for p in self.raw_prompts:
            await self.queue.put(PromptTask(unique_id=p['id'], text=p['prompt']))

        # 2. Connect Browser
        await self.browser_core.connect()

        # 3. Spawn Workers (Tabs)
        workers = []
        # Create exactly CONCURRENCY_LIMIT workers
        # Even if we have 100 prompts, only 5 tabs will open and consume the queue
        num_workers = min(Config.CONCURRENCY_LIMIT, len(self.raw_prompts))
        
        logger.info(f"Spawning {num_workers} worker tabs...")
        
        for i in range(num_workers):
            workers.append(asyncio.create_task(self._worker(i+1)))

        # 4. Wait for completion
        await self.queue.join()
        await asyncio.gather(*workers)

        # 5. Save Results
        self.save_results()
        
        # 6. Cleanup
        # Note: We usually don't close the browser here if the user wants to keep using it,
        # but we disconnect the playwright session.
        await self.browser_core.playwright.stop()

    def save_results(self):
        logger.info("Saving results to JSON...")
        try:
            with open(Config.OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=4)
            logger.success(f"Successfully saved to {Config.OUTPUT_FILE}")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")