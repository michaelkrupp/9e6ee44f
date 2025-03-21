import json
from dataclasses import asdict
from typing import Final, Self
from uuid import uuid4

from pydantic import Field, dataclasses

type ChatMessageID = str


@dataclasses.dataclass
class ChatMessage:
    sender: Final[str]

    text: Final[str] = Field(default="")
    id: Final[ChatMessageID] = Field(default_factory=lambda: str(uuid4()))

    @classmethod
    def from_json(cls, json_str: str, **kwargs) -> Self:
        data = json.loads(json_str)
        return cls(**data, **kwargs)

    def to_json(self) -> str:
        return json.dumps(asdict(self))
