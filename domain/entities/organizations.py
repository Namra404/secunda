from dataclasses import dataclass
from uuid import UUID

from domain.entities.activities import Activity

@dataclass
class Organization:
    id: UUID | None
    name: str
    building_id: UUID
    phones: list[str]
    activities: list[Activity]