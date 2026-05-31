import uuid

from pydantic import BaseModel, ConfigDict, Field


class BranchBase(BaseModel):
    name: str = Field(..., max_length=200)
    address: str | None = Field(default=None, max_length=500)
    timezone: str = Field(default="America/Mexico_City", max_length=50)


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    address: str | None = Field(default=None, max_length=500)
    timezone: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None


class BranchOut(BranchBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
