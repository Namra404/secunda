from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from configuration.entities.organizations import Organization
from configuration.exceptions import OrganizationNotFoundError, OrganizationCreateError, ActivityNotFoundError
from configuration.mapper.organizations import map_organization_to_entity
from infrastructure.db.models import OrganizationModel, OrganizationPhoneModel, ActivityModel, BuildingModel
from infrastructure.repositories.activities import ActivitiesRepository


class OrganizationsRepository:
    def __init__(self, session: AsyncSession, activity_repo: ActivitiesRepository):
        self.session = session
        self.activity_repo = activity_repo

    async def get_by_id(self, organization_id: UUID) -> Organization:
        """
        Получить организацию по её ID
        Подгружает телефоны, виды деятельности и здание
        """
        stmt = (
            select(OrganizationModel)
            .options(
                selectinload(OrganizationModel.phones),
                selectinload(OrganizationModel.activities),
                selectinload(OrganizationModel.building),
            )
        ).where(OrganizationModel.id == organization_id)

        organ = await self.session.scalar(stmt)

        if not organ:
            raise OrganizationNotFoundError

        return map_organization_to_entity(organ)



    async def create(self, organization: Organization):
        """Создать новую организацию с привязкой к зданию, телефонами и видами деятельности"""
        try:
            organization_model = OrganizationModel(
                name=organization.name,
                building_id=organization.building_id,
                activities=[],
                phones=[],
            )
            self.session.add(organization_model)
            await self.session.flush()


            for phone in organization.phones or []:
                org_phone = phone.strip()
                if org_phone:
                    self.session.add(
                        OrganizationPhoneModel(
                            organization_id=organization_model.id,
                            phone=org_phone
                        )
                    )

            if organization.activities:
                activity_ids = [activity.id for activity in organization.activities if activity.id]
                if activity_ids:
                    res = await self.session.execute(
                        select(ActivityModel).where(ActivityModel.id.in_(activity_ids))
                    )
                    loaded_activities = list(res.scalars().all())
                    organization_model.activities.extend(loaded_activities)

            await self.session.commit()
            await self.session.refresh(organization_model)
        except Exception:
            await self.session.rollback()
            raise OrganizationCreateError
        return map_organization_to_entity(organization_model)

    async def list_all(self):
        """
        Получить список всех организаций
        Подгружает телефоны, виды деятельности и здания
        """
        stmt = select(OrganizationModel).options(
            selectinload(OrganizationModel.phones),
            selectinload(OrganizationModel.activities),
            selectinload(OrganizationModel.building),
        )
        res = await self.session.scalars(stmt)
        return [map_organization_to_entity(model) for model in res.all()]

    async def list_by_activity_id(self, activity_id: UUID) -> list[Organization]:
        """
        Получить организации по ID вида деятельности
        Учитываются все дочерние виды
        """
        activity_ids = await self.activity_repo.get_descendant(activity_id)
        activity_ids.append(activity_id)

        stmt = (
            select(OrganizationModel)
            .where(OrganizationModel.activities.any(ActivityModel.id.in_(activity_ids)))
            .options(
                selectinload(OrganizationModel.phones),
                selectinload(OrganizationModel.activities),
            )
            .order_by(OrganizationModel.name.asc())
        )
        res = await self.session.scalars(stmt)
        return [map_organization_to_entity(model) for model in res.all()]

    async def list_by_activity_name(self, activity_name: str) -> list[Organization]:
        """Получить организации по названию вида деятельности"""
        try:
            activity = await self.activity_repo.get_by_name(activity_name)
        except Exception:
            raise ActivityNotFoundError
        return await self.list_by_activity_id(activity.id)

    async def list_by_building_id(self, building_id: UUID):
        """Получить все организации, находящиеся в конкретном здании"""
        stmt = (
            select(OrganizationModel)
            .options(
                selectinload(OrganizationModel.phones),
                selectinload(OrganizationModel.activities),
                selectinload(OrganizationModel.building),
            ).where(OrganizationModel.building_id == building_id)
        )
        res = await self.session.scalars(stmt)
        return [map_organization_to_entity(model) for model in res.all()]

    async def find_organization_by_name(self, name: str) -> list[Organization]:
        """Найти организации по точному совпадению имени"""
        stmt = (
            select(OrganizationModel)
            .options(
                selectinload(OrganizationModel.phones),
                selectinload(OrganizationModel.activities),
            )
            .where(OrganizationModel.name == name)
        )
        res = await self.session.scalars(stmt)
        return [map_organization_to_entity(m) for m in res.all()]


    async def list_by_square( self, lat_min: float, lon_min: float, lat_max: float, lon_max: float ):
        """Возвращает организации, которые находятся в прямоугольной области"""
        stmt = (
            select(OrganizationModel)
            .join(BuildingModel)
            .where(BuildingModel.latitude.between(lat_min, lat_max))
            .where(BuildingModel.longitude.between(lon_min, lon_max))
            .options(
                selectinload(OrganizationModel.phones),
                selectinload(OrganizationModel.activities),
                selectinload(OrganizationModel.building),
            )
        )

        res = await self.session.scalars(stmt)
        return [map_organization_to_entity(model) for model in res.all()]

