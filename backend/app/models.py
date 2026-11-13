from pydantic import BaseModel, Field
from typing import Literal

class GenerateRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=180)
    duration: Literal["30", "45", "60"] = "45"
    style: Literal["educational", "storytelling", "entertaining"] = "educational"
    voice: str = "en-US-AriaNeural"
    use_ai_images: bool = True
    use_music: bool = False
