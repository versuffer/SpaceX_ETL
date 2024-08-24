from datetime import datetime
from typing import Annotated
from uuid import UUID

from sqlalchemy import TEXT, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

text = Annotated[str, mapped_column(TEXT)]


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
    }
    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.current_timestamp())
