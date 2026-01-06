"""Common Pydantic schemas used across platforms."""

from pydantic import BaseModel, Field, model_validator

from .sorting import SortAttribute, SortLevel


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
    sort_levels: list[SortLevel] = Field(
        ...,
        min_length=1,
        description="Ordered list of sort levels (primary first)",
    )
    favourite_artists: list[str] = Field(
        default=[],
        description="Optional list of favourite artist names for sorting",
    )

    @model_validator(mode="after")
    def validate_sort_level_compatibility(self) -> "SortRequest":
        """
        Validate that sort levels are logically compatible.

        Rules:
        1. Track Number requires album context (album_name or album_release_date before it)
        2. Album attributes should not appear after Track Number
        3. No duplicate attributes
        """
        levels = self.sort_levels
        seen_attrs: set[SortAttribute] = set()

        for idx, level in enumerate(levels):
            attr = level.attribute

            # Rule 3: No duplicates
            if attr in seen_attrs:
                raise ValueError(f"Duplicate sort attribute: {attr.value}")
            seen_attrs.add(attr)

            preceding_attrs = {lv.attribute for lv in levels[:idx]}

            # Rule 1: Track Number needs album context
            if attr == SortAttribute.TRACK_NUMBER:
                has_album_context = (
                    SortAttribute.ALBUM_NAME in preceding_attrs
                    or SortAttribute.ALBUM_RELEASE_DATE in preceding_attrs
                )
                if not has_album_context:
                    raise ValueError(
                        "Track Number requires Album Name or Album Release Date before it"
                    )

            # Rule 2: Album attributes shouldn't come after Track Number
            if SortAttribute.TRACK_NUMBER in preceding_attrs:
                if attr in (SortAttribute.ALBUM_NAME, SortAttribute.ALBUM_RELEASE_DATE):
                    raise ValueError(f"{attr.value} cannot appear after Track Number")

        return self


class SortResponse(BaseModel):
    """Response from sorting a playlist."""

    success: bool
    message: str
    tracks_reordered: int = 0
