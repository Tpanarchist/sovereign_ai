import datetime
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

import orjson
from pydantic import BaseModel, Field, HttpUrl, SecretStr


def serialize(v, *, default, **kwargs):
    return orjson.dumps(v, default=default, **kwargs).decode()


def timeline():
    return datetime.datetime.now(datetime.timezone.utc)


class Event(BaseModel):
    origin: str
    content: str
    name: Optional[str] = None
    action: Optional[str] = None
    timestamp: datetime.datetime = Field(default_factory=timeline)
    end_condition: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

    def __str__(self) -> str:
        return str(self.model_dump(exclude_none=True))


class Session(BaseModel):
    id: Union[str, UUID] = Field(default_factory=uuid4)
    dob: datetime.datetime = Field(default_factory=timeline)
    auth: Dict[str, SecretStr]
    model_id: str
    system: str
    params: Dict[str, Any] = {}
    event_stream: List[Event] = []
    input_fields: Set[str] = {}
    recent_messages: Optional[int] = None
    save_messages: Optional[bool] = True
    total_prompt_length: int = 0
    total_completion_length: int = 0
    total_length: int = 0
    title: Optional[str] = None

    def __str__(self) -> str:
        start_str = self.dob.strftime("%Y-%m-%d %H:%M:%S")
        end_str = self.event_stream[-1].timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"Session began {start_str} — {len(self.event_stream):,} events, last at {end_str}"

    def format_input_events(
        self, system_event: Event, user_event: Event
    ) -> list:
        recent = (
            self.event_stream[-self.recent_messages:]
            if self.recent_messages else self.event_stream
        )
        return (
            [system_event.model_dump(include=self.input_fields, exclude_none=True)]
            + [
                e.model_dump(include=self.input_fields, exclude_none=True)
                for e in recent
            ]
            + [user_event.model_dump(include=self.input_fields, exclude_none=True)]
        )

    def add_events(
        self,
        user_event: Event,
        response_event: Event,
        save_messages: bool = None,
    ) -> None:
        to_save = isinstance(save_messages, bool)
        if to_save:
            if save_messages:
                self.event_stream.append(user_event)
                self.event_stream.append(response_event)
        elif self.save_messages:
            self.event_stream.append(user_event)
            self.event_stream.append(response_event)
