# Song Search and Connection Architecture

This document describes the current backend implementation for finding songs,
creating song connections, authenticating users, recording supporters, and
calculating points.

## Overview

The backend stores songs in a local catalog. Search checks that catalog first.
Only when a search has no local matches does the backend query MusicBrainz.
MusicBrainz results are written to the local catalog before they are returned,
so a search can add songs even when the user never creates a connection.

Connections always reference local song IDs. MusicBrainz IDs are used to
identify and de-duplicate songs in the catalog, but they are not used as
foreign keys by the connection tables.

## Song search

The public endpoint is:

```text
GET /songs/search?title=<title>&artist=<artist>
```

At least one of `title` or `artist` must be provided.

### Local-search path

The endpoint builds a case-insensitive partial-match query against the local
`songs` table:

- `title` is matched with `Song.title.ilike("%<title>%")` when supplied.
- `artist` is matched with `Song.artist.ilike("%<artist>%")` when supplied.
- When both are supplied, both filters must match.
- Results are ordered by title and artist and limited to 25 rows.

If at least one local result is found, those results are returned immediately.
MusicBrainz is not queried in this case.

### MusicBrainz fallback path

If the local query returns no rows, the endpoint calls the MusicBrainz
recording-search client. The client:

- Builds a recording query from the supplied title and/or artist.
- Sends the request with the configured User-Agent.
- Enforces a shared delay between requests.
- Retries connection errors and selected rate-limit/server errors.
- Converts MusicBrainz responses into the application's song-result shape.

Each returned MusicBrainz recording is checked by `mb_id`. New records are
inserted into `songs`, the transaction is committed, and the resulting local
song records are returned. Existing records with the same `mb_id` are reused.

The fallback therefore has a cache-aside behavior:

```text
local search
    ├── results found → return local results
    └── no results
          └── MusicBrainz search
                └── insert/reuse local songs
                      └── commit and return local songs
```

The search endpoint is not protected by the authentication dependency. A user
does not need to be logged in to perform a search or cause MusicBrainz results
to be cached.

If MusicBrainz fails, the endpoint returns HTTP 503. An empty MusicBrainz
result produces an empty response and adds no songs.

## Saving a song directly

The authenticated endpoint is:

```text
POST /songs/
```

The request contains an `mb_id`, title, and artist. The endpoint first checks
for an existing song with that `mb_id`. If one exists, it returns that record.
Otherwise it creates and commits a new local song.

This endpoint is separate from the search fallback. Search can populate the
catalog without authentication; direct song creation requires authentication.

## Connection creation

The authenticated endpoint is:

```text
POST /connections/
{
  "song_1_id": 12,
  "song_2_id": 34
}
```

The connection service performs these steps:

1. Rejects a request where both song IDs are equal.
2. Normalizes the pair so the smaller ID is stored as `song_1_id` and the
   larger ID as `song_2_id`.
3. Verifies that both song IDs exist in the local `songs` table.
4. Finds an existing `connections` row for the normalized pair or creates
   one.
5. Checks whether the current user already supports that connection.
6. If not, creates a `user_song_connections` row and recalculates points.
7. Commits the transaction and returns the connection.

Because of pair normalization, requests for `(12, 34)` and `(34, 12)` refer to
the same connection. The database also has a unique constraint on the ordered
pair `(song_1_id, song_2_id)`.

If either ID is unknown, the endpoint returns an error. It does not query
MusicBrainz during connection creation. The client must search for the song
first, receive or create a local song record, and then submit that local ID.

## Authentication

Authentication is implemented with users, password hashes, and JWTs.

### Signup

```text
POST /auth/signup
```

The username must be unique. The submitted password is hashed before the user
is stored in the `users` table.

### Login

```text
POST /auth/login
```

The backend verifies the username and password. On success it creates an HS256
JWT containing the user ID and a one-day expiration, then places it in an
`HttpOnly` cookie named `access_token`.

The authentication dependency accepts the token from either:

- the `access_token` cookie, or
- a bearer token in the Authorization header.

It decodes the token, loads the corresponding user, and returns HTTP 401 when
the token is missing, invalid, expired, or refers to a nonexistent user.

The current login cookie uses `SameSite=Lax` and `secure=False`.

## Supporter records

The `user_song_connections` table records a user's support for a connection.
It contains:

- `user_id`
- `connection_id`
- `created_at`
- `points`

The `(user_id, connection_id)` pair is unique. Therefore, a user can support a
given connection only once. Repeating the connection request is a no-op for
that user's supporter record, although the existing connection is still
returned.

The `created_at` value establishes supporter order. The connection's supporter
endpoint returns supporters in ascending creation order and exposes the first
20 supporters with their rank and points.

## Points calculation

When a new supporter is added, the backend counts all supporters for the
connection and selects the earliest 20 by `created_at`.

For each selected supporter, it calculates:

```text
points = ln(total_supporters / rank)
```

where:

- `total_supporters` is the total number of supporters for the connection.
- `rank` starts at 1 for the earliest supporter.

Only the selected first 20 records are recalculated. Supporters outside that
window retain their stored points value.

## Tables and relationships

```text
users
  └──< user_song_connections >── connections
                                  ├── songs (song_1_id)
                                  └── songs (song_2_id)
```

- `songs` stores the local catalog and unique MusicBrainz IDs.
- `connections` stores one normalized pair of songs.
- `users` stores accounts and password hashes.
- `user_song_connections` links users to connections and stores supporter
  timing and points.
