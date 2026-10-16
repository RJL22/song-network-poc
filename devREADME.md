# Music Similarity Graph (song-network-poc)

Portfolio project to learn backend engineering. Not a production-scale
catalog — the goal is depth on architecture/design decisions, not feature
count.

## Core Idea

Users form "Song A is similar to Song B" connections. Multiple users can
independently form the *same* connection — that convergence is the point of
the app, not a private list. There's no voting/unvoting; the unit of action
is *making* a connection. Re-forming a connection you already made is a
no-op (idempotent per user); a different user forming the same connection
reuses the existing `Connection` row and adds a new attribution row.

A reward system gives points to early supporters of connections that later
become popular: `points = ln(N / n)`, where `N` = total supporters of a
connection and `n` = the supporter's rank (how early they formed it).
Recomputed only for the earliest 20 supporters per connection (bounded
window) to avoid O(k²) cost on popular connections — a deliberate fix after
an earlier version recomputed all supporters on every new join.

## Tech Stack

- **Backend:** FastAPI, PostgreSQL, SQLAlchemy 2.x (`Mapped`/`mapped_column`
  style), psycopg, Docker (Postgres only, not backend/frontend), Alembic
- **Auth:** JWT (passlib/bcrypt for hashing, python-jose for tokens, HS256)
- **Frontend:** React + TypeScript (Vite), React Router — just started
- **External data:** MusicBrainz API, used live (not a bulk import) —
  currently under reconsideration, see Open Questions below

## File Structure

```
song-network-poc/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, routers, CORS middleware
│   │   ├── database.py              # engine, SessionLocal, get_db
│   │   ├── core/
│   │   │   └── security.py          # hash_password, verify_password, JWT create/decode
│   │   ├── dependencies/
│   │   │   └── auth.py              # get_current_user — the auth chokepoint
│   │   ├── models/                  # Song, Connection, User, UserSongConnection
│   │   ├── schemas/                 # Pydantic: song, connection, auth
│   │   ├── services/
│   │   │   └── musicbrainz/
│   │   │       ├── client.py        # search_recordings, rate limiter, IPv4 transport workaround
│   │   │       └── schemas.py       # SongSearchResult
│   │   ├── crud/
│   │   │   ├── song.py              # create_song (idempotent by mb_id)
│   │   │   ├── connection.py        # create_connection_service
│   │   │   └── points.py            # get_ranked_supporters, recompute_points_for_connection
│   │   └── routers/
│   │       ├── songs.py             # POST/GET /songs, GET /songs/search (title+artist params —
│       │                          currently local-DB-only, see Search Architecture below)
│   │       ├── connections.py       # POST /connections, GET /connections/{id}/supporters
│   │       └── auth.py              # POST /auth/signup, /auth/login
│   ├── alembic/                     # lives inside backend/ so env.py imports app cleanly
│   └── scripts/
│       └── test_flow.py             # manual end-to-end script (not pytest) — auth, idempotency,
│                                       multi-user convergence, points recompute all verified passing
└── frontend/
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api/
        │   └── client.ts            # apiFetch() — base URL + JWT header wrapper
        └── components/
            └── SongSearch.tsx       # title/artist search, reports selection via onSongSelected prop
```

## Current Status

**Backend — functionally complete for v1 scope.** Auth, song search/save,
connection creation (with idempotency + multi-user convergence), and the
points/reward system are all implemented and verified via `test_flow.py`.
`GET /connections/{id}/supporters` returns the ranked-window supporter list
(user_id, username, rank, points).

**Frontend — just started.** Vite + TS scaffolded, `client.ts` API wrapper
written, `SongSearch` component built and manually tested (search by title
+ artist, reports selection to parent). No router wired in yet beyond
having chosen React Router as the approach. No save/connect/supporters UI
yet. No auth screens yet.

## Known Issues / Environment Notes

- **GlobalProtect VPN network extension** (`com.paloaltonetworks.GlobalProtect...`)
  causes intermittent `httpx.ConnectError` / `SSL_ERROR_SYSCALL` to
  MusicBrainz — first request after a network change succeeds, then all
  subsequent requests (even from `curl`, even to unrelated processes) fail
  until the network changes again. Likely MDM-enforced, may not be fully
  disableable. Workaround: switch networks (e.g. Wi-Fi off/on, or hotspot)
  to reset; not yet solved permanently.
- `user_song_connections` FKs have no `ondelete` behavior set — deferred
  until user deletion is a real feature.
- The pytest suite lives in `backend/tests/`. Run it with
  `backend/.venv/bin/python -m pytest` from the repository root (or
  `.venv/bin/python -m pytest` from `backend/`). The repository-level
  `pytest.ini` configures collection and the backend import path; the legacy
  `backend/test_orm.py` database-inspection script is intentionally excluded
  from collection.

## Search Architecture — Temporary Stopgap (as of this writing)

`GET /songs/search` currently queries the local `songs` table only — no
live MusicBrainz call in the search path at all. A one-time import script
loaded the top 1,000 songs into that table to unblock frontend development
without depending on a flaky live connection (see GlobalProtect VPN issue
below).

**This is explicitly temporary, not the final architecture** — adopted to
delay deciding on the real search/caching approach while frontend work
proceeds. Consequences worth remembering while it's in place:
- Anything outside those 1,000 songs is currently unsearchable/unsavable,
  silently — no live fallback.
- `search_recordings()`, the rate limiter, and the IPv4 transport
  workaround in `services/musicbrainz/client.py` are currently dead code
  on the search path (still relevant to revisit, not deleted).

**Plan:** revisit search architecture once frontend v1 is done. Leading
candidate is a persistent cache-aside design over the live MusicBrainz
API — every search result gets stored locally, the corpus grows
organically from real user queries, `pg_trgm` handles fuzzy/typo-tolerant
matching over that growing local corpus — rather than a one-time
popularity-ranked bulk dump (which goes stale, doesn't solve typos by
itself, and has a hard coverage cutoff). Not yet implemented.

## Roadmap

1. Decide and implement the MusicBrainz caching strategy above.
2. Finish frontend v1: save-song flow, connect-songs flow, supporters/points
   display — explicitly scoped to exclude user profiles/friends.
3. Wire up React Router with more than the single placeholder route.
4. Auth screens (signup/login) on the frontend.
5. Deferred until later, no urgency yet: `ondelete` behavior on
   `user_song_connections` FKs; negative-case tests in `test_flow.py`
   (bad/missing token, nonexistent song ids); a real pytest suite.
6. Explicitly deferred, not yet designed: friends/relationship model and
   user profile pages (total points, friends' points).
