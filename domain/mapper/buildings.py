from domain.entities.buildings import Building
from infrastructure.db.models import BuildingModel

def map_building_to_entity(model: BuildingModel) -> Building:
    return Building(
        id=model.id,
        address=model.address,
        latitude=model.latitude,
        longitude=model.longitude,
    )