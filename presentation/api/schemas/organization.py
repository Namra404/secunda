from uuid import UUID

from pydantic import BaseModel, Field

from presentation.api.schemas.activities import ActivityResponse


class OrganizationCreate(BaseModel):
    """Запрос на создание организации."""
    name: str = Field(..., description="Название организации")
    building_id: UUID = Field(..., description="ID здания")
    phones: list[str] = Field(default_factory=list, description="Список телефонов")
    activity_ids: list[UUID] = Field(default_factory=list, description="ID видов деятельности")


class OrganizationResponse(BaseModel):
    """Ответ с данными организации (неплоский, с активностями)."""
    id: UUID
    name: str
    building_id: UUID
    phones: list[str]
    activities: list[ActivityResponse]


class OrganizationsListResponse(BaseModel):
    organizations: list[OrganizationResponse]