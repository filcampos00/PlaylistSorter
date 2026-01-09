---
description: Decisions made regarding project
---

# Design Decisions & Rationale

## API Selection: Spotify
- **Decision**: Use `spotipy` library.
- **Rationale**: Standard Python wrapper, handles OAuth implementation and rate limiting.

## API Selection: ytmusicapi vs. Official YouTube Data API v3
- **Decision**: Use `ytmusicapi` (unofficial).
- **Rationale**: 
  - **Quotas**: The official API is limited to 10k units/day. Moving a single song costs 50 units. A 300-song playlist would require 15k units to sort, exceeding the daily limit. `ytmusicapi` has no such hard quota.
  - **Metadata**: `ytmusicapi` provides specific music metadata (Album, Artist, Track Number) that the official API lacks.
- **Risk**: Being unofficial, it could break if YouTube changes internal endpoints. Mitigation: Centralize API calls for easy updates.

## Backend Framework: FastAPI vs. Flask
- **Decision**: use FastAPI.
- **Rationale**:
  - **Automatic Docs**: Built-in Swagger UI for easy endpoint testing.
  - **Performance**: High performance with native `async/await` support.
  - **Validation**: Pydantic integration ensures data integrity automatically.
  - **Modernity**: Better type-hinting support and developer experience.

## Infrastructure Choice: GitHub Actions vs. Jenkins
- **Decision**: GitHub Actions.
- **Rationale**: Zero maintenance (SaaS), built-in Integration with the repo, and simplified YAML configuration.

## Logging Strategy: Centralized vs. Per-Module
- **Decision**: Centralized configuration in `core/logging.py` utilizing the Singleton pattern.
- **Rationale**:
  - **Single Source of Truth**: Prevents duplicate handlers and inconsistent formatting across modules.
  - **Environment Control**: Easier to switch between File-only (Production) and Console (Development) outputs.
  - **Performance**: Silences noisy third-party loggers (`urllib3`) while keeping application `DEBUG` logs active.
  - **Persistence**: Ensures logs are written to physical files (`logs/playlist_sorter.log`) for post-mortem analysis, rather than lost in ephemeral console streams.

## Feature: Favourite Artists Implementation
- **Architecture**: Stateless Design.
- **Decision**: Favourite artists are passed in the API request body (`POST`) rather than stored in a user database.
- **Rationale**:
  - **Privacy**: No need to store user preferences or create user accounts.
  - **Flexibility**: Users can try different combinations without permanent state management.

- **External Integration**: Last.fm Proxy.
- **Decision**: Backend proxies Last.fm API calls (`/api/lastfm/top-artists`) instead of direct frontend calls.
- **Rationale**:
  - **Security**: Keeps the `LASTFM_API_KEY` secure in backend environment variables.
  - **CORS**: Avoids Cross-Origin Resource Sharing issues common with direct browser-to-API calls.
  - **Simplification**: Frontend deals with a simplified internal schema.

- **Input Handling**: Newline Separation.
- **Decision**: Manual input parses artists by newline (`\n`) instead of commas.
- **Rationale**: Supports artists with commas in their names (e.g., "Tyler, The Creator", "Earth, Wind & Fire").

## Sorting Architecture: User-Controlled Multi-Level
- **Decision**: Replace fixed sort options with composable multi-level sorting.
- **Rationale**:
  - **Transparency**: Original design hid secondary/tertiary sorts from users.
  - **Flexibility**: Users can define their own sort hierarchy (e.g., Artist → Album Date → Track #).
  - **Presets**: Common configurations exposed as one-click shortcuts for simplicity.
- **Validation**: Both frontend (UI hides invalid options) and backend (Pydantic validator) enforce compatibility rules.
- **Key Rules**:
  - Track Number requires album context (Album Name or Album Release Date before it).
  - Album attributes cannot appear after Track Number.
  - No duplicate attributes.

## UI Design: Simple + Advanced Mode
- **Decision**: Show presets by default, hide multi-level builder behind "Custom Sort" toggle.
- **Rationale**:
  - **80/20 Rule**: Most users want one-click presets; power users can access full flexibility.
  - **Reduced Cognitive Load**: Fewer options in the default view prevents confusion.

## Release Date Metadata: YouTube Upload Date Limitation
- **Problem**: YouTube Music metadata uses "Upload Date" (e.g., 2011 for a 1970s song), causing incorrect chronological sorting for older music.
- **Investigation**: Tested Discogs (imprecise precision), MusicBrainz (slow rate limits), and iTunes Search API.
- **Decision**: Accept YouTube's upload date as-is. No external metadata integration planned.
- **Rationale**:
  - **Complexity**: Implementing a robust metadata service with local database caching is significant scope creep.
  - **Diminishing Returns**: Most modern music has correct dates; edge cases (re-uploads of old songs) are rare.
  - **User Experience**: The immediate need is sorting functionality; perfect historical accuracy is a "nice to have" that may never be addressed.