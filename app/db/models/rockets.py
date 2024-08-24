from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, text


class RocketModel(Base):
    __tablename__ = 'rockets'

    rocket_id: Mapped[text] = mapped_column(nullable=False, unique=True)
    wikipedia: Mapped[text] = mapped_column(nullable=True)
