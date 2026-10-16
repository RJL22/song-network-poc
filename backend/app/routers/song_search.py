from app.models.song import Song
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

#from app.services.musicbrainz import SongSearchResult, search_recordings
from app.schemas.song import SongResponse
from app.services.musicbrainz.client import search_recordings

from app.database import get_db

router = APIRouter(prefix="/songs", tags=["songs"])

@router.get("/search", response_model=list[SongResponse])
async def search_songs(
    title: str | None = None,
    artist: str | None = None,
    db: Session = Depends(get_db),
):
    """Search the local catalog, then cache MusicBrainz results on a miss."""
    if not title and not artist:
        raise HTTPException(status_code=400, detail="Must provide at least a title or an artist")
    filters = []
    if title:
        filters.append(Song.title.ilike(f"%{title}%"))
    if artist:
        filters.append(Song.artist.ilike(f"%{artist}%"))
    local = db.scalars(select(Song).where(*filters).order_by(Song.title, Song.artist).limit(25)).all()
    if local:
        return local

    try:
        external = await search_recordings(title=title, artist=artist, limit=10)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Song search provider is unavailable") from exc

    songs = []
    for result in external:
        song = db.scalar(select(Song).where(Song.mb_id == result.musicbrainz_id))
        if song is None:
            song = Song(mb_id=result.musicbrainz_id, title=result.title, artist=result.artist)
            db.add(song)
            songs.append(song)
        else:
            songs.append(song)
    db.commit()
    for song in songs:
        db.refresh(song)
    return songs
