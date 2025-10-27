from uuid import UUID

from sqlalchemy import select, literal, func, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession

from configuration.entities.activities import Activity
from configuration.exceptions import ParentActivityNotFoundError, ActivityDepthLimitError, ActivityNotFoundError, \
    ActivityHasChildrenError
from configuration.mapper.activities import map_activity_to_entity
from infrastructure.db.models import ActivityModel

class ActivitiesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, activity_id: UUID) -> Activity:
        """Получить вид деятельности по ID"""
        activity = await self.session.get(ActivityModel, activity_id)
        if activity is None:
            raise ActivityNotFoundError
        return map_activity_to_entity(activity)

    async def get_by_name(self,activity_name: str) -> Activity:
        """Получить вид деятельности по названию"""
        stmt = select(ActivityModel).where(ActivityModel.name == activity_name)
        activity = await self.session.scalar(stmt)
        if activity is None:
            raise ActivityNotFoundError
        return map_activity_to_entity(activity)

    async def get_children_list(self, parent_id: UUID | None) -> list[Activity]:
        """Получить список дочерних активностей по ID родителя"""
        stmt = select(ActivityModel).where(ActivityModel.parent_id == parent_id).order_by(ActivityModel.name.asc())
        res = await self.session.scalars(stmt)
        return [map_activity_to_entity(activity) for activity in res.all()]

    async def create(self, activity: Activity) -> Activity:
        """
        Создать новый вид деятельности
        Проверяет существование родителя и ограничение по глубине (до 3 уровней)
        """
        if activity.parent_id is not None:
            parent_exists = await self.session.scalar(
                select(exists().where(ActivityModel.id == activity.parent_id))
            )
            if not parent_exists:
                raise ParentActivityNotFoundError

        depth = await self._get_depth_from_node(activity.parent_id)
        if depth >= 3:
            raise ActivityDepthLimitError
        activity_model= ActivityModel(
            name= activity.name,
            parent_id=activity.parent_id
        )
        self.session.add(activity_model)
        # await self.session.flush()
        await self.session.commit()
        return map_activity_to_entity(activity_model)

    async def delete(self, activity_id: UUID) -> None:
        """
        Удалить вид деятельности
        Нельзя удалить, если у него есть дочерние элементы
        """
        await self.get_by_id(activity_id)
        children = await self.get_children_list(activity_id)
        if children:
            raise ActivityHasChildrenError
        stmt = delete(ActivityModel).where(ActivityModel.id == activity_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_descendant(self, root_id: UUID) -> list[UUID]:
        cte = self._create_descendants_cte(root_id)
        rows = await self.session.execute(select(cte.c.id))
        return [r[0] for r in rows.all()]


    @staticmethod
    def _create_ancestors_cte(child_id: UUID):
        base = select(
            ActivityModel.id,
            literal(1).label("depth"),
        ).where(ActivityModel.id == child_id)

        cte = base.cte(name="ancestors", recursive=True)

        up = (
            select(
                ActivityModel.parent_id.label("id"),
                (cte.c.depth + 1).label("depth"),
            )
            .join(ActivityModel, ActivityModel.id == cte.c.id)
            .where(ActivityModel.parent_id.is_not(None))
        )

        return cte.union_all(up)

    @staticmethod
    def _create_descendants_cte(parent_id: UUID):
        base_query = select(
            ActivityModel.id,
        ).where(ActivityModel.id == parent_id)

        cte = base_query.cte(name="descendants", recursive=True)

        recursive_query = select(
            ActivityModel.id,
        ).join(cte, ActivityModel.parent_id == cte.c.id)

        cte = cte.union_all(recursive_query)

        return cte

    async def _get_depth_from_node(self, parent_id: UUID | None) -> int:
        if parent_id is None:
            return 0
        cte = self._create_ancestors_cte(child_id=parent_id)
        res = await self.session.execute(select(func.max(cte.c.depth)))
        return res.scalar_one() or 0

