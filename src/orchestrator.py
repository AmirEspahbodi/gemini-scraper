import asyncio
import json
import os
from typing import Dict, List, Set

from loguru import logger

from src.browser_core import BrowserCore
from src.config import Config
from src.domain import PromptTask
from src.page_handler import GeminiTabHandler


class Orchestrator:
    def __init__(self, prompts: List[Dict]):
        self.queue = asyncio.Queue()
        self.raw_prompts = prompts
        self.browser_core = BrowserCore()
        self.file_lock = asyncio.Lock()

    async def _get_existing_completed_ids(self) -> Set[str]:
        """
        Reads the output file to find which IDs have already been processed.
        Returns a set of IDs to allow O(1) lookup.
        """
        if not os.path.exists(Config.OUTPUT_FILE):
            # If file doesn't exist, create it as an empty list and return empty set
            logger.info(f"{Config.OUTPUT_FILE} not found. Creating new file.")
            with open(Config.OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            return set()

        try:
            with open(Config.OUTPUT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Handle case where file is empty or not a list
                if not isinstance(data, list):
                    return set()

                # Extract IDs
                existing_ids = {item.get("key") for item in data if "key" in item}
                logger.info(
                    f"Found {len(existing_ids)} completed prompts in {Config.OUTPUT_FILE}."
                )
                return existing_ids
        except json.JSONDecodeError:
            logger.warning(
                f"{Config.OUTPUT_FILE} is corrupted or empty. Starting fresh."
            )
            with open(Config.OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            return set()

    async def _append_result_to_file(self, result_entry: Dict):
        """
        Thread-safe append. Reads the file, adds item, writes back.
        """
        async with self.file_lock:
            try:
                current_data = []
                # Read
                if os.path.exists(Config.OUTPUT_FILE):
                    with open(Config.OUTPUT_FILE, "r", encoding="utf-8") as f:
                        try:
                            current_data = json.load(f)
                        except json.JSONDecodeError:
                            current_data = []

                # Append
                current_data.append(result_entry)

                # Write
                with open(Config.OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(current_data, f, ensure_ascii=False, indent=4)

            except Exception as e:
                logger.error(f"Failed to write result to file: {e}")

    async def _worker(self, worker_id: int):
        """The lifecycle of a single tab."""
        page = await self.browser_core.context.new_page()
        handler = GeminiTabHandler(page, worker_id)

        await handler.initialize()

        while not self.queue.empty():
            task: PromptTask = await self.queue.get()
            try:
                if await handler.check_rate_limit():
                    logger.error(
                        f"[Worker {handler.worker_id}] reached rate limit, quiting ... ."
                    )
                    break
            except Exception as e:
                logger.error(
                    f"[Worker {handler.worker_id}] failed to check reaching rate limit"
                )

            try:
                await handler.expand_menu()
                await handler.ensure_temporary_chat()
                await handler.enable_thinking_mode()
                logger.info(
                    f"[Worker {handler.worker_id}] Tab initialized with Temporary Chat with thinking mode."
                )
            except Exception as e:
                logger.error(f"[Worker {handler.worker_id}] Init failed: {e}")

            result = await handler.process_prompt(task)

            output_entry = {"key": result.unique_id, "value": result.output}

            await self._append_result_to_file(output_entry)
            logger.success(f"Saved result for ID {task.unique_id}")

            await handler.start_new_chat()
            self.queue.task_done()

        await page.close()

    async def run(self):
        # 1. Check what is already done
        completed_ids = await self._get_existing_completed_ids()

        # 2. Filter prompts (Exclude ones that are in completed_ids)
        pending_prompts = [p for p in self.raw_prompts if p["id"] not in completed_ids]

        if not pending_prompts:
            logger.success("All prompts are already scraped! Exiting.")
            return

        logger.info(
            f"Resuming scrape. {len(pending_prompts)} prompts remaining out of {len(self.raw_prompts)} total."
        )

        # 3. Populate Queue with ONLY pending prompts
        for p in pending_prompts:
            await self.queue.put(PromptTask(unique_id=p["id"], text=p["prompt"]))

        # 4. Connect Browser
        await self.browser_core.connect()

        # 5. Spawn Workers
        workers = []
        # Don't open more tabs than pending prompts
        num_workers = min(Config.CONCURRENCY_LIMIT, len(pending_prompts))

        logger.info(f"Spawning {num_workers} worker tabs...")

        for i in range(num_workers):
            workers.append(asyncio.create_task(self._worker(i + 1)))

        # 6. Wait for completion
        await self.queue.join()
        await asyncio.gather(*workers)

        # 7. Close Connection
        await self.browser_core.close()
        logger.success("Batch completed.")
