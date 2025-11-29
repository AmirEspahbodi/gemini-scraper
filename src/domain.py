from dataclasses import dataclass
from typing import Optional

@dataclass
class PromptTask:
    unique_id: str
    text: str

@dataclass
class ScrapeResult:
    unique_id: str
    prompt_text: str
    output: str
    status: str = "success" # success or error