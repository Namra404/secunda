from dataclasses import dataclass


class ActivityNotFoundError(Exception):
    """Деятельность не найдена"""


class ParentActivityNotFoundError(Exception):
    """Деятельность не найдена"""


class ActivityDepthLimitError(Exception):
    """Превышена допустимая глубина иерархии (максимум 3 уровня)"""


class ActivityHasChildrenError(Exception):
    """Нельзя удалить деятельность, у которой есть дочерние элементы"""


class OrganizationNotFoundError(Exception):
    """Организация не найдена"""


@dataclass
class OrganizationCreateError(Exception):
    """Ошибка при создании организации"""
    msg: str


class BuildingNotFoundError(Exception):
    """Здание не найдено"""


@dataclass
class BuildingCreateError(Exception):
    """Ошибка при создании здания"""
    msg: str


class DuplicateBuildingAddressError(Exception):
    """Здание с таким адресом уже существует"""
