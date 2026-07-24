from pydantic import BaseModel
 
 
class SongSearchResult(BaseModel):
    """What our app returns for a MusicBrainz search"""
 
    musicbrainz_id: str
    title: str
    artist: str