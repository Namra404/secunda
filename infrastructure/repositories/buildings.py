from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.buildings import Building
from configuration.exceptions import DuplicateBuildingAddressError, BuildingCreateError, BuildingNotFoundError
from domain.mapper.buildings import map_building_to_entity
from infrastructure.db.models import BuildingModel



class BuildingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, building: Building):
        """
        Создать новое здание
        Проверяет уникальность адреса и добавляет запись в БД
        """
        exists_stmt = select(BuildingModel).where(BuildingModel.address == building.address)
        exists = await self.session.scalar(exists_stmt)
        if exists:
            raise DuplicateBuildingAddressError

        building_model = BuildingModel(
            address=building.address,
            latitude=building.latitude,
            longitude=building.longitude
        )
        try:
            self.session.add(building_model)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise BuildingCreateError(str(e))

        return map_building_to_entity(building_model)

    async def get_by_id(self, building_id: UUID) -> Building:
        """Получить здание по ID"""
        building = await self.session.get(BuildingModel, building_id)
        if not building:
            raise BuildingNotFoundError
        return map_building_to_entity(building)

    async def list_all(self) -> list[Building]:
        """Получить список всех зданий"""
        stmt = select(BuildingModel).order_by(BuildingModel.id)
        buildings = await self.session.execute(stmt)
        result = buildings.scalars().all()
        return [map_building_to_entity(model) for model in result]

    async def list_by_square( self, lat_min: float, lon_min: float, lat_max: float, lon_max: float):
        """Получить здания, которые находятся в прямоугольной области"""
        stmt = (
            select(BuildingModel)
            .where(BuildingModel.latitude.between(lat_min, lat_max))
            .where(BuildingModel.longitude.between(lon_min, lon_max))
        )
        res = await self.session.scalars(stmt)
        return [map_building_to_entity(m) for m in res.all()]

