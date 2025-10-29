import re
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from presentation.api.schemas.activities import ActivityResponse

PHONE_REGEX = re.compile(
    r"""
    ^\s*                   
    (?:\+?7|8)                 # код страны (+7, 7 или 8)
    [\s\-()]*                  # возможные пробелы и скобки
    (?:\d[\s\-()]*){10}        # ровно 10 цифр после кода страны
    \s*$                       
    """,
    re.VERBOSE
)


class OrganizationCreate(BaseModel):
    """Запрос на создание организации."""
    name: str = Field(..., description="Название организации")
    building_id: UUID = Field(..., description="ID здания")
    phones: list[str] = Field(default_factory=list, description="Список телефонов")
    activity_ids: list[UUID] = Field(default_factory=list, description="ID видов деятельности")

    @field_validator('phones', mode='before')
    def validate_phones(cls, phones: list[str]) -> list[str]:
        if not isinstance(phones, list):
            raise ValueError("Поле phones должно быть списком строк")

        validated = []
        for phone in phones:
            phone = phone.strip()
            if not PHONE_REGEX.match(phone):
                raise ValueError(
                    f"Некорректный формат номера: {phone}. Допустимые форматы: +79991234567, 8 (999) 123-45-67, +7 999 123 4567"
                )
            validated.append(phone)
        return validated


class OrganizationResponse(BaseModel):
    """Ответ с данными организации (неплоский, с активностями)."""
    id: UUID
    name: str
    building_id: UUID
    phones: list[str]
    activities: list[ActivityResponse]


class OrganizationsListResponse(BaseModel):
    organizations: list[OrganizationResponse]