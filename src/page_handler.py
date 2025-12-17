import asyncio
from ast import BoolOp, Return
from asyncio import sleep

from loguru import logger
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeout

from src.config import Config
from src.domain import PromptTask, ScrapeResult


class GeminiTabHandler:
    def __init__(self, page: Page, worker_id: int):
        self.page = page
        self.worker_id = worker_id

    async def initialize(self):
        """Initial startup: Override UA and Go to URL"""
        try:
            # --- UA Override Logic ---
            if hasattr(Config, "USER_AGENT") and Config.USER_AGENT:
                try:
                    # Establish a CDP session for this specific page
                    client = await self.page.context.new_cdp_session(self.page)
                    # Override the User Agent at the protocol level
                    await client.send(
                        "Network.setUserAgentOverride", {"userAgent": Config.USER_AGENT}
                    )
                    logger.debug(
                        f"[Worker {self.worker_id}] User Agent spoofed successfully."
                    )
                except Exception as e:
                    logger.warning(
                        f"[Worker {self.worker_id}] Failed to override User Agent via CDP: {e}"
                    )
            # -------------------------

            await self.page.goto(Config.BASE_URL)
            logger.info(f"[Worker {self.worker_id}] Tab initialized.")
        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] Init failed: {e}")

    async def expand_menu(self):
        """Expands the side menu to access more options."""
        try:
            await sleep(3)
            is_already_expanded = await self.page.locator(
                Config.HISTORY_SEARCH_BUTTON
            ).is_visible()

            if is_already_expanded:
                logger.debug(f"[Worker {self.worker_id}] Already Expanded.")
                return

            menu_button = self.page.locator(Config.EXPAND_MENUE_SELECTOR)
            await menu_button.wait_for(state="visible")
            await menu_button.click()
            logger.debug(f"[Worker {self.worker_id}] Side menu expanded.")
        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] Failed to expand menu:\n{e}")

    async def ensure_temporary_chat(self):
        """
        Logic to switch the current session to Temporary Chat.
        This handles the UI interactions to toggle the setting.
        """
        try:
            # 1. Wait for the chat input to be visible (confirms page loaded)
            await sleep(3)

            await self.page.wait_for_selector(
                Config.SELECTOR_TEXT_AREA, state="visible"
            )

            # 2. Check if we are ALREADY in temporary chat to avoid toggling it OFF.
            is_already_temp = await self.page.locator(
                Config.SELECTOR_TEMP_CHAT_INDICATOR
            ).is_visible()

            if is_already_temp:
                logger.debug(f"[Worker {self.worker_id}] Already in Temporary Chat.")
                return

            # 3. Open the "Conversation Options" menu (Three dots)
            menu_btn = self.page.locator(Config.SELECTOR_CHAT_OPTIONS_BTN)
            await menu_btn.wait_for(state="visible")
            await menu_btn.click()

            # 4. Click "Temporary chat" in the dropdown
            temp_chat_toggle = self.page.locator(Config.TEXT_TEMP_CHAT_TOGGLE)
            await temp_chat_toggle.wait_for(state="visible")
            await temp_chat_toggle.click()

            # 5. Wait for the UI to refresh/confirm
            await self.page.wait_for_selector(
                Config.TEXT_TEMP_CHAT_TOGGLE, timeout=5000
            )

        except PlaywrightTimeout as pe:
            logger.warning(
                f"[Worker {self.worker_id}] Could not confirm Temporary Chat state (UI might differ)."
            )
            logger.error(
                f"[Worker {self.worker_id}] Failed to enable Temporary Chat: {pe}"
            )
        except Exception as e:
            logger.error(
                f"[Worker {self.worker_id}] Failed to enable Temporary Chat: {e}"
            )

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
                await stop_btn.wait_for(
                    state="hidden", timeout=Config.TIMEOUT_GENERATION
                )
            except PlaywrightTimeout:
                pass  # Proceed to extraction

            # Extract Output
            await self.page.wait_for_selector(".markdown", timeout=5000)
            responses = await self.page.locator(".markdown").all_inner_texts()
            final_text = responses[-1] if responses else "No output extracted"

            return ScrapeResult(
                unique_id=task.unique_id, prompt_text=task.text, output=final_text
            )

        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] Error on {task.unique_id}: {e}")
            return ScrapeResult(
                unique_id=task.unique_id,
                prompt_text=task.text,
                output=str(e),
                status="error",
            )

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
        """
        try:
            logger.debug(
                f"[Worker {self.worker_id}] Ensuring Thinking Mode is active..."
            )

            model_selector = self.page.locator(Config.SELECTOR_MODEL_DROPDOWN)
            await model_selector.wait_for(state="visible")
            await model_selector.click()

            model_mode_selector = self.page.locator(
                Config.SELECTOR_THINKING_MODEL_OPTION
            )
            await model_mode_selector.wait_for(state="visible")
            await model_mode_selector.click()

            await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning(
                f"[Worker {self.worker_id}] Could not explicitly set Thinking Mode: {e}"
            )

    async def check_rate_limit(self) -> bool:
        return False
