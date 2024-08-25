from pydantic import BaseModel


class ObjectUrlCountSchema(BaseModel):
    launches: int
    missions: int
    rockets: int
