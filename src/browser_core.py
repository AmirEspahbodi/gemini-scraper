from playwright.async_api import async_playwright, Browser, BrowserContext
from loguru import logger
from src.config import Config

class BrowserCore:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    async def connect(self):
        """Connects to the existing Chrome instance via CDP."""
        try:
            self.playwright = await async_playwright().start()
            logger.info(f"Connecting to Chrome at {Config.CDP_URL}...")
            self.browser = await self.playwright.chromium.connect_over_cdp(Config.CDP_URL)
            self.context = self.browser.contexts[0] # Use the default context
            logger.success("Connected to Chrome successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Chrome: {e}")
            raise

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()