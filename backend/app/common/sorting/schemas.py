"""Schemas for platform-agnostic playlist sorting."""

from enum import Enum

from pydantic import BaseModel


class SortOption(str, Enum):
    """Available sorting options for playlists."""

    ALBUM_RELEASE_DATE_ASC = "album_release_date_asc"
    ALBUM_RELEASE_DATE_DESC = "album_release_date_desc"
    ARTIST_NAME_ASC = "artist_name_asc"
    ARTIST_NAME_DESC = "artist_name_desc"
    FAVOURITE_ARTISTS_FIRST = "favourite_artists_first"


class TrackForSorting(BaseModel):
    """Platform-agnostic track with sorting metadata."""

    video_id: str
    set_video_id: str  # Platform's internal ID for reordering
    title: str
    artist_name: str | None = None
    album_name: str | None = None
    album_release_date: str | None = None  # "YYYY-MM-DD"
    album_track_number: int = 9999  # Track position in album (1-indexed)
