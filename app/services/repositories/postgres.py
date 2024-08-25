from typing import Generic, Sequence, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel, TypeAdapter
from sqlalchemy import and_, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import _AbstractLoad

from app.db.base import manage_async_session
from app.db.models.base import Base
from app.db.models.launches import LaunchLinksModel, LaunchModel
from app.db.models.missions import MissionModel
from app.db.models.rockets import RocketModel
from app.schemas.api.v1.data_mart import ObjectUrlCountSchema
from app.schemas.etl.launches import LaunchLinksSchema, LaunchSchema
from app.schemas.etl.missions import MissionSchema
from app.schemas.etl.rockets import RocketSchema

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    one_object_options: list[_AbstractLoad] = []
    multi_objects_options: list[_AbstractLoad] = []

    def __init__(self, model: Type[ModelType]):
        self._model = model

    @manage_async_session
    async def get(
        self,
        id_: UUID,
        *,
        extra_options: list[_AbstractLoad] | None = None,
        session: AsyncSession,
    ) -> ModelType | None:
        extra_options = extra_options or []
        statement = (
            select(self._model).where(self._model.id == str(id_)).options(*self.one_object_options, *extra_options)
        )
        results = await session.execute(statement=statement)
        return results.scalar_one_or_none()

    @manage_async_session
    async def get_one(
        self,
        *args_filters,
        extra_options: list[_AbstractLoad] | None = None,
        session: AsyncSession,
        **kwargs_filters,
    ) -> ModelType | None:
        extra_options = extra_options or []
        filters = list(args_filters)
        filters.extend([getattr(self._model, key) == value for key, value in kwargs_filters.items()])

        statement = select(self._model).where(and_(*filters)).options(*self.one_object_options, *extra_options)

        results = await session.execute(statement=statement)
        return results.scalar_one_or_none()

    @manage_async_session
    async def get_multi(
        self,
        *args_filters,
        skip: int | None = None,
        limit: int | None = None,
        extra_options: list[_AbstractLoad] | None = None,
        session: AsyncSession,
        **kwargs_filters,
    ) -> Sequence[ModelType]:
        filters = list(args_filters)
        filters.extend([getattr(self._model, key) == value for key, value in kwargs_filters.items()])

        statement = (
            select(self._model).where(and_(*filters)).offset(skip).limit(limit).options(*self.multi_objects_options)
        )
        if extra_options:
            statement = statement.options(*extra_options)

        results = await session.execute(statement=statement)
        return results.scalars().all()

    @manage_async_session
    async def create(
        self,
        obj_in: CreateSchemaType,
        *,
        session: AsyncSession,
        **extra_values,
    ) -> ModelType:
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        data |= extra_values

        result = await session.execute(
            insert(self._model).values(**data).returning(self._model).options(*self.one_object_options)
        )
        return result.scalar_one()

    @manage_async_session
    async def update(
        self,
        id_: UUID,
        obj_in: UpdateSchemaType | dict,
        *,
        session: AsyncSession,
        **extra_values,
    ) -> ModelType | None:
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        data |= extra_values

        result = (
            await session.execute(
                update(self._model)
                .where(self._model.id == id_)
                .values(**data)
                .returning(self._model)
                .options(*self.one_object_options)
            )
        ).scalar_one_or_none()

        await session.refresh(result)
        return result


class DataMartRepository:
    @manage_async_session
    async def get_object_url_count(self, *, session: AsyncSession) -> ObjectUrlCountSchema:
        data = await session.execute(text('SELECT object, url_count FROM object_url_count'))
        return TypeAdapter(ObjectUrlCountSchema).validate_python({obj_type: count for obj_type, count in data})


launches_repository: BaseRepository[LaunchModel, LaunchSchema, LaunchSchema] = BaseRepository(LaunchModel)
launch_links_repository: BaseRepository[LaunchLinksModel, LaunchLinksSchema, LaunchLinksSchema] = BaseRepository(
    LaunchLinksModel
)
missions_repository: BaseRepository[MissionModel, MissionSchema, MissionSchema] = BaseRepository(MissionModel)
rockets_repository: BaseRepository[RocketModel, RocketSchema, RocketSchema] = BaseRepository(RocketModel)
