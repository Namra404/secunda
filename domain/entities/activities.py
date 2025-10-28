from dataclasses import dataclass
from uuid import UUID

@dataclass
class Activity:
    id: UUID | None
    name: str
    parent_id: UUID | None
