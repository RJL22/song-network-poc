from pydantic import BaseModel, ConfigDict

class SongCreate(BaseModel):
    title: str
    artist: str

class SongResponse(BaseModel):
    id: int
    title: str
    artist: str

    model_config = ConfigDict(from_attributes=True)

class SongUpdate(BaseModel):
    title: str
    artist: str