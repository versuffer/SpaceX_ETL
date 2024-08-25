from uuid import UUID

from sqlalchemy import ARRAY, TEXT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, text


class LaunchModel(Base):
    __tablename__ = 'launches'

    launch_id: Mapped[text] = mapped_column(nullable=False, unique=True)

    # one-to-one
    launch_link: Mapped['LaunchLinkModel'] = relationship(back_populates='launch', uselist=False)


class LaunchLinkModel(Base):
    __tablename__ = 'launch_links'

    mission_id: Mapped[text] = mapped_column(nullable=False, unique=True)
    article_link: Mapped[text] = mapped_column(nullable=True)
    flickr_images: Mapped[list[str]] = mapped_column(ARRAY(TEXT), default=[])
    presskit: Mapped[text] = mapped_column(nullable=True)
    reddit_campaign: Mapped[text] = mapped_column(nullable=True)
    reddit_launch: Mapped[text] = mapped_column(nullable=True)
    reddit_media: Mapped[text] = mapped_column(nullable=True)
    reddit_recovery: Mapped[text] = mapped_column(nullable=True)
    video_link: Mapped[text] = mapped_column(nullable=True)
    wikipedia: Mapped[text] = mapped_column(nullable=True)

    # one-to-one
    launch_uuid: Mapped[UUID] = mapped_column(
        ForeignKey('launches.id', ondelete='CASCADE'), nullable=False, unique=True
    )
    launch: Mapped[LaunchModel] = relationship(back_populates='launch_links')
