from sqlalchemy import ARRAY, TEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, text


class LaunchModel(Base):
    __tablename__ = 'launches'

    launch_id: Mapped[text] = mapped_column(nullable=False, unique=True)


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
