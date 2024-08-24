from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, text


class MissionModel(Base):
    __tablename__ = 'missions'

    mission_id: Mapped[text] = mapped_column(nullable=False, unique=True)
    twitter: Mapped[text] = mapped_column(nullable=True)
    website: Mapped[text] = mapped_column(nullable=True)
    wikipedia: Mapped[text] = mapped_column(nullable=True)
