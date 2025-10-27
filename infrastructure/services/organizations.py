from dataclasses import dataclass
from uuid import UUID

from configuration.entities.organizations import Organization
from infrastructure.repositories.organizations import OrganizationsRepository


@dataclass
class OrganizationsService:
    repository: OrganizationsRepository

    async def create(self, org: Organization) -> Organization:
        return await self.repository.create(org)

    async def get_by_id(self, org_id: UUID) -> Organization | None:
        return await self.repository.get_by_id(org_id)

    async def list_all(self) -> list[Organization]:
        return await self.repository.list_all()

    async def list_by_building(self, building_id: UUID) -> list[Organization]:
        return await self.repository.list_by_building_id(building_id)

    async def list_by_activity_id(self, activity_id: UUID) -> list[Organization]:
        return await self.repository.list_by_activity_id(activity_id)

    async def list_by_activity_name(self, activity_name: str) -> list[Organization]:
        return await self.repository.list_by_activity_name(activity_name)

    async def find_by_name(self, name: str) -> list[Organization]:
        return await self.repository.find_organization_by_name(name)

    async def list_by_square(self, lat_min: float, lon_min: float, lat_max: float, lon_max: float):
        return await self.repository.list_by_square(lat_min, lon_min, lat_max, lon_max)