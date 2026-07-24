"""
Thin client around the MusicBrainz recording search API.

Owns: query building, the required User-Agent header, rate limiting,
and translating raw JSON into our own SongSearchResult. Nothing outside
this module should ever see MusicBrainz's response shape directly.
"""

import asyncio
import time

import httpx

from app.services.musicbrainz.schemas import SongSearchResult

MUSICBRAINZ_BASE_URL = "https://musicbrainz.org/ws/2/recording"

# Replace the contact with something real before this hits production use.
USER_AGENT = "MusicGraph/0.1 (ryan@example.com)"

MIN_SECONDS_BETWEEN_REQUESTS = 1.0  # MusicBrainz's unauthenticated limit


class MusicBrainzRateLimiter:
    """
    Serializes requests and enforces a minimum gap between them.

    One shared instance for the whole app — the 1 req/sec limit is
    per-IP, so every concurrent search from every user of this app
    draws from the same budget.
    """

    def __init__(self, min_interval: float = MIN_SECONDS_BETWEEN_REQUESTS):
        self._min_interval = min_interval
        self._lock = asyncio.Lock()
        self._last_request_time: float = 0.0

    async def wait_for_turn(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request_time
            if elapsed < self._min_interval:
                await asyncio.sleep(self._min_interval - elapsed)
            self._last_request_time = time.monotonic()


_rate_limiter = MusicBrainzRateLimiter()


def _build_query(title: str | None, artist: str | None) -> str:
    if not title and not artist:
        raise ValueError("Must provide at least a title or an artist")

    clauses = []
    if title:
        clauses.append(f'recording:"{title}"')
    if artist:
        clauses.append(f'artist:"{artist}"')

    return " AND ".join(clauses)


async def search_recordings(
    title: str | None = None,
    artist: str | None = None,
    limit: int = 10,
) -> list[SongSearchResult]:
    """Search MusicBrainz recordings by title and/or artist."""
    query = _build_query(title, artist)

    await _rate_limiter.wait_for_turn()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            MUSICBRAINZ_BASE_URL,
            params={"query": query, "fmt": "json", "limit": limit},
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()

    return _parse_response(response.json())


def _parse_response(data: dict) -> list[SongSearchResult]:
    results = []
    for recording in data.get("recordings", []):
        artist_credit = recording.get("artist-credit", [])
        artist_name = "".join(
            part.get("name", "") + part.get("joinphrase", "")
            for part in artist_credit
        ) or "Unknown Artist"

        results.append(
            SongSearchResult(
                musicbrainz_id=recording["id"],
                title=recording.get("title", "Unknown Title"),
                artist=artist_name,
            )
        )
    return results