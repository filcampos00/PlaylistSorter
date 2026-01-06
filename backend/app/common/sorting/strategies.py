"""Sorting strategies using composable comparators for multi-level sorting."""

from dataclasses import dataclass, field
from typing import Callable

from .schemas import SortAttribute, SortDirection, SortLevel, TrackForSorting


@dataclass
class SortContext:
    """Per-request context for strategies that need configuration."""

    artist_rankings: dict[str, int] = field(default_factory=dict)


class _NegatedStr:
    """
    Wrapper for descending string comparison.
    Compares in reverse order without character manipulation.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str):
        self._value = value

    def __lt__(self, other: "_NegatedStr") -> bool:
        return self._value > other._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _NegatedStr):
            return NotImplemented
        return self._value == other._value

    def __le__(self, other: "_NegatedStr") -> bool:
        return self._value >= other._value


def _get_artist_name_key(
    track: TrackForSorting, direction: SortDirection, context: SortContext
) -> tuple:
    """Get sort key for artist name."""
    artist = (track.artist_name or "").lower()
    if direction == SortDirection.DESC:
        return (_NegatedStr(artist),)
    return (artist,)


def _get_album_name_key(
    track: TrackForSorting, direction: SortDirection, context: SortContext
) -> tuple:
    """Get sort key for album name."""
    album = (track.album_name or "").lower()
    if direction == SortDirection.DESC:
        return (_NegatedStr(album),)
    return (album,)


def _get_album_release_date_key(
    track: TrackForSorting, direction: SortDirection, context: SortContext
) -> tuple:
    """Get sort key for album release date."""
    # Default: tracks without dates go to end
    if direction == SortDirection.ASC:
        date = track.album_release_date or "9999-12-31"
        return (date,)
    else:
        date = track.album_release_date or "0000-01-01"
        return (_NegatedStr(date),)


def _get_track_number_key(
    track: TrackForSorting, direction: SortDirection, context: SortContext
) -> tuple:
    """Get sort key for track number."""
    num = track.album_track_number
    if direction == SortDirection.DESC:
        return (-num,)
    return (num,)


def _get_favourite_artists_key(
    track: TrackForSorting, direction: SortDirection, context: SortContext
) -> tuple:
    """Get sort key for favourite artists ranking."""
    # Normalize artist name for matching
    normalized_rankings = {
        name.lower(): rank for name, rank in context.artist_rankings.items()
    }
    artist = (track.artist_name or "").lower()
    rank = normalized_rankings.get(artist, float("inf"))

    if direction == SortDirection.DESC:
        # Reverse ranking (non-favourites first)
        return (-rank if rank != float("inf") else float("-inf"),)
    return (rank,)


def _get_title_key(
    track: TrackForSorting, direction: SortDirection, context: SortContext
) -> tuple:
    """Get sort key for track title."""
    title = (track.title or "").lower()
    if direction == SortDirection.DESC:
        return (_NegatedStr(title),)
    return (title,)


# Registry of key extractors per attribute
_KEY_EXTRACTORS: dict[
    SortAttribute,
    Callable[[TrackForSorting, SortDirection, SortContext], tuple],
] = {
    SortAttribute.ARTIST_NAME: _get_artist_name_key,
    SortAttribute.ALBUM_NAME: _get_album_name_key,
    SortAttribute.TITLE: _get_title_key,
    SortAttribute.ALBUM_RELEASE_DATE: _get_album_release_date_key,
    SortAttribute.TRACK_NUMBER: _get_track_number_key,
    SortAttribute.FAVOURITE_ARTISTS: _get_favourite_artists_key,
}


def multi_level_sort(
    tracks: list[TrackForSorting],
    levels: list[SortLevel],
    context: SortContext,
) -> list[TrackForSorting]:
    """
    Sort tracks by multiple levels.

    Args:
        tracks: List of tracks to sort.
        levels: Ordered list of sort levels (primary first).
        context: Context with additional data (e.g., artist rankings).

    Returns:
        Sorted list of tracks.
    """
    import logging

    logger = logging.getLogger(__name__)

    if not tracks or not levels:
        return tracks

    # Log the sort configuration
    level_desc = " → ".join(
        f"{lvl.attribute.value}({lvl.direction.value})" for lvl in levels
    )
    logger.info(f"[SORT] Sorting {len(tracks)} tracks by: {level_desc}")

    def get_composite_key(track: TrackForSorting) -> tuple:
        """Build composite sort key from all levels."""
        key_parts: list = []
        for level in levels:
            extractor = _KEY_EXTRACTORS.get(level.attribute)
            if extractor:
                key_parts.extend(extractor(track, level.direction, context))
        return tuple(key_parts)

    result = sorted(tracks, key=get_composite_key)

    # Log first 20 tracks of sorted result for debugging
    logger.debug("[SORT] Sorted order (first 20 tracks):")
    for i, track in enumerate(result[:20]):
        logger.debug(
            f"  {i + 1:2}. {track.artist_name or 'Unknown':<20} | "
            f"{track.album_name or 'Unknown':<30} | "
            f"{track.album_release_date or 'N/A':<10} | "
            f"Track {track.album_track_number:2} | {track.title}"
        )

    return result


# --- Preset Definitions ---
# Common sort configurations for convenience

PRESET_DISCOGRAPHY: list[SortLevel] = [
    SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
    SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.ASC),
    SortLevel(attribute=SortAttribute.TRACK_NUMBER, direction=SortDirection.ASC),
]

PRESET_LATEST_RELEASES: list[SortLevel] = [
    SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.DESC),
    SortLevel(attribute=SortAttribute.TRACK_NUMBER, direction=SortDirection.ASC),
]

PRESET_FAVOURITES_FIRST: list[SortLevel] = [
    SortLevel(attribute=SortAttribute.FAVOURITE_ARTISTS, direction=SortDirection.ASC),
    SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
    SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.DESC),
    SortLevel(attribute=SortAttribute.TRACK_NUMBER, direction=SortDirection.ASC),
]
