"""Sorting strategies using Strategy pattern with ABC."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .schemas import SortOption, TrackForSorting


@dataclass
class SortContext:
    """Per-request context for strategies that need configuration."""

    artist_rankings: dict[str, int] = field(default_factory=dict)
    # Future: last.fm data, user preferences, etc.


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


def create_strategy(option: SortOption) -> SortStrategy:
    """Factory function - creates strategy instance per request."""
    match option:
        case SortOption.ALBUM_RELEASE_DATE_ASC:
            return AlbumReleaseDateStrategy(ascending=True)
        case SortOption.ALBUM_RELEASE_DATE_DESC:
            return AlbumReleaseDateStrategy(ascending=False)
        case _:
            raise ValueError(f"Unknown sort option: {option}")
