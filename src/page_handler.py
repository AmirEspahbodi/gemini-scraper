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
        """Initial startup: Go to URL and enable temp chat."""
        try:
            await self.page.goto(Config.BASE_URL)
            await self.expand_menu()
            await self.ensure_temporary_chat()
            logger.info(f"[Worker {self.worker_id}] Tab initialized with Temporary Chat.")
        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] Init failed: {e}")

    async def expand_menu(self):
        """Expands the side menu to access more options."""
        try:
            menu_button = self.page.locator(Config.EXPAND_MENUE_SELECTOR)
            await menu_button.wait_for(state="visible")
            await menu_button.click()
            logger.debug(f"[Worker {self.worker_id}] Side menu expanded.")
        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] Failed to expand menu: {e}")

    async def ensure_temporary_chat(self):
        """
        Logic to switch the current session to Temporary Chat.
        This handles the UI interactions to toggle the setting.
        """
        try:
            # 1. Wait for the chat input to be visible (confirms page loaded)
            await self.page.wait_for_selector(Config.SELECTOR_TEXT_AREA, state="visible")

            # 2. Check if we are ALREADY in temporary chat to avoid toggling it OFF.
            # (Gemini often shows a banner or bottom text saying 'Activity is off' or 'Temporary chat is on')
            is_already_temp = await self.page.locator(Config.SELECTOR_TEMP_CHAT_INDICATOR).is_visible()
            
            if is_already_temp:
                logger.debug(f"[Worker {self.worker_id}] Already in Temporary Chat.")
                return

            # 3. Open the "Conversation Options" menu (Three dots)
            menu_btn = self.page.locator(Config.SELECTOR_CHAT_OPTIONS_BTN)
            await menu_btn.wait_for(state="visible")
            await menu_btn.click()

            # 4. Click "Temporary chat" in the dropdown
            # We use get_by_text because it's the most robust way to find this menu item
            
            temp_chat_toggle = self.page.locator(Config.TEXT_TEMP_CHAT_TOGGLE)
            # print({temp_chat_toggle})
            await temp_chat_toggle.wait_for(state="visible")
            await temp_chat_toggle.click()
            
            # await self.page.get_by_text(Config.TEXT_TEMP_CHAT_TOGGLE).click()

            # 5. Wait for the UI to refresh/confirm
            # Gemini usually reloads the chat view slightly when this happens
            await self.page.wait_for_selector(Config.TEXT_TEMP_CHAT_TOGGLE, timeout=5000)
            
        except PlaywrightTimeout:
            logger.warning(f"[Worker {self.worker_id}] Could not confirm Temporary Chat state (UI might differ).")
        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] Failed to enable Temporary Chat: {e}")

    async def process_prompt(self, task: PromptTask) -> ScrapeResult:
        try:
            logger.info(f"[Worker {self.worker_id}] Processing: {task.unique_id}")

            textarea = self.page.locator(Config.SELECTOR_TEXT_AREA)
            await textarea.wait_for(state="visible")
            
            # Focus and Fill
            await textarea.click() 
            await textarea.fill(task.text)
            await asyncio.sleep(0.5) 
            await self.page.keyboard.press("Enter")

            # Wait for generation to Start and then Finish
            try:
                stop_btn = self.page.locator(Config.SELECTOR_STOP_GENERATION)
                # Wait for start
                await stop_btn.wait_for(state="visible", timeout=5000)
                # Wait for finish
                await stop_btn.wait_for(state="hidden", timeout=Config.TIMEOUT_GENERATION)
            except PlaywrightTimeout:
                pass # Proceed to extraction

            # Extract Output
            # We fetch all markdown blocks and take the last one
            await self.page.wait_for_selector(".markdown", timeout=5000)
            responses = await self.page.locator(".markdown").all_inner_texts()
            final_text = responses[-1] if responses else "No output extracted"

            return ScrapeResult(unique_id=task.unique_id, prompt_text=task.text, output=final_text)

        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] Error on {task.unique_id}: {e}")
            return ScrapeResult(unique_id=task.unique_id, prompt_text=task.text, output=str(e), status="error")

    async def start_new_chat(self):
        """
        Resets for the next prompt.
        Requirement: Must open Temporary Chat again (effectively resetting context).
        """
        try:
            # Reloading the page is the cleanest way to ensure a fresh state
            # Then we re-run the ensure_temporary_chat logic
            await self.page.goto(Config.BASE_URL)
            await self.expand_menu()
            await self.ensure_temporary_chat()
        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] Failed to reset chat: {e}")

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