from pydantic import BaseModel, ConfigDict

class ConnectionCreate(BaseModel):
    song_1_id: int
    song_2_id: int

class ConnectionResponse(BaseModel):
    id: int
    song_1_id: int
    song_2_id: int

class ConnectionResponse(BaseModel):
    id: int
    song_1_id: int
    song_2_id: int

    model_config = ConfigDict(from_attributes=True)