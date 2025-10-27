from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.database import get_db_session
from infrastructure.repositories.activities import ActivitiesRepository
from infrastructure.repositories.buildings import BuildingsRepository
from infrastructure.repositories.organizations import OrganizationsRepository
from infrastructure.services.activities import ActivitiesService
from infrastructure.services.buildings import BuildingService
from infrastructure.services.organizations import OrganizationsService


def get_building_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> BuildingService:
    """Получить сервис для работы со зданиями."""
    repository = BuildingsRepository(session)
    return BuildingService(repository=repository)


def get_activities_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> ActivitiesService:
    """Получить сервис для работы со зданиями."""
    repository = ActivitiesRepository(session)
    return ActivitiesService(repository=repository)

def get_organizations_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    activities_service: Annotated[ActivitiesService, Depends(get_activities_service)]
) -> OrganizationsService:
    """Получить сервис для работы с организациями."""
    organization_repository = OrganizationsRepository(session, activities_service.repository)
    return OrganizationsService(repository=organization_repository)