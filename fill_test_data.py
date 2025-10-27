import asyncio
import uuid
from sqlalchemy import insert, text, select, func
from infrastructure.db.database import async_session_maker
from infrastructure.db.models import (
    BuildingModel,
    OrganizationModel,
    OrganizationPhoneModel,
    ActivityModel,
    organization_activities,
)


async def fill_full_data():
    async with async_session_maker() as session:
        try:
            existing = await session.scalar(select(func.count(BuildingModel.id)))
            if existing and existing > 0:
                print("Тестовые данные уже существуют, пропускаем заполнение.")
                return
            # Здания
            buildings = [
                BuildingModel(id=uuid.uuid4(), address="г. Москва, ул. Ленина, 10", latitude=55.7558, longitude=37.6173),
                BuildingModel(id=uuid.uuid4(), address="г. Саратов, пр. Кирова, 42", latitude=51.5406, longitude=46.0086),
                BuildingModel(id=uuid.uuid4(), address="г. Санкт-Петербург, Невский пр., 12", latitude=59.9343, longitude=30.3351),
                BuildingModel(id=uuid.uuid4(), address="г. Казань, ул. Баумана, 5", latitude=55.7963, longitude=49.1088),
                BuildingModel(id=uuid.uuid4(), address="г. Новосибирск, Красный пр., 10", latitude=55.0084, longitude=82.9357),
            ]
            session.add_all(buildings)
            await session.flush()

            # Деятельность
            retail = ActivityModel(id=uuid.uuid4(), name="Розничная торговля", parent_id=None)
            construction = ActivityModel(id=uuid.uuid4(), name="Строительство", parent_id=None)
            fasteners = ActivityModel(id=uuid.uuid4(), name="Саморезы", parent_id=construction.id)
            food = ActivityModel(id=uuid.uuid4(), name="Общественное питание", parent_id=None)
            cafe = ActivityModel(id=uuid.uuid4(), name="Кафе", parent_id=food.id)
            it = ActivityModel(id=uuid.uuid4(), name="Разработка ПО", parent_id=None)
            session.add_all([retail, construction, fasteners, food, cafe, it])
            await session.flush()


            organizations = [
                OrganizationModel(id=uuid.uuid4(), name="ООО 'СтройМаркет'", building_id=buildings[0].id),
                OrganizationModel(id=uuid.uuid4(), name="ИП Иванов", building_id=buildings[1].id),
                OrganizationModel(id=uuid.uuid4(), name="ООО 'Пышки и Кофе'", building_id=buildings[2].id),
                OrganizationModel(id=uuid.uuid4(), name="ООО 'КазанСофт'", building_id=buildings[3].id),
                OrganizationModel(id=uuid.uuid4(), name="ООО 'СибирьСтрой'", building_id=buildings[4].id),
            ]
            session.add_all(organizations)
            await session.flush()


            phones = [
                OrganizationPhoneModel(id=uuid.uuid4(), organization_id=organizations[0].id, phone="+7 (495) 111-11-11"),
                OrganizationPhoneModel(id=uuid.uuid4(), organization_id=organizations[1].id, phone="+7 (8452) 222-22-22"),
                OrganizationPhoneModel(id=uuid.uuid4(), organization_id=organizations[2].id, phone="+7 (812) 555-55-55"),
                OrganizationPhoneModel(id=uuid.uuid4(), organization_id=organizations[3].id, phone="+7 (843) 444-44-44"),
                OrganizationPhoneModel(id=uuid.uuid4(), organization_id=organizations[4].id, phone="+7 (383) 333-33-33"),
            ]
            session.add_all(phones)

            # Привязка деятельности
            await session.execute(
                insert(organization_activities),
                [
                    {"organization_id": organizations[0].id, "activity_id": construction.id},
                    {"organization_id": organizations[1].id, "activity_id": retail.id},
                    {"organization_id": organizations[1].id, "activity_id": fasteners.id},
                    {"organization_id": organizations[2].id, "activity_id": cafe.id},
                    {"organization_id": organizations[3].id, "activity_id": it.id},
                    {"organization_id": organizations[4].id, "activity_id": it.id},
                ],
            )

            await session.commit()
            print("Полная база тестовых данных успешно создана!")

        except Exception as e:
            await session.rollback()
            print(f"Ошибка при заполнении БД: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(fill_full_data())


