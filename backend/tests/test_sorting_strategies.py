"""Unit tests for sorting strategies."""

import pytest

from app.common.sorting.schemas import SortOption, TrackForSorting
from app.common.sorting.strategies import (
    AlbumReleaseDateStrategy,
    ArtistAlphabeticalStrategy,
    FavouriteArtistsStrategy,
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


class TestArtistAlphabeticalStrategy:
    """Tests for ArtistAlphabeticalStrategy."""

    def test_sort_ascending_a_to_z(self, sample_tracks: list[TrackForSorting]):
        """Ascending: artists sorted A to Z."""
        strategy = ArtistAlphabeticalStrategy(ascending=True)
        context = SortContext()

        sorted_tracks = strategy.sort(sample_tracks, context)

        assert sorted_tracks[0].artist_name == "Artist A"
        assert sorted_tracks[1].artist_name == "Artist B"
        assert sorted_tracks[2].artist_name == "Artist C"
        assert sorted_tracks[3].artist_name == "Artist D"

    def test_sort_descending_z_to_a(self, sample_tracks: list[TrackForSorting]):
        """Descending: artists sorted Z to A."""
        strategy = ArtistAlphabeticalStrategy(ascending=False)
        context = SortContext()

        sorted_tracks = strategy.sort(sample_tracks, context)

        assert sorted_tracks[0].artist_name == "Artist D"
        assert sorted_tracks[1].artist_name == "Artist C"
        assert sorted_tracks[2].artist_name == "Artist B"
        assert sorted_tracks[3].artist_name == "Artist A"

    def test_sort_tracks_same_artist_by_album_and_track(self):
        """Tracks from same artist sorted by album, then track number."""
        tracks = [
            TrackForSorting(
                video_id="v3",
                set_video_id="s3",
                title="Track 3 from Album B",
                artist_name="Artist X",
                album_name="Album B",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Track 2 from Album A",
                artist_name="Artist X",
                album_name="Album A",
                album_track_number=2,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Track 1 from Album A",
                artist_name="Artist X",
                album_name="Album A",
                album_track_number=1,
            ),
        ]

        strategy = ArtistAlphabeticalStrategy(ascending=True)
        context = SortContext()

        sorted_tracks = strategy.sort(tracks, context)

        assert sorted_tracks[0].title == "Track 1 from Album A"
        assert sorted_tracks[1].title == "Track 2 from Album A"
        assert sorted_tracks[2].title == "Track 3 from Album B"

    def test_none_artist_goes_to_end_ascending(self):
        """Tracks without artist go to end when ascending."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="With Artist",
                artist_name="Artist Z",
                album_name="Album",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="No Artist",
                artist_name=None,
                album_name="Album",
                album_track_number=1,
            ),
        ]

        strategy = ArtistAlphabeticalStrategy(ascending=True)
        context = SortContext()

        sorted_tracks = strategy.sort(tracks, context)

        assert sorted_tracks[0].title == "No Artist"  # Empty string sorts first
        assert sorted_tracks[1].title == "With Artist"


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

    def test_create_artist_name_asc(self):
        """Factory creates ascending artist name strategy."""
        strategy = create_strategy(SortOption.ARTIST_NAME_ASC)
        assert isinstance(strategy, ArtistAlphabeticalStrategy)
        assert strategy.ascending is True

    def test_create_artist_name_desc(self):
        """Factory creates descending artist name strategy."""
        strategy = create_strategy(SortOption.ARTIST_NAME_DESC)
        assert isinstance(strategy, ArtistAlphabeticalStrategy)
        assert strategy.ascending is False

    def test_invalid_sort_option(self):
        """Factory raises error for unknown option."""
        with pytest.raises(ValueError, match="Unknown sort option"):
            create_strategy("invalid_option")

    def test_create_favourite_artists_strategy(self):
        """Factory creates favourite artists strategy."""
        strategy = create_strategy(SortOption.FAVOURITE_ARTISTS_FIRST)
        assert isinstance(strategy, FavouriteArtistsStrategy)


class TestFavouriteArtistsStrategy:
    """Tests for FavouriteArtistsStrategy."""

    def test_favourite_artists_first(self, sample_tracks: list[TrackForSorting]):
        """Favourite artists appear before non-favourites."""
        strategy = FavouriteArtistsStrategy()
        # Artist C is favourite (rank 0), Artist A is second favourite (rank 1)
        context = SortContext(artist_rankings={"Artist C": 0, "Artist A": 1})

        sorted_tracks = strategy.sort(sample_tracks, context)

        # Artist C should be first, Artist A second
        assert sorted_tracks[0].artist_name == "Artist C"
        assert sorted_tracks[1].artist_name == "Artist A"
        # Non-favourites (B, D) sorted alphabetically after favourites
        assert sorted_tracks[2].artist_name == "Artist B"
        assert sorted_tracks[3].artist_name == "Artist D"

    def test_empty_rankings_sorts_alphabetically(self, sample_tracks: list[TrackForSorting]):
        """With no favourites, falls back to alphabetical order."""
        strategy = FavouriteArtistsStrategy()
        context = SortContext(artist_rankings={})

        sorted_tracks = strategy.sort(sample_tracks, context)

        # All artists have rank infinity, so sorted alphabetically
        assert sorted_tracks[0].artist_name == "Artist A"
        assert sorted_tracks[1].artist_name == "Artist B"
        assert sorted_tracks[2].artist_name == "Artist C"
        assert sorted_tracks[3].artist_name == "Artist D"

    def test_case_insensitive_matching(self):
        """Artist matching is case-insensitive."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Track 1",
                artist_name="METALLICA",
                album_name="Album",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Track 2",
                artist_name="queen",
                album_name="Album",
                album_track_number=1,
            ),
        ]

        strategy = FavouriteArtistsStrategy()
        # Different case in rankings
        context = SortContext(artist_rankings={"Queen": 0, "metallica": 1})

        sorted_tracks = strategy.sort(tracks, context)

        # Queen should be first despite case difference
        assert sorted_tracks[0].artist_name == "queen"
        assert sorted_tracks[1].artist_name == "METALLICA"

    def test_same_favourite_artist_sorted_by_album_release_date(self):
        """Tracks from same favourite artist are sorted by album release date then track number."""
        tracks = [
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Track 2",
                artist_name="Queen",
                album_name="Newer Album",
                album_release_date="2020-01-01",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Track 1",
                artist_name="Queen",
                album_name="Oldest Album",
                album_release_date="2010-01-01",
                album_track_number=2,
            ),
            TrackForSorting(
                video_id="v3",
                set_video_id="s3",
                title="Track 3",
                artist_name="Queen",
                album_name="Oldest Album",
                album_release_date="2010-01-01",
                album_track_number=1,
            ),
        ]

        strategy = FavouriteArtistsStrategy()
        
        # Test with oldest albums first
        context = SortContext(artist_rankings={"Queen": 0}, album_order="oldest")
        sorted_tracks = strategy.sort(tracks, context)

        # Oldest first: 2010 album tracks first (by track number), then 2020 album
        assert sorted_tracks[0].title == "Track 3"  # 2010, track 1
        assert sorted_tracks[1].title == "Track 1"  # 2010, track 2
        assert sorted_tracks[2].title == "Track 2"  # 2020, track 1

    def test_newest_albums_first(self):
        """Test newest albums first sorting within favourite artist."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Old Track",
                artist_name="Queen",
                album_name="Old Album",
                album_release_date="2010-01-01",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="New Track",
                artist_name="Queen",
                album_name="New Album",
                album_release_date="2020-01-01",
                album_track_number=1,
            ),
        ]

        strategy = FavouriteArtistsStrategy()
        context = SortContext(artist_rankings={"Queen": 0}, album_order="newest")

        sorted_tracks = strategy.sort(tracks, context)

        # Newest first: 2020 album should come before 2010
        assert sorted_tracks[0].title == "New Track"  # 2020
        assert sorted_tracks[1].title == "Old Track"  # 2010
