from domain.entities.activities import Activity
from infrastructure.db.models import ActivityModel

def map_activity_to_entity(model: ActivityModel) -> Activity:
    return Activity(
        id=model.id,
        name=model.name,
        parent_id=model.parent_id,
    )