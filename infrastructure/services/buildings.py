from dataclasses import dataclass
from uuid import UUID

from configuration.entities.buildings import Building
from infrastructure.repositories.buildings import BuildingsRepository


@dataclass
class BuildingService:
    repository: BuildingsRepository

    async def create_building(self, building: Building) -> Building:
        return await self.repository.create(building=building)

    async def get_building_by_id(self, building_id: UUID) -> Building:
        return await self.repository.get_by_id(building_id=building_id)

    async def list_all_buildings(self) -> list[Building]:
        return await self.repository.list_all()

    async def list_buildings_in_square(self, lat_min: float, lon_min: float, lat_max: float, lon_max: float,) -> list[Building]:
        buildings = await self.repository.list_by_square(lat_min, lon_min, lat_max, lon_max)
        if not buildings:
            return []
        return buildings