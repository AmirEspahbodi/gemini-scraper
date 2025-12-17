import os


class Config:
    CDP_URL = "http://localhost:9222"
    CONCURRENCY_LIMIT = 4
    OUTPUT_FILE = "_2initial_prompts_outputs.json"
    BASE_URL = "https://gemini.google.com/u/1/app"

    # --- USER AGENT ---
    # We define a custom User Agent to be injected into the browser
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    # --- INPUT SELECTORS ---
    SELECTOR_TEXT_AREA = "div[contenteditable='true'][role='textbox']"

    # --- Expand Menue
    HISTORY_SEARCH_BUTTON = "mat-icon[data-mat-icon-name='search']"
    EXPAND_MENUE_SELECTOR = "mat-icon[data-mat-icon-name='menu']"

    # --- Enable Think Mode ---
    SELECTOR_MODEL_DROPDOWN = "mat-icon[data-mat-icon-name='keyboard_arrow_down']"
    SELECTOR_THINKING_MODEL_OPTION = "button[data-test-id='bard-mode-option-thinking']"

    # --- TEMPORARY CHAT SELECTORS ---
    SELECTOR_CHAT_OPTIONS_BTN = "button[data-test-id='temp-chat-button']"
    TEXT_TEMP_CHAT_TOGGLE = "div[data-placeholder='Ask questions in a temporary chat']"
    SELECTOR_TEMP_CHAT_INDICATOR = (
        "div[data-placeholder='Ask questions in a temporary chat']"
    )

    # --- RESPONSE HANDLING ---
    SELECTOR_SEND_BUTTON = "button[aria-label*='Send']"
    SELECTOR_STOP_GENERATION = "button[aria-label*='Stop']"

    # Timeouts
    TIMEOUT_PAGE_LOAD = 30000
    TIMEOUT_GENERATION = 120000
