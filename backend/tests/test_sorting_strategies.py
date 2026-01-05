"""Unit tests for sorting strategies."""

import pytest

from app.common.sorting.schemas import SortOption, TrackForSorting
from app.common.sorting.strategies import (
    AlbumReleaseDateStrategy,
    SortContext,
    create_strategy,
)


@pytest.fixture
def sample_tracks() -> list[TrackForSorting]:
    """Sample tracks with varying album release dates."""
    return [
        TrackForSorting(
            video_id="vid1",
            set_video_id="set1",
            title="Song from 2020",
            artist_name="Artist A",
            album_name="Album 2020",
            album_release_date="2020-05-15",
            album_track_number=1,
        ),
        TrackForSorting(
            video_id="vid2",
            set_video_id="set2",
            title="Song from 2018",
            artist_name="Artist B",
            album_name="Album 2018",
            album_release_date="2018-01-01",
            album_track_number=5,
        ),
        TrackForSorting(
            video_id="vid3",
            set_video_id="set3",
            title="Song from 2023",
            artist_name="Artist C",
            album_name="Album 2023",
            album_release_date="2023-11-20",
            album_track_number=2,
        ),
        TrackForSorting(
            video_id="vid4",
            set_video_id="set4",
            title="Song with no date",
            artist_name="Artist D",
            album_name="Unknown Album",
            album_release_date=None,
            album_track_number=9999,
        ),
    ]


class TestAlbumReleaseDateStrategy:
    """Tests for AlbumReleaseDateStrategy."""

    def test_sort_ascending_oldest_first(self, sample_tracks: list[TrackForSorting]):
        """Ascending: oldest albums first."""
        strategy = AlbumReleaseDateStrategy(ascending=True)
        context = SortContext()

        sorted_tracks = strategy.sort(sample_tracks, context)

        assert sorted_tracks[0].album_release_date == "2018-01-01"
        assert sorted_tracks[1].album_release_date == "2020-05-15"
        assert sorted_tracks[2].album_release_date == "2023-11-20"
        # Tracks without date go to end (default 9999)
        assert sorted_tracks[3].album_release_date is None

    def test_sort_descending_newest_first(self, sample_tracks: list[TrackForSorting]):
        """Descending: newest albums first."""
        strategy = AlbumReleaseDateStrategy(ascending=False)
        context = SortContext()

        sorted_tracks = strategy.sort(sample_tracks, context)

        assert sorted_tracks[0].album_release_date == "2023-11-20"
        assert sorted_tracks[1].album_release_date == "2020-05-15"
        assert sorted_tracks[2].album_release_date == "2018-01-01"
        # Tracks without date go to end (default 0000)
        assert sorted_tracks[3].album_release_date is None

    def test_empty_list(self):
        """Sorting empty list returns empty list."""
        strategy = AlbumReleaseDateStrategy(ascending=True)
        context = SortContext()

        sorted_tracks = strategy.sort([], context)

        assert sorted_tracks == []

    def test_sort_tracks_within_same_album(self):
        """Tracks from the same album should be sorted by album_track_number."""
        tracks = [
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Track 2",
                album_name="Album A",
                album_release_date="2020-01-01",
                album_track_number=2,
            ),
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Track 1",
                album_name="Album A",
                album_release_date="2020-01-01",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v3",
                set_video_id="s3",
                title="Track 3",
                album_name="Album A",
                album_release_date="2020-01-01",
                album_track_number=3,
            ),
        ]

        strategy = AlbumReleaseDateStrategy(ascending=True)
        context = SortContext()

        sorted_tracks = strategy.sort(tracks, context)

        assert sorted_tracks[0].title == "Track 1"
        assert sorted_tracks[1].title == "Track 2"
        assert sorted_tracks[2].title == "Track 3"


class TestCreateStrategy:
    """Tests for the strategy factory."""

    def test_create_album_date_asc(self):
        """Factory creates ascending album date strategy."""
        strategy = create_strategy(SortOption.ALBUM_RELEASE_DATE_ASC)
        assert isinstance(strategy, AlbumReleaseDateStrategy)
        assert strategy.ascending is True

    def test_create_album_date_desc(self):
        """Factory creates descending album date strategy."""
        strategy = create_strategy(SortOption.ALBUM_RELEASE_DATE_DESC)
        assert isinstance(strategy, AlbumReleaseDateStrategy)
        assert strategy.ascending is False

    def test_invalid_sort_option(self):
        """Factory raises error for unknown option."""
        with pytest.raises(ValueError, match="Unknown sort option"):
            create_strategy("invalid_option")
