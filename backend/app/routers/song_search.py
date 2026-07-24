from fastapi import APIRouter, HTTPException

#from app.services.musicbrainz import SongSearchResult, search_recordings
from app.services.musicbrainz.schemas import SongSearchResult
from app.services.musicbrainz.client import search_recordings

router = APIRouter(prefix="/songs", tags=["songs"])

@router.get("/search", response_model=list[SongSearchResult])
async def search_songs(
    title: str | None = None,
    artist: str | None = None,
):
    """Search MuscicBrainz for candidate recordings. Does not touch our database."""
    if not title and not artist:
        raise HTTPException(status_code=400, detail="Must provide at least a title or an artist")
    print(f"Searching for {title} by {artist}")
    return await search_recordings(title=title, artist=artist)