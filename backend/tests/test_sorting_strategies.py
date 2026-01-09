"""Unit tests for multi-level sorting."""

import pytest

from app.common.sorting.schemas import (
    SortAttribute,
    SortDirection,
    SortLevel,
    TrackForSorting,
)
from app.common.sorting.strategies import (
    SortContext,
    multi_level_sort,
    PRESET_DISCOGRAPHY,
    PRESET_LATEST_RELEASES,
    PRESET_FAVOURITES_FIRST,
)


@pytest.fixture
def sample_tracks() -> list[TrackForSorting]:
    """Sample tracks with varying attributes."""
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


class TestMultiLevelSort:
    """Tests for multi_level_sort function."""

    def test_sort_by_artist_asc(self, sample_tracks: list[TrackForSorting]):
        """Sort by artist name ascending."""
        levels = [
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC)
        ]
        context = SortContext()

        result = multi_level_sort(sample_tracks, levels, context)

        assert result[0].artist_name == "Artist A"
        assert result[1].artist_name == "Artist B"
        assert result[2].artist_name == "Artist C"
        assert result[3].artist_name == "Artist D"

    def test_sort_by_artist_desc(self, sample_tracks: list[TrackForSorting]):
        """Sort by artist name descending."""
        levels = [
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.DESC)
        ]
        context = SortContext()

        result = multi_level_sort(sample_tracks, levels, context)

        assert result[0].artist_name == "Artist D"
        assert result[1].artist_name == "Artist C"
        assert result[2].artist_name == "Artist B"
        assert result[3].artist_name == "Artist A"

    def test_sort_by_album_date_asc(self, sample_tracks: list[TrackForSorting]):
        """Sort by album release date ascending (oldest first)."""
        levels = [
            SortLevel(
                attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.ASC
            )
        ]
        context = SortContext()

        result = multi_level_sort(sample_tracks, levels, context)

        assert result[0].album_release_date == "2018-01-01"
        assert result[1].album_release_date == "2020-05-15"
        assert result[2].album_release_date == "2023-11-20"
        # Tracks without date go to end
        assert result[3].album_release_date is None

    def test_sort_by_album_date_desc(self, sample_tracks: list[TrackForSorting]):
        """Sort by album release date descending (newest first)."""
        levels = [
            SortLevel(
                attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.DESC
            )
        ]
        context = SortContext()

        result = multi_level_sort(sample_tracks, levels, context)

        assert result[0].album_release_date == "2023-11-20"
        assert result[1].album_release_date == "2020-05-15"
        assert result[2].album_release_date == "2018-01-01"
        # Tracks without date go to end
        assert result[3].album_release_date is None

    def test_multi_level_artist_then_date(self):
        """Multi-level: Artist A-Z, then Album Date oldest first."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="New Song",
                artist_name="Artist A",
                album_release_date="2023-01-01",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Old Song",
                artist_name="Artist A",
                album_release_date="2010-01-01",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v3",
                set_video_id="s3",
                title="B Song",
                artist_name="Artist B",
                album_release_date="2020-01-01",
                album_track_number=1,
            ),
        ]
        levels = [
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
            SortLevel(
                attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.ASC
            ),
        ]
        context = SortContext()

        result = multi_level_sort(tracks, levels, context)

        # Artist A first, then by date oldest first
        assert result[0].title == "Old Song"  # Artist A, 2010
        assert result[1].title == "New Song"  # Artist A, 2023
        assert result[2].title == "B Song"  # Artist B

    def test_multi_level_with_track_number(self):
        """Multi-level: Album Date, then Track Number."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Track 3",
                album_name="Album A",
                album_release_date="2020-01-01",
                album_track_number=3,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Track 1",
                album_name="Album A",
                album_release_date="2020-01-01",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v3",
                set_video_id="s3",
                title="Track 2",
                album_name="Album A",
                album_release_date="2020-01-01",
                album_track_number=2,
            ),
        ]
        levels = [
            SortLevel(
                attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.ASC
            ),
            SortLevel(
                attribute=SortAttribute.TRACK_NUMBER, direction=SortDirection.ASC
            ),
        ]
        context = SortContext()

        result = multi_level_sort(tracks, levels, context)

        assert result[0].title == "Track 1"
        assert result[1].title == "Track 2"
        assert result[2].title == "Track 3"

    def test_empty_list(self):
        """Empty track list returns empty list."""
        levels = [SortLevel(attribute=SortAttribute.ARTIST_NAME)]
        result = multi_level_sort([], levels, SortContext())
        assert result == []

    def test_empty_levels(self, sample_tracks: list[TrackForSorting]):
        """Empty levels list returns tracks unchanged."""
        result = multi_level_sort(sample_tracks, [], SortContext())
        assert result == sample_tracks


class TestFavouriteArtistsSorting:
    """Tests for favourite artists sorting."""

    def test_favourites_first(self, sample_tracks: list[TrackForSorting]):
        """Favourite artists appear first by rank."""
        levels = [
            SortLevel(
                attribute=SortAttribute.FAVOURITE_ARTISTS, direction=SortDirection.ASC
            ),
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
        ]
        context = SortContext(artist_rankings={"Artist C": 0, "Artist A": 1})

        result = multi_level_sort(sample_tracks, levels, context)

        # Favourites first by rank
        assert result[0].artist_name == "Artist C"  # rank 0
        assert result[1].artist_name == "Artist A"  # rank 1
        # Non-favourites sorted alphabetically
        assert result[2].artist_name == "Artist B"
        assert result[3].artist_name == "Artist D"

    def test_case_insensitive_matching(self):
        """Artist matching is case-insensitive."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Track 1",
                artist_name="METALLICA",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Track 2",
                artist_name="queen",
                album_track_number=1,
            ),
        ]
        levels = [SortLevel(attribute=SortAttribute.FAVOURITE_ARTISTS)]
        context = SortContext(artist_rankings={"Queen": 0, "metallica": 1})

        result = multi_level_sort(tracks, levels, context)

        assert result[0].artist_name == "queen"  # rank 0
        assert result[1].artist_name == "METALLICA"  # rank 1

    def test_no_favourites_falls_back(self, sample_tracks: list[TrackForSorting]):
        """Without favourites, sorting continues to next level."""
        levels = [
            SortLevel(attribute=SortAttribute.FAVOURITE_ARTISTS),
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
        ]
        context = SortContext(artist_rankings={})  # No favourites

        result = multi_level_sort(sample_tracks, levels, context)

        # All have inf rank, so fall through to artist name
        assert result[0].artist_name == "Artist A"
        assert result[1].artist_name == "Artist B"
        assert result[2].artist_name == "Artist C"
        assert result[3].artist_name == "Artist D"


class TestPresets:
    """Tests for preset configurations."""

    def test_preset_discography(self):
        """Discography preset: Artist A-Z → Album Date oldest → Track #."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Track 2",
                artist_name="Artist A",
                album_release_date="2020-01-01",
                album_track_number=2,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Track 1",
                artist_name="Artist A",
                album_release_date="2020-01-01",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v3",
                set_video_id="s3",
                title="Old Track",
                artist_name="Artist A",
                album_release_date="2010-01-01",
                album_track_number=1,
            ),
        ]

        result = multi_level_sort(tracks, PRESET_DISCOGRAPHY, SortContext())

        assert result[0].title == "Old Track"  # 2010
        assert result[1].title == "Track 1"  # 2020, track 1
        assert result[2].title == "Track 2"  # 2020, track 2

    def test_preset_latest_releases(self):
        """Latest releases preset: Album Date newest → Track #."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Old",
                album_release_date="2010-01-01",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="New",
                album_release_date="2023-01-01",
                album_track_number=1,
            ),
        ]

        result = multi_level_sort(tracks, PRESET_LATEST_RELEASES, SortContext())

        assert result[0].title == "New"  # 2023
        assert result[1].title == "Old"  # 2010

    def test_preset_favourites_first(self):
        """Favourites first preset works with rankings."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Non-Fav",
                artist_name="Unknown",
                album_release_date="2020-01-01",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Favourite",
                artist_name="Queen",
                album_release_date="2020-01-01",
                album_track_number=1,
            ),
        ]
        context = SortContext(artist_rankings={"Queen": 0})

        result = multi_level_sort(tracks, PRESET_FAVOURITES_FIRST, context)

        assert result[0].title == "Favourite"
        assert result[1].title == "Non-Fav"


class TestTitleSorting:
    """Tests for title sorting."""

    def test_sort_by_title_asc(self):
        """Sort by title ascending (A-Z)."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Zebra",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Apple",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v3",
                set_video_id="s3",
                title="Mango",
                album_track_number=1,
            ),
        ]
        levels = [SortLevel(attribute=SortAttribute.TITLE, direction=SortDirection.ASC)]
        context = SortContext()

        result = multi_level_sort(tracks, levels, context)

        assert result[0].title == "Apple"
        assert result[1].title == "Mango"
        assert result[2].title == "Zebra"

    def test_sort_by_title_desc(self):
        """Sort by title descending (Z-A)."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Apple",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Zebra",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v3",
                set_video_id="s3",
                title="Mango",
                album_track_number=1,
            ),
        ]
        levels = [
            SortLevel(attribute=SortAttribute.TITLE, direction=SortDirection.DESC)
        ]
        context = SortContext()

        result = multi_level_sort(tracks, levels, context)

        assert result[0].title == "Zebra"
        assert result[1].title == "Mango"
        assert result[2].title == "Apple"

    def test_title_case_insensitive(self):
        """Title sorting is case-insensitive."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="BANANA",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="apple",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v3",
                set_video_id="s3",
                title="Cherry",
                album_track_number=1,
            ),
        ]
        levels = [SortLevel(attribute=SortAttribute.TITLE, direction=SortDirection.ASC)]
        context = SortContext()

        result = multi_level_sort(tracks, levels, context)

        assert result[0].title == "apple"
        assert result[1].title == "BANANA"
        assert result[2].title == "Cherry"

    def test_multi_level_artist_then_title(self):
        """Multi-level: Artist A-Z, then Title A-Z."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Song B",
                artist_name="Artist A",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Song A",
                artist_name="Artist A",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v3",
                set_video_id="s3",
                title="Song C",
                artist_name="Artist B",
                album_track_number=1,
            ),
        ]
        levels = [
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.TITLE, direction=SortDirection.ASC),
        ]
        context = SortContext()

        result = multi_level_sort(tracks, levels, context)

        # Artist A first, then by title
        assert result[0].title == "Song A"  # Artist A
        assert result[1].title == "Song B"  # Artist A
        assert result[2].title == "Song C"  # Artist B

    def test_empty_title_handled(self):
        """Empty titles are handled gracefully."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="",
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Actual Title",
                album_track_number=1,
            ),
        ]
        levels = [SortLevel(attribute=SortAttribute.TITLE, direction=SortDirection.ASC)]
        context = SortContext()

        result = multi_level_sort(tracks, levels, context)

        # Empty string sorts before "Actual Title"
        assert result[0].title == ""
        assert result[1].title == "Actual Title"


class TestDurationSorting:
    """Tests for duration sorting."""

    def test_sort_by_duration_asc(self):
        """Sort by duration ascending (shortest first)."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Long Song",
                duration_ms=300000,  # 5 minutes
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Short Song",
                duration_ms=120000,  # 2 minutes
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v3",
                set_video_id="s3",
                title="Medium Song",
                duration_ms=210000,  # 3.5 minutes
                album_track_number=1,
            ),
        ]
        levels = [
            SortLevel(attribute=SortAttribute.DURATION, direction=SortDirection.ASC)
        ]
        context = SortContext()

        result = multi_level_sort(tracks, levels, context)

        assert result[0].title == "Short Song"  # 2 min
        assert result[1].title == "Medium Song"  # 3.5 min
        assert result[2].title == "Long Song"  # 5 min

    def test_sort_by_duration_desc(self):
        """Sort by duration descending (longest first)."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Short Song",
                duration_ms=120000,
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Long Song",
                duration_ms=300000,
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v3",
                set_video_id="s3",
                title="Medium Song",
                duration_ms=210000,
                album_track_number=1,
            ),
        ]
        levels = [
            SortLevel(attribute=SortAttribute.DURATION, direction=SortDirection.DESC)
        ]
        context = SortContext()

        result = multi_level_sort(tracks, levels, context)

        assert result[0].title == "Long Song"  # 5 min
        assert result[1].title == "Medium Song"  # 3.5 min
        assert result[2].title == "Short Song"  # 2 min

    def test_null_duration_goes_to_end(self):
        """Tracks without duration go to end."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="No Duration",
                duration_ms=None,
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Has Duration",
                duration_ms=180000,
                album_track_number=1,
            ),
        ]
        levels = [
            SortLevel(attribute=SortAttribute.DURATION, direction=SortDirection.ASC)
        ]
        context = SortContext()

        result = multi_level_sort(tracks, levels, context)

        assert result[0].title == "Has Duration"
        assert result[1].title == "No Duration"

    def test_multi_level_artist_then_duration(self):
        """Multi-level: Artist A-Z, then Duration shortest first."""
        tracks = [
            TrackForSorting(
                video_id="v1",
                set_video_id="s1",
                title="Long A",
                artist_name="Artist A",
                duration_ms=300000,
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v2",
                set_video_id="s2",
                title="Short A",
                artist_name="Artist A",
                duration_ms=120000,
                album_track_number=1,
            ),
            TrackForSorting(
                video_id="v3",
                set_video_id="s3",
                title="Song B",
                artist_name="Artist B",
                duration_ms=180000,
                album_track_number=1,
            ),
        ]
        levels = [
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.DURATION, direction=SortDirection.ASC),
        ]
        context = SortContext()

        result = multi_level_sort(tracks, levels, context)

        # Artist A first, then by duration
        assert result[0].title == "Short A"  # Artist A, 2 min
        assert result[1].title == "Long A"  # Artist A, 5 min
        assert result[2].title == "Song B"  # Artist B
