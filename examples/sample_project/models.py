from typing import List

import pika_pydantic


class Message(pika_pydantic.BaseModel):
    title: str
    text: str


class CollectedData(pika_pydantic.BaseModel):
    counter: int
    data: List[str]
