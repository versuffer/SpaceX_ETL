from typing import Generic, Sequence, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import and_, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import _AbstractLoad

from app.db.base import manage_async_session
from app.db.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class PostgresRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    one_object_options: list[_AbstractLoad] = []
    multi_objects_options: list[_AbstractLoad] = []

    def __init__(self, model: Type[ModelType]):
        self._model = model

    @manage_async_session
    async def get(
        self, session: AsyncSession, id_: UUID, *, extra_options: list[_AbstractLoad] | None = None
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
        session: AsyncSession,
        *args_filters,
        extra_options: list[_AbstractLoad] | None = None,
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
        session: AsyncSession,
        *args_filters,
        skip: int | None = None,
        limit: int | None = None,
        extra_options: list[_AbstractLoad] | None = None,
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
        session: AsyncSession,
        obj_in: CreateSchemaType,
        **extra_values,
    ) -> ModelType:
        result = await session.execute(
            insert(self._model)
            .values(**obj_in.model_dump(exclude_unset=True), **extra_values)
            .returning(self._model)
            .options(*self.one_object_options)
        )
        return result.scalar_one()

    @manage_async_session
    async def update(
        self,
        session: AsyncSession,
        id_: UUID,
        obj_in: UpdateSchemaType | dict,
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
