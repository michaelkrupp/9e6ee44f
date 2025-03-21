import json
from dataclasses import asdict
from typing import Final, Self
from uuid import uuid4

from pydantic import Field, dataclasses

type ChatRoomID = str


@dataclasses.dataclass
class ChatRoom:
    id: Final[ChatRoomID] = Field(default_factory=lambda: str(uuid4()))

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        data = json.loads(json_str)
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(asdict(self))
