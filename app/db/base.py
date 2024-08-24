import functools

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.settings.config import app_settings

async_engine = create_async_engine(url=app_settings.POSTGRES_DSN, echo=False)  # type: ignore [arg-type]


def manage_async_session(func):
    @functools.wraps(func)
    async def inner(*args, **kwargs):
        if (session := kwargs.get('session')) and isinstance(session, AsyncSession):
            return await func(*args, **kwargs)

        async with AsyncSession(bind=async_engine, expire_on_commit=False) as session:
            kwargs['session'] = session
            result = await func(*args, **kwargs)
            await session.commit()
            return result

    return inner
