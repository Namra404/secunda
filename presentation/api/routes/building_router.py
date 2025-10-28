from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from domain.entities.buildings import Building
from configuration.exceptions import DuplicateBuildingAddressError, BuildingCreateError, BuildingNotFoundError
from infrastructure.services.buildings import BuildingService
from presentation.api.dependencies import get_building_service
from presentation.api.schemas.buildings import BuildingsResponse, BuildingsCreate, BuildingsListResponse

router = APIRouter(prefix='/buildings', tags=['buildings'])

@router.post('/', response_model=BuildingsResponse, status_code=status.HTTP_201_CREATED)
async def create_building(building_data: BuildingsCreate, building_service: BuildingService = Depends(get_building_service)):
    """Создать новое здание"""
    building_entity = Building(
        id=None,
        address=building_data.address,
        latitude=building_data.latitude,
        longitude=building_data.longitude,
    )
    try:
        building = await building_service.create_building(building=building_entity)
    except DuplicateBuildingAddressError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Здание с адресом '{building_data.address}' уже существует")
    except BuildingCreateError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ошибка при создании здания")
    return _building_entity_to_response(building=building)

@router.get('/{user_id}', response_model=BuildingsResponse)
async def get_building(building_id: UUID, building_service: BuildingService = Depends(get_building_service)):
    """Получить пользователя по ID"""
    try:
        building = await building_service.get_building_by_id(building_id=building_id)
    except BuildingNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Здание с ID {building_id} не найдено")
    return _building_entity_to_response(building)


@router.get('/', response_model=BuildingsListResponse)
async def list_all_buildings(building_service: BuildingService = Depends(get_building_service)):
    """Получить список всех зданий"""
    buildings = await building_service.list_all_buildings()
    return BuildingsListResponse(
        buildings=[_building_entity_to_response(building) for building in buildings]
    )

@router.get("/geo/square", response_model=BuildingsListResponse)
async def get_buildings_in_square(
    lat_min: float,
    lon_min: float,
    lat_max: float,
    lon_max: float,
    building_service: BuildingService = Depends(get_building_service),
):
    """Получить здания, находящиеся в пределах прямоугольной области"""
    buildings = await building_service.list_buildings_in_square(lat_min, lon_min, lat_max, lon_max)
    return BuildingsListResponse(
        buildings=[_building_entity_to_response(b) for b in buildings]
    )

def _building_entity_to_response(building: Building) -> BuildingsResponse:
    """Преобразовать доменную сущность в модель ответа"""
    return BuildingsResponse(
        id=building.id,
        address=building.address,
        latitude=building.longitude,
        longitude=building.latitude,
    )