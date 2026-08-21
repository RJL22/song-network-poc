from app.models.song import Song
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

#from app.services.musicbrainz import SongSearchResult, search_recordings
from app.services.musicbrainz.schemas import SongSearchResult
from app.schemas.song import SongResponse
from app.services.musicbrainz.client import search_recordings

from app.database import get_db

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

@router.get("/search2", response_model=list[SongResponse])
async def search_songs2(
    title: str | None = None,
    artist: str | None = None,
    db: Session = Depends(get_db)
):
    """Search our database for candidate recordings. Does not touch Musicbrainz."""
    if not title and not artist:
        raise HTTPException(status_code=400, detail="Must provide at least a title or an artist")
    print(f"Searching for {title} by {artist}")
    query = (select(Song).where(Song.title.ilike(f"%{title}%")) if title else select(Song)).where(Song.artist.ilike(f"%{artist}%") if artist else True)
    results = db.scalars(query).all()
    return [SongResponse(id=song.id, mb_id=song.mb_id, title=song.title, artist=song.artist) for song in results]