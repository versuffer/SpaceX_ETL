from pydantic import BaseModel, ConfigDict, Field


class MissionSchema(BaseModel):
    mission_id: str = Field(validation_alias='id')
    twitter: str | None
    website: str | None
    wikipedia: str | None

    model_config = ConfigDict(from_attributes=True)
