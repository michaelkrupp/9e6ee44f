import json
from dataclasses import asdict
from enum import Enum
from typing import Any, Final, Self
from uuid import uuid4

from pydantic import Field, dataclasses, validator

from .chat_room import ChatRoomID

type ChatNotificationID = str


class ChatNotificationKind(str, Enum):
    ROOMS_UPDATED = "rooms_updated"


@dataclasses.dataclass
class ChatNotification:
    kind: Final[ChatNotificationKind]
    room_ids: Final[list[ChatRoomID]]
    id: Final[ChatNotificationID] = Field(default_factory=lambda: str(uuid4()))

    @classmethod
    def from_json(cls, json_str: str, **kwargs) -> Self:
        data = json.loads(json_str)
        return cls(**data, **kwargs)

    def to_json(self) -> str:
        return json.dumps(asdict(self))
