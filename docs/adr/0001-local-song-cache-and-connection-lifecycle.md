# ADR 0001: Local Song Cache and Connection Lifecycle

- Status: Accepted
- Date: 2026-09-05

## Context

The application needs local song IDs for relationships and supporter records,
while MusicBrainz provides external recording search results. The backend must
also support repeated searches and repeated attempts to create the same song
connection.

## Decision

The backend uses the local `songs` table as the first search source. If a
search has no local matches, it queries MusicBrainz and stores the returned
recordings locally before returning them.

Songs are de-duplicated by their MusicBrainz recording ID (`mb_id`).
Connections reference local `songs.id` values and normalize each pair by
storing the smaller ID first.

The connection itself is shared by all users. A separate
`user_song_connections` row records each user's support, with a unique
constraint preventing the same user from supporting the same connection more
than once.

## Consequences

- A search can add songs to the local database even when no connection is
  created.
- Connection creation does not need to call MusicBrainz; it only accepts
  local song IDs.
- Reversed song order resolves to the same connection.
- The database contains both catalog records that are connected and records
  that were only discovered through search.
- Supporter order and points can be calculated from local timestamps and
  supporter records.
