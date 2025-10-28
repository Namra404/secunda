from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from domain.entities.activities import Activity
from configuration.exceptions import ParentActivityNotFoundError, ActivityDepthLimitError, ActivityNotFoundError, ActivityHasChildrenError
from infrastructure.services.activities import ActivitiesService
from presentation.api.dependencies import get_activities_service
from presentation.api.schemas.activities import ActivityResponse, ActivityCreate, ActivitiesListResponse, ActivitySubtreeIdsResponse

router = APIRouter(prefix='/activities', tags=['activities'])

@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    data: ActivityCreate,
    service: ActivitiesService = Depends(get_activities_service),
):
    """Создать новую деятельность (уровень вложенности деятельностей не больше 3)"""
    activity_entity = Activity(
        id = None,
        name=data.name,
        parent_id=data.parent_id,
    )
    try:
        created = await service.create(activity_entity)
    except ParentActivityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Родитель с ID {data.parent_id} не найден')
    except ActivityDepthLimitError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cant create activity with deep >= 3")
    return _to_activity_response(created)

@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity_by_id(
    activity_id: UUID,
    service: ActivitiesService = Depends(get_activities_service),
):
    """Получить деятельность по ID"""
    try:
        activity = await service.get_by_id(activity_id)
    except ActivityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Активность с ID {activity_id} не найдена")
    return _to_activity_response(activity)

@router.get("/", response_model=ActivitiesListResponse)
async def list_children(
    parent_id: UUID,
    service: ActivitiesService = Depends(get_activities_service),
):
    """Получить список деятельность"""
    items = await service.list_children(parent_id)
    return ActivitiesListResponse(activities=[_to_activity_response(a) for a in items])


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: UUID,
    service: ActivitiesService = Depends(get_activities_service),
):
    """Удалить деятельность (ошибка, если есть дети)"""

    try:
        await service.delete(activity_id)
    except ActivityHasChildrenError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Нельзя удалить активность с ID {activity_id}, так как у неё есть дочерние элементы")
    except ActivityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Активность ID {activity_id} не найдена")


@router.get("/{activity_id}/subtree", response_model=ActivitySubtreeIdsResponse)
async def get_subtree_ids_by_id(
    activity_id: UUID,
    service: ActivitiesService = Depends(get_activities_service),
):
    """ID всех деятельностей поддерева"""
    ids = await service.get_subtree_ids(activity_id)
    return ActivitySubtreeIdsResponse(ids=ids)


@router.get("/subtree/by-name", response_model=ActivitySubtreeIdsResponse)
async def get_subtree_ids_by_name(
    name: str,
    service: ActivitiesService = Depends(get_activities_service),
):
    """ID всех деятельностей поддерева"""
    ids = await service.get_subtree_ids_by_name(name)
    return ActivitySubtreeIdsResponse(ids=ids)

def _to_activity_response(activity: Activity) -> ActivityResponse:
    return ActivityResponse(
        id=activity.id,
        name=activity.name,
        parent_id=activity.parent_id,
    )