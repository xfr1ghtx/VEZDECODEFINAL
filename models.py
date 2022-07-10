from typing import Union, Optional

from pydantic import BaseModel


class CreateMeme(BaseModel):
    image_url: Optional[str] = None
    top_text: Optional[str] = None
    bottom_text: Optional[str] = None


class Meme(BaseModel):
    meme_id: int
    image_url: str
    src_url: str
    top_text: str
    bottom_text: str
