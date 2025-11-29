import asyncio
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout
from src.config import Config
from src.domain import PromptTask, ScrapeResult
from loguru import logger

class GeminiTabHandler:
    def __init__(self, page: Page, worker_id: int):
        self.page = page
        self.worker_id = worker_id

    async def initialize(self):
        """Navigates to Gemini and prepares the session."""
        try:
            await self.page.goto(Config.BASE_URL)
            await self.page.wait_for_selector(Config.SELECTOR_TEXT_AREA, state="visible")
            logger.info(f"[Worker {self.worker_id}] Tab initialized.")
        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] Init failed: {e}")

    async def enable_thinking_mode(self):
        """
        Attempts to enable thinking mode. 
        Note: Specific UI clicks depend heavily on current Google A/B testing.
        """
        try:
            # Logic: Click model dropdown -> Select 'Thinking' model
            # This is a placeholder logic as selectors vary by user account type
            logger.debug(f"[Worker {self.worker_id}] Ensuring Thinking Mode is active...")
            
            # Example logic (Commented out as it's fragile without specific DOM snapshot)
            # await self.page.click(Config.SELECTOR_MODEL_DROPDOWN)
            # await self.page.click(Config.SELECTOR_THINKING_MODEL_OPTION)
            
            # For now, we assume the user sets the model once or we send a precise click
            await asyncio.sleep(0.5) 
        except Exception as e:
            logger.warning(f"[Worker {self.worker_id}] Could not explicitly set Thinking Mode: {e}")

    async def process_prompt(self, task: PromptTask) -> ScrapeResult:
        try:
            logger.info(f"[Worker {self.worker_id}] Processing: {task.unique_id}")

            # 1. Type Prompt
            textarea = self.page.locator(Config.SELECTOR_TEXT_AREA)
            await textarea.click()
            await textarea.fill(task.text)
            
            # 2. Send
            await self.page.keyboard.press("Enter")
            # Or click send button: await self.page.click(Config.SELECTOR_SEND_BUTTON)

            # 3. Wait for response to complete
            # We wait for the 'Stop generating' button to appear, then disappear
            # Or we wait for the generation stream to finish.
            
            # Simple heuristic: Wait for a moment, then wait for network idle or specific UI state
            await asyncio.sleep(2) # Give it a second to start
            
            # Wait for the "Stop" button to DETACH/HIDE (meaning generation is done)
            try:
                stop_btn = self.page.locator(Config.SELECTOR_STOP_GENERATION)
                if await stop_btn.is_visible():
                    await stop_btn.wait_for(state="hidden", timeout=Config.TIMEOUT_GENERATION)
            except PlaywrightTimeout:
                logger.warning(f"[Worker {self.worker_id}] Timeout waiting for generation to end.")

            # 4. Extract Output
            # Gemini structure usually puts the last response in a specific container
            # We fetch all markdown blocks and take the last one
            responses = await self.page.locator(".markdown").all_inner_texts()
            
            final_text = responses[-1] if responses else "No output extracted"

            return ScrapeResult(unique_id=task.unique_id, prompt_text=task.text, output=final_text)

        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] Error on {task.unique_id}: {e}")
            return ScrapeResult(unique_id=task.unique_id, prompt_text=task.text, output=str(e), status="error")

    async def start_new_chat(self):
        """Resets the chat for the next prompt."""
        try:
            # Usually clicking 'New Chat' button or simply reloading the page
            # Reloading is often more robust for clearing context
            await self.page.goto(Config.BASE_URL)
            await self.page.wait_for_selector(Config.SELECTOR_TEXT_AREA)
        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] Failed to reset chat: {e}")