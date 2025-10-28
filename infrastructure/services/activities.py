from dataclasses import dataclass
from uuid import UUID

from domain.entities.activities import Activity
from infrastructure.repositories.activities import ActivitiesRepository


@dataclass
class ActivitiesService:
    repository: ActivitiesRepository

    async def create(self, activity: Activity) -> Activity:

        return await self.repository.create(activity)

    async def get_by_id(self, activity_id: UUID) -> Activity:

        return await self.repository.get_by_id(activity_id)

    async def get_by_name(self, name: str) -> Activity | None:

        return await self.repository.get_by_name(name)

    async def list_children(self, parent_id:  UUID | None) -> list[Activity]:

        return await self.repository.get_children_list(parent_id)

    async def delete(self, activity_id: UUID) -> None:

        await self.repository.delete(activity_id)

    async def get_subtree_ids(self, root_id: UUID) -> list[UUID]:

        return await self.repository.get_descendant(root_id)

    async def get_subtree_ids_by_name(self, name: str) -> list[UUID]:

        root = await self.repository.get_by_name(name)
        if not root:
            return []
        return await self.repository.get_descendant(root.id)