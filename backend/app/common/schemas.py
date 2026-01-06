"""Common Pydantic schemas used across platforms."""

from pydantic import BaseModel, Field


class AuthHeaders(BaseModel):
    """Raw headers string pasted from browser."""

    headers_raw: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Raw HTTP headers copied from browser DevTools",
    )


class AuthTestResponse(BaseModel):
    """Response from auth test endpoint."""

    success: bool
    message: str
    channel_name: str | None = None


class Playlist(BaseModel):
    """Generic playlist representation (platform-agnostic)."""

    playlist_id: str
    title: str
    thumbnail_url: str | None = None
    track_count: int | None = None


class PlaylistsResponse(BaseModel):
    """Response containing user's playlists."""

    success: bool
    message: str
    playlists: list[Playlist] = []


class SortRequest(BaseModel):
    """Request body for sorting a playlist."""

    headers_raw: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Raw HTTP headers copied from browser DevTools",
    )
    favourite_artists: list[str] = Field(
        default=[],
        description="Optional list of favourite artist names for sorting",
    )
    album_order: str = Field(
        default="newest",
        description="Album sort order: 'newest' or 'oldest'",
    )


class SortResponse(BaseModel):
    """Response from sorting a playlist."""

    success: bool
    message: str
    tracks_reordered: int = 0
