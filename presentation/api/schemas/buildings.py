from uuid import UUID

from pydantic import BaseModel, Field


class BuildingsResponse(BaseModel):
    """Модель ответа с данными здания."""

    id: UUID = Field(..., description='ID здания')
    address: str = Field(..., description='Адрес')
    latitude: float = Field(..., description='Широта')
    longitude: float = Field(..., description='Долгота')


class BuildingsCreate(BaseModel):
    """Модель ответа с данными здания."""

    address: str = Field(..., description='Адрес')
    latitude: float = Field(..., description='Широта')
    longitude: float = Field(..., description='Долгота')


class BuildingsListResponse(BaseModel):
    buildings: list[BuildingsResponse]


