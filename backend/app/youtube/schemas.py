"""Pydantic schemas specific to YouTube Music."""

from pydantic import BaseModel


class YouTubePlaylist(BaseModel):
    """A YouTube Music playlist."""

    playlist_id: str
    title: str
    thumbnail_url: str | None = None
    track_count: int | None = None
