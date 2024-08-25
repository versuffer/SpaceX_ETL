from pydantic import BaseModel, ConfigDict, Field


class LaunchLinksSchema(BaseModel):
    article_link: str | None
    flickr_images: list[str]
    presskit: str | None
    reddit_campaign: str | None
    reddit_launch: str | None
    reddit_media: str | None
    reddit_recovery: str | None
    video_link: str | None
    wikipedia: str | None

    model_config = ConfigDict(from_attributes=True)


class LaunchSchema(BaseModel):
    launch_id: str = Field(validation_alias='id')
    launch_links: LaunchLinksSchema = Field(validation_alias='links')

    model_config = ConfigDict(from_attributes=True)
