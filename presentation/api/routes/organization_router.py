from uuid import UUID

from fastapi import HTTPException, Depends, APIRouter
from starlette import status

from domain.entities.activities import Activity
from domain.entities.organizations import Organization
from configuration.exceptions import OrganizationCreateError, ActivityNotFoundError
from infrastructure.services.organizations import OrganizationsService
from presentation.api.dependencies import get_organizations_service
from presentation.api.routes.activity_router import _to_activity_response
from presentation.api.schemas.organization import OrganizationResponse, OrganizationCreate, OrganizationsListResponse


router = APIRouter(prefix='/organization', tags=['organization'])

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: OrganizationCreate,
    service: OrganizationsService = Depends(get_organizations_service)
):
    """Создать новую организацию"""
    org_entity = Organization(
        id=None,
        name=data.name,
        building_id=data.building_id,
        phones=list(data.phones or []),
        activities=[Activity(id=aid, name="", parent_id=None) for aid in (data.activity_ids or [])],
    )
    try:
        created = await service.create(org_entity)
    except OrganizationCreateError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ошибка при создании организации")
    return _to_organization_response(created)

@router.get("/", response_model=OrganizationsListResponse)
async def list_all_organizations(service: OrganizationsService = Depends(get_organizations_service)):
    """Получить список всех организаций"""
    items = await service.list_all()
    return OrganizationsListResponse(organizations=[_to_organization_response(o) for o in items])


@router.get("/building/{building_id}", response_model=OrganizationsListResponse)
async def list_by_building_by_id(building_id: UUID, service: OrganizationsService = Depends(get_organizations_service)):
    """Получить организации, находящиеся в конкретном здании"""
    items = await service.list_by_building(building_id)
    return OrganizationsListResponse(organizations=[_to_organization_response(o) for o in items])


@router.get("/by-activity/{activity_id}", response_model=OrganizationsListResponse)
async def list_by_activity_id(activity_id: UUID, service: OrganizationsService = Depends(get_organizations_service)):
    """Получить организации по ID вида деятельности"""
    items = await service.list_by_activity_id(activity_id)
    return OrganizationsListResponse(organizations=[_to_organization_response(o) for o in items])


@router.get("/by-activity-name", response_model=OrganizationsListResponse)
async def list_by_activity_name(name: str, service: OrganizationsService = Depends(get_organizations_service)):
    """Получить организации по названию вида деятельности"""
    try:
        items = await service.list_by_activity_name(name)
    except ActivityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Деятельность '{name}' не найдена")
    return OrganizationsListResponse(organizations=[_to_organization_response(o) for o in items])


@router.get("/search/name", response_model=OrganizationsListResponse)
async def find_by__name(name: str, service: OrganizationsService = Depends(get_organizations_service)):
    """Найти организации по точному совпадению имени"""
    items = await service.find_by_name(name)
    return OrganizationsListResponse(organizations=[_to_organization_response(o) for o in items])

@router.get("/geo/square", response_model=OrganizationsListResponse)
async def get_organizations_in_square(
    lat_min: float,
    lon_min: float,
    lat_max: float,
    lon_max: float,
    service: OrganizationsService = Depends(get_organizations_service),
):
    """Найти организации в пределах прямоугольной области"""
    items = await service.list_by_square(lat_min, lon_min, lat_max, lon_max)
    return OrganizationsListResponse(organizations=[_to_organization_response(o) for o in items])

@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization_by_id(organization_id: UUID, service: OrganizationsService = Depends(get_organizations_service)):
    """Получить организацию по её ID"""
    org = await service.get_by_id(organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Организация с ID {organization_id} не найдена")
    return _to_organization_response(org)

def _to_organization_response(org: Organization) -> OrganizationResponse:
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        building_id=org.building_id,
        phones=list(org.phones or []),
        activities=[_to_activity_response(a) for a in (org.activities or [])],
    )
