"""Sorting strategies using Strategy pattern with ABC."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .schemas import SortOption, TrackForSorting


@dataclass
class SortContext:
    """Per-request context for strategies that need configuration."""

    artist_rankings: dict[str, int] = field(default_factory=dict)
    album_order: str = "newest"  # "newest" or "oldest"


class SortStrategy(ABC):
    """Abstract base class for sorting strategies."""

    @abstractmethod
    def sort(
        self, tracks: list[TrackForSorting], context: SortContext
    ) -> list[TrackForSorting]:
        """Sort tracks and return sorted list."""
        pass


class AlbumReleaseDateStrategy(SortStrategy):
    """Sort tracks by album release date."""

    def __init__(self, ascending: bool = True):
        self.ascending = ascending

    def sort(
        self, tracks: list[TrackForSorting], context: SortContext
    ) -> list[TrackForSorting]:
        # Defaults: tracks without dates go to end
        date_default = "0000-01-01" if not self.ascending else "9999-12-31"
        album_default = "zzz" if not self.ascending else ""

        # Sort by (release_date, album_name, track_number)
        return sorted(
            tracks,
            key=lambda t: (
                t.album_release_date or date_default,
                t.album_name or album_default,
                t.album_track_number if self.ascending else -t.album_track_number,
            ),
            reverse=not self.ascending,
        )


class ArtistAlphabeticalStrategy(SortStrategy):
    """Sort tracks by artist name alphabetically, then album, then track number."""

    def __init__(self, ascending: bool = True):
        self.ascending = ascending

    def sort(
        self, tracks: list[TrackForSorting], context: SortContext
    ) -> list[TrackForSorting]:
        # Defaults: tracks without artist go to end
        artist_default = "" if self.ascending else "zzz"
        album_default = "" if self.ascending else "zzz"

        # Sort by (artist_name, album_name, track_number)
        return sorted(
            tracks,
            key=lambda t: (
                (t.artist_name or artist_default).lower(),
                (t.album_name or album_default).lower(),
                t.album_track_number if self.ascending else -t.album_track_number,
            ),
            reverse=not self.ascending,
        )


class FavouriteArtistsStrategy(SortStrategy):
    """Sort tracks with favourite artists first, then by album release date."""

    def sort(
        self, tracks: list[TrackForSorting], context: SortContext
    ) -> list[TrackForSorting]:
        """
        Sort tracks prioritizing favourite artists.

        Uses context.artist_rankings to determine favourites.
        Artists in rankings get their rank value (lower = higher priority).
        Artists not in rankings get infinity (appear after favourites).
        Within same artist: sorts by album release date, then track number.
        """
        # Normalize artist rankings to lowercase for case-insensitive matching
        normalized_rankings = {
            name.lower(): rank for name, rank in context.artist_rankings.items()
        }

        # Determine sort direction for albums
        newest_first = context.album_order == "newest"
        date_default = "0000-01-01" if newest_first else "9999-12-31"

        def get_sort_key(track: TrackForSorting):
            artist = (track.artist_name or "").lower()
            # Get rank from normalized rankings, default to infinity
            rank = normalized_rankings.get(artist, float("inf"))

            # Get release date for sorting
            release_date = track.album_release_date or date_default

            return (
                rank,
                artist,
                release_date
                if not newest_first
                else f"_{release_date}",  # Prefix for reverse
                track.album_track_number,
            )

        # Sort, then reverse album dates if newest first
        sorted_tracks = sorted(tracks, key=get_sort_key, reverse=newest_first)

        # For newest_first, we need a more sophisticated approach
        # because we want rank ASC, but date DESC
        # Let's use a cleaner approach:
        if newest_first:

            def get_sort_key_newest(track: TrackForSorting):
                artist = (track.artist_name or "").lower()
                rank = normalized_rankings.get(artist, float("inf"))
                release_date = track.album_release_date or "0000-01-01"
                return (
                    rank,
                    artist,
                    release_date,  # Will be reversed within groups
                    -track.album_track_number,  # Negative for reverse
                )

            # Sort by rank/artist ASC, then by date DESC, track DESC
            # Use tuple negation trick: sort by (rank, artist, -date, -track)
            # Since dates are strings, we need a different approach
            # Group by artist, then reverse date within each group
            sorted_tracks = sorted(
                tracks,
                key=lambda t: (
                    normalized_rankings.get(
                        (t.artist_name or "").lower(), float("inf")
                    ),
                    (t.artist_name or "").lower(),
                    # Invert date string for descending order
                    "".join(
                        chr(255 - ord(c))
                        for c in (t.album_release_date or "0000-01-01")
                    ),
                    t.album_track_number,
                ),
            )
        else:
            sorted_tracks = sorted(
                tracks,
                key=lambda t: (
                    normalized_rankings.get(
                        (t.artist_name or "").lower(), float("inf")
                    ),
                    (t.artist_name or "").lower(),
                    t.album_release_date or "9999-12-31",
                    t.album_track_number,
                ),
            )

        return sorted_tracks


def create_strategy(option: SortOption) -> SortStrategy:
    """Factory function - creates strategy instance per request."""
    match option:
        case SortOption.ALBUM_RELEASE_DATE_ASC:
            return AlbumReleaseDateStrategy(ascending=True)
        case SortOption.ALBUM_RELEASE_DATE_DESC:
            return AlbumReleaseDateStrategy(ascending=False)
        case SortOption.ARTIST_NAME_ASC:
            return ArtistAlphabeticalStrategy(ascending=True)
        case SortOption.ARTIST_NAME_DESC:
            return ArtistAlphabeticalStrategy(ascending=False)
        case SortOption.FAVOURITE_ARTISTS_FIRST:
            return FavouriteArtistsStrategy()
        case _:
            raise ValueError(f"Unknown sort option: {option}")
