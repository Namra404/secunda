from uuid import UUID

from pydantic import BaseModel, Field


class ActivityResponse(BaseModel):
    """Модель ответа с данными вида деятельности."""
    id: UUID = Field(..., description="ID активности")
    name: str = Field(..., description="Название")
    parent_id: UUID | None = Field(None, description="ID родителя (если есть)")


class ActivityCreate(BaseModel):
    """Модель запроса на создание вида деятельности."""
    name: str = Field(..., description="Название")
    parent_id: UUID | None = Field(None, description="ID родителя (опционально)")


class ActivitiesListResponse(BaseModel):
    """Список активностей (например, дети заданного parent_id)."""
    activities: list[ActivityResponse]


class ActivitySubtreeIdsResponse(BaseModel):
    """ID всех активностей поддерева (включая корень)."""
    ids: list[UUID]