from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ConnectionCreate(BaseModel):
    song_1_id: int
    song_2_id: int

class ConnectionResponse(BaseModel):
    id: int
    song_1_id: int
    song_2_id: int
    supporter_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class SupporterResponse(BaseModel):
    user_id: int
    username: str
    rank: int
    points: float


class ConnectionHistoryResponse(BaseModel):
    connection_id: int
    song_1_id: int
    song_2_id: int
    created_at: datetime
    points: float
    supporter_count: int
