import os

class Config:
    CDP_URL = "http://localhost:9222"
    CONCURRENCY_LIMIT = 4
    OUTPUT_FILE = "finall_result.json"
    BASE_URL = "https://gemini.google.com/app"

    # --- INPUT SELECTORS ---
    SELECTOR_TEXT_AREA = "div[contenteditable='true'][role='textbox']"
    
    # --- Expand Menue
    HISTORY_SEARCH_BUTTON = "mat-icon[data-mat-icon-name='search']"
    EXPAND_MENUE_SELECTOR = "mat-icon[data-mat-icon-name='menu']"
    
    # --- TEMPORARY CHAT SELECTORS ---
    # The 'three dots' menu at the top right of the chat area
    # Note: aria-label might be 'Conversation options' or 'More options' depending on version
    SELECTOR_CHAT_OPTIONS_BTN = "button[data-test-id='temp-chat-button']" 
    
    # The actual menu item to click. We will use a text locator for this in the code
    # because the class names are obfuscated.
    TEXT_TEMP_CHAT_TOGGLE = "div[data-placeholder='Ask questions in a temporary chat']"
    
    # Indicator that temp chat is active (usually a banner or specific element)
    # We use this to verify the state.
    SELECTOR_TEMP_CHAT_INDICATOR = "div[data-placeholder='Ask questions in a temporary chat']"

    # --- RESPONSE HANDLING ---
    SELECTOR_SEND_BUTTON = "button[aria-label*='Send']" 
    SELECTOR_STOP_GENERATION = "button[aria-label*='Stop']" 
    
    # Timeouts
    TIMEOUT_PAGE_LOAD = 30000
    TIMEOUT_GENERATION = 120000