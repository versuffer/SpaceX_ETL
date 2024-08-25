from fastapi import APIRouter, Depends, status

from app.services.repositories.postgres import DataMartRepository

data_mart_router = APIRouter(prefix='/data_mart')


@data_mart_router.get(
    '/object_url_count',
    status_code=status.HTTP_200_OK,
    summary='Получение количества URL для объектов типа launch, mission и rocket',
    tags=['Витрина данных'],
)
async def get_object_url(data_mart: DataMartRepository = Depends()):
    return await data_mart.get_object_url_count()
