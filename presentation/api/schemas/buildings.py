from uuid import UUID

from pydantic import BaseModel, Field


class BuildingsResponse(BaseModel):
    """Модель ответа с данными здания."""

    id: UUID = Field(..., description='ID здания')
    address: str = Field(..., description='Адрес')
    latitude: float = Field(..., description='Широта')
    longitude: float = Field(..., description='Долгота')


class BuildingsCreate(BaseModel):
    """Модель запроса на создание здания."""

    address: str = Field(..., description='Адрес')
    latitude: float = Field(..., ge=-90, le=90,description='Широта (от -90 до 90)')
    longitude: float = Field(..., ge=-180, le=180, description='Долгота (от -180 до 180)')


class BuildingsListResponse(BaseModel):
    buildings: list[BuildingsResponse]


