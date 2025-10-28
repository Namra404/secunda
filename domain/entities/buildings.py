from uuid import UUID
from dataclasses import dataclass


@dataclass
class Building:
    id: UUID | None
    address: str
    latitude: float
    longitude: float