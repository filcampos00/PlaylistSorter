"""Schemas for platform-agnostic playlist sorting."""

from enum import Enum

from pydantic import BaseModel


class SortAttribute(str, Enum):
    """Individual sortable attributes for multi-level sorting."""

    ARTIST_NAME = "artist_name"
    ALBUM_NAME = "album_name"
    ALBUM_RELEASE_DATE = "album_release_date"
    TRACK_NUMBER = "track_number"
    FAVOURITE_ARTISTS = "favourite_artists"
    TITLE = "title"


class SortDirection(str, Enum):
    """Sort direction for an attribute."""

    ASC = "asc"
    DESC = "desc"


class SortLevel(BaseModel):
    """A single level in multi-level sorting."""

    attribute: SortAttribute
    direction: SortDirection = SortDirection.ASC


class TrackForSorting(BaseModel):
    """Platform-agnostic track with sorting metadata."""

    video_id: str
    set_video_id: str  # Platform's internal ID for reordering
    title: str
    artist_name: str | None = None
    album_name: str | None = None
    album_release_date: str | None = None  # "YYYY-MM-DD"
    album_track_number: int = 9999  # Track position in album (1-indexed)
