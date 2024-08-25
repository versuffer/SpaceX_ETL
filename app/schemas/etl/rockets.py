from pydantic import BaseModel, ConfigDict, Field


class RocketSchema(BaseModel):
    rocket_id: str = Field(validation_alias='id')
    wikipedia: str | None

    model_config = ConfigDict(from_attributes=True)
