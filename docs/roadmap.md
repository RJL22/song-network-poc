# Project Status and Roadmap

## Purpose

Song Network is a portfolio project for exploring backend engineering through a crowdsourced song-similarity graph. The core product idea is that independent users form connections between songs they believe are similar; repeated connections provide a community signal.

The project is intentionally a proof of concept rather than a production-scale music catalog. The goal is to make architecture and design tradeoffs visible while building a complete application flow.

## Technology

- Backend: FastAPI, PostgreSQL, SQLAlchemy 2.x, Alembic, and Docker.
- Authentication: JWTs, passlib/bcrypt password hashing, and HS256.
- Frontend: React, TypeScript, and Vite.
- External data: MusicBrainz recording search with local cache-aside storage.

## Current status

### Backend

Implemented:

- User signup, login, logout, and authenticated-user lookup.
- JWT authentication through an HttpOnly cookie, with bearer-token fallback.
- Local song catalog and MusicBrainz fallback search.
- Idempotent song creation by MusicBrainz recording ID.
- Symmetric, normalized song connections.
- Shared connections with per-user supporter records.
- Ranked supporters and windowed points recalculation.
- Connection history for the current user.
- API and configuration tests.

### Frontend

Implemented:

- Login and signup screens.
- Cookie-based authentication state.
- Song search and selection.
- Song connection creation.
- Community recommendations and supporter display.
- Current-user connection history.

The frontend is intentionally lightweight. It does not yet have a full routing library, polished error/loading states, or user profile features.

## Known issues and environment notes

- MusicBrainz connectivity can be unreliable on networks where the GlobalProtect VPN extension interferes with TLS connections. The client includes connection reuse, throttling, and retries, but the network issue may still require changing networks.
- The MusicBrainz client User-Agent still uses a placeholder contact address and should be updated before broader external use.
- The `user_song_connections` foreign keys do not yet specify deletion behavior because user deletion is not currently a product feature.
- The backend tests use SQLite for fast isolation; PostgreSQL migration behavior should also be checked against a representative database.
- The current frontend toolchain requires a newer Node.js version than the Node 18 environment previously used for verification.

## Roadmap

1. Validate the unique song-pair migration against any existing production-like data and resolve duplicates before applying it to a populated database.
2. Finish frontend reliability and polish: loading states, better error handling, complete routing, and responsive layout.
3. Expand automated coverage for MusicBrainz fallback/retries, authentication failures, missing songs, migration behavior, and frontend flows.
4. Replace the placeholder MusicBrainz User-Agent contact information.
5. Decide whether fuzzy matching, PostgreSQL `pg_trgm`, or another search strategy is needed as the local catalog grows.
6. Add user profiles and friends only after the core connection and discovery flow is stable.

## Deferred product scope

User profiles, friends, social relationship modeling, and profile-level point summaries are intentionally deferred. They should not shape the current schema until the core song-search and connection lifecycle has been exercised further.
