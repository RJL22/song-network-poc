from pydantic import BaseModel, ConfigDict

class SongCreate(BaseModel):
    mb_id: str
    title: str
    artist: str

class SongResponse(BaseModel):
    id: int
    mb_id: str
    title: str
    artist: str

    model_config = ConfigDict(from_attributes=True)

class SongUpdate(BaseModel):
    title: str
    artist: str