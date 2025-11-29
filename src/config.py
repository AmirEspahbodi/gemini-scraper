import os

class Config:
    # Connection settings
    CDP_URL = "http://localhost:9222"
    CONCURRENCY_LIMIT = 1
    OUTPUT_FILE = "finall_result.json"
    
    # Gemini URL
    BASE_URL = "https://gemini.google.com/app"

    # Selectors (These are fragile in dynamic apps, kept centralized here)
    # Note: Selectors are based on ARIA labels and roles where possible for robustness
    SELECTOR_TEXT_AREA = "div[contenteditable='true']" # The main chat input
    SELECTOR_SEND_BUTTON = "button[aria-label*='Send']" # Send button
    SELECTOR_RESPONSE_CONTAINER = "model-response" # Custom tag often used by Google
    SELECTOR_LATEST_RESPONSE = ".model-response-text" # Class often used for text
    
    # Logic to detect if generation is finished (Wait for 'Stop' button to disappear)
    SELECTOR_STOP_GENERATION = "button[aria-label*='Stop']" 
    
    # Thinking Mode / Model Selector logic
    # This is highly specific. Usually involves a dropdown header.
    SELECTOR_MODEL_DROPDOWN = "button[aria-label*='model']" 
    SELECTOR_THINKING_MODEL_OPTION = "li[data-value*='thinking']" # Pseudo-selector example

    # Timeouts (seconds)
    TIMEOUT_PAGE_LOAD = 30000
    TIMEOUT_GENERATION = 120000 # 2 minutes max for thinking