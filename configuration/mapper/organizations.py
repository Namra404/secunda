from configuration.entities.organizations import Organization
from configuration.mapper.activities import map_activity_to_entity
from infrastructure.db.models import OrganizationModel

def map_organization_to_entity(model: OrganizationModel | None) -> Organization | None:
    if model is None:
        return None
    return Organization(
        id=model.id,
        name=model.name,
        building_id=model.building_id,
        phones=[p.phone for p in model.phones],
        activities=[map_activity_to_entity(a) for a in model.activities],
    )