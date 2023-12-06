from enum import Enum
from typing import Union

from pydantic import BaseModel


class SpiderType(int, Enum):
    video: 0
    reply: 1
    sub_reply: 2
    rank: 3


class SpiderParam(BaseModel):
    name: str = "DefaultSpyder"
    type: int = 0
    is_loop: bool = True
    interval: int = 600
    is_working: Union[bool, None] = False
