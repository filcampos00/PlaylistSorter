"""
POC: Sorting Combination Analysis

This test module uses a realistic 20-song sample playlist to empirically
evaluate all possible sorting combinations and depth levels.

Goals:
1. Determine the maximum useful sorting depth
2. Identify valid, invalid, and unusual combinations
3. Document expected behavior for each scenario
"""

import pytest
from itertools import permutations
from typing import NamedTuple

from pydantic import ValidationError

from app.common.schemas import SortRequest
from app.common.sorting.schemas import (
    SortAttribute,
    SortDirection,
    SortLevel,
    TrackForSorting,
)
from app.common.sorting.strategies import (
    SortContext,
    multi_level_sort,
)


class TrackData(NamedTuple):
    """Helper for defining tracks concisely."""
    video_id: str
    title: str
    artist: str
    album: str
    date: str | None
    track_num: int
    duration_ms: int


# Realistic 20-song playlist with INTENTIONAL COLLISIONS for stress-testing:
# - Duplicate titles (covers, "Intro" tracks, compilation appearances)
# - Same release dates (Friday releases, same album)
# - Identical durations
# - Same artist on different albums with same track numbers
SAMPLE_PLAYLIST_DATA = [
    # === DUPLICATE TITLES ===
    # "Intro" - extremely common duplicate
    TrackData("v01", "Intro", "The Weeknd", "After Hours", "2020-03-20", 1, 60000),
    TrackData("v02", "Intro", "Bruno Mars", "24K Magic", "2016-11-18", 1, 45000),
    TrackData("v03", "Intro", "Queen", "A Night at the Opera", "1975-11-21", 1, 30000),

    # "Bohemian Rhapsody" - original + cover
    TrackData("v04", "Bohemian Rhapsody", "Queen", "A Night at the Opera", "1975-11-21", 11, 354000),
    TrackData("v05", "Bohemian Rhapsody", "Panic! At The Disco", "Bohemian Rhapsody OST", "2018-10-19", 1, 354000),  # Same duration!

    # === SAME RELEASE DATE (Friday drops) ===
    # 2016-11-18 - Bruno Mars AND The Weeknd released same day
    TrackData("v06", "24K Magic", "Bruno Mars", "24K Magic", "2016-11-18", 2, 226000),
    TrackData("v07", "Starboy", "The Weeknd", "Starboy", "2016-11-18", 1, 230000),  # Same day as Bruno!
    TrackData("v08", "I Feel It Coming", "The Weeknd", "Starboy", "2016-11-18", 18, 269000),

    # === SAME ARTIST, MULTIPLE ALBUMS, SAME TRACK NUMBERS ===
    TrackData("v09", "We Will Rock You", "Queen", "News of the World", "1977-10-28", 1, 122000),  # Track 1
    TrackData("v10", "Somebody to Love", "Queen", "A Day at the Races", "1976-12-10", 1, 298000),  # Track 1!
    TrackData("v11", "We Are the Champions", "Queen", "News of the World", "1977-10-28", 2, 179000),

    # === COMPILATION APPEARANCES (same song, different albums) ===
    TrackData("v12", "Blinding Lights", "The Weeknd", "After Hours", "2020-03-20", 9, 200000),
    TrackData("v13", "Blinding Lights", "The Weeknd", "The Highlights", "2021-02-05", 2, 200000),  # Best-of!

    # === IDENTICAL DURATIONS ===
    TrackData("v14", "Save Your Tears", "The Weeknd", "After Hours", "2020-03-20", 6, 215000),
    TrackData("v15", "In Your Eyes", "The Weeknd", "After Hours", "2020-03-20", 7, 215000),  # Same duration!

    # === Edge cases ===
    TrackData("v16", "Uptown Funk", "Bruno Mars", "Uptown Special", "2015-01-13", 4, 270000),
    TrackData("v17", "That's What I Like", "Bruno Mars", "24K Magic", "2016-11-18", 3, 206000),
    TrackData("v18", "Mystery Song", "Unknown Artist", None, None, 1, 180000),  # Missing album/date
    TrackData("v19", "Love of My Life", "Queen", "A Night at the Opera", "1975-11-21", 9, 219000),
    TrackData("v20", "Finesse", "Bruno Mars", "24K Magic", "2016-11-18", 9, 191000),
]


@pytest.fixture
def sample_playlist() -> list[TrackForSorting]:
    """Convert sample data to TrackForSorting objects."""
    return [
        TrackForSorting(
            video_id=t.video_id,
            set_video_id=f"set_{t.video_id}",
            title=t.title,
            artist_name=t.artist,
            album_name=t.album,
            album_release_date=t.date,
            album_track_number=t.track_num,
            duration_ms=t.duration_ms,
        )
        for t in SAMPLE_PLAYLIST_DATA
    ]


class TestDepthLevelAnalysis:
    """Analyze how many depth levels are meaningful."""

    def test_depth_1_title_has_collisions(self, sample_playlist):
        """Level 1: Title alone does NOT give unique order - we have duplicates!"""
        levels = [SortLevel(attribute=SortAttribute.TITLE, direction=SortDirection.ASC)]
        result = multi_level_sort(sample_playlist, levels, SortContext())

        # First result is "24K Magic" (alphabetically)
        assert result[0].title == "24K Magic"
        # But we have MULTIPLE "Intro" and "Blinding Lights" and "Bohemian Rhapsody"
        intro_tracks = [t for t in result if t.title == "Intro"]
        assert len(intro_tracks) == 3, "Should have 3 duplicate 'Intro' tracks"

    def test_depth_1_artist_creates_ties(self, sample_playlist):
        """Level 1: Artist alone creates ties (multiple tracks per artist)."""
        levels = [SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC)]
        result = multi_level_sort(sample_playlist, levels, SortContext())

        # Bruno Mars first (alphabetically), but order within artist is undefined
        assert result[0].artist_name == "Bruno Mars"
        # Count Bruno Mars tracks in first 5 positions (he has 5 tracks)
        bruno_count = sum(1 for t in result[:5] if t.artist_name == "Bruno Mars")
        assert bruno_count == 5

    def test_depth_2_resolves_artist_ties(self, sample_playlist):
        """Level 2: Artist + Album Date resolves most ties."""
        levels = [
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.ASC),
        ]
        result = multi_level_sort(sample_playlist, levels, SortContext())

        # Bruno Mars tracks should be ordered by album date
        bruno_tracks = [t for t in result if t.artist_name == "Bruno Mars"]
        assert bruno_tracks[0].album_name == "Uptown Special"  # 2015
        # Next 4 are from "24K Magic" (2016)
        assert all(t.album_name == "24K Magic" for t in bruno_tracks[1:])

    def test_depth_3_resolves_album_ties(self, sample_playlist):
        """Level 3: Artist + Album Date + Track # resolves within-album order."""
        levels = [
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.TRACK_NUMBER, direction=SortDirection.ASC),
        ]
        result = multi_level_sort(sample_playlist, levels, SortContext())

        # Find Queen's "A Night at the Opera" tracks
        opera_tracks = [
            t for t in result
            if t.artist_name == "Queen" and t.album_name == "A Night at the Opera"
        ]
        # Should be in track number order: 1, 9, 11
        track_nums = [t.album_track_number for t in opera_tracks]
        assert track_nums == [1, 9, 11]

    def test_depth_4_favourites_discography(self, sample_playlist):
        """Level 4: Favourites + Artist + Album Date + Track # (maximum preset)."""
        levels = [
            SortLevel(attribute=SortAttribute.FAVOURITE_ARTISTS, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.TRACK_NUMBER, direction=SortDirection.ASC),
        ]
        context = SortContext(artist_rankings={"Queen": 0, "Bruno Mars": 1})
        result = multi_level_sort(sample_playlist, levels, context)

        # Queen should be first (favourite rank 0)
        assert result[0].artist_name == "Queen"
        # Bruno Mars second favourite
        queen_count = sum(1 for t in SAMPLE_PLAYLIST_DATA if t.artist == "Queen")
        assert result[queen_count].artist_name == "Bruno Mars"

    def test_depth_4_is_sufficient(self, sample_playlist):
        """Verify 4 levels is sufficient for fully deterministic ordering."""
        levels = [
            SortLevel(attribute=SortAttribute.FAVOURITE_ARTISTS, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.TRACK_NUMBER, direction=SortDirection.ASC),
        ]
        context = SortContext(artist_rankings={"Queen": 0, "Bruno Mars": 1})

        # Sort twice
        result1 = multi_level_sort(sample_playlist, levels, context)
        result2 = multi_level_sort(sample_playlist, levels, context)

        # Order should be exactly the same (deterministic)
        for t1, t2 in zip(result1, result2):
            assert t1.video_id == t2.video_id


class TestInvalidCombinations:
    """Test combinations that should be rejected by validation."""

    @pytest.mark.parametrize("levels,error_match", [
        # Track number without album context
        ([SortLevel(attribute=SortAttribute.TRACK_NUMBER)],
         "requires Album Name or Album Release Date"),

        # Artist -> Track (missing album context)
        ([SortLevel(attribute=SortAttribute.ARTIST_NAME),
          SortLevel(attribute=SortAttribute.TRACK_NUMBER)],
         "requires Album Name or Album Release Date"),

        # Title -> Track (missing album context)
        ([SortLevel(attribute=SortAttribute.TITLE),
          SortLevel(attribute=SortAttribute.TRACK_NUMBER)],
         "requires Album Name or Album Release Date"),

        # Album Date -> Track -> Album Name (album after track)
        ([SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE),
          SortLevel(attribute=SortAttribute.TRACK_NUMBER),
          SortLevel(attribute=SortAttribute.ALBUM_NAME)],
         "cannot appear after Track Number"),

        # Duplicate attributes
        ([SortLevel(attribute=SortAttribute.ARTIST_NAME),
          SortLevel(attribute=SortAttribute.ARTIST_NAME)],
         "Duplicate sort attribute"),

        # Favourites -> Track (missing album context even with favourites)
        ([SortLevel(attribute=SortAttribute.FAVOURITE_ARTISTS),
          SortLevel(attribute=SortAttribute.TRACK_NUMBER)],
         "requires Album Name or Album Release Date"),
    ])
    def test_invalid_combination(self, levels, error_match):
        """Parameterized test for invalid combinations."""
        with pytest.raises(ValidationError) as exc_info:
            SortRequest(
                headers_raw="Cookie: test=value",
                sort_levels=levels,
            )
        assert error_match in str(exc_info.value)


class TestUnusualButValidCombinations:
    """Combinations that work but may be unexpected or unusual."""

    def test_duration_then_artist(self, sample_playlist):
        """Duration first is unusual but valid - groups by song length."""
        levels = [
            SortLevel(attribute=SortAttribute.DURATION, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
        ]
        result = multi_level_sort(sample_playlist, levels, SortContext())

        # Shortest song first (Queen's Intro at 30000ms)
        assert result[0].title == "Intro"
        assert result[0].artist_name == "Queen"

    def test_title_then_album_date_uses_tiebreaker(self, sample_playlist):
        """Title first with album date as tiebreaker - NEEDED for duplicates!"""
        levels = [
            SortLevel(attribute=SortAttribute.TITLE, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.ASC),
        ]
        result = multi_level_sort(sample_playlist, levels, SortContext())

        # With collisions, L2 IS used!
        # "Intro" appears 3 times - should be sorted by date within title
        intro_tracks = [t for t in result if t.title == "Intro"]
        dates = [t.album_release_date for t in intro_tracks]
        assert dates == ["1975-11-21", "2016-11-18", "2020-03-20"], "Intros should be ordered by date"

    def test_both_album_attributes(self, sample_playlist):
        """Album Date + Album Name - used when multiple albums release same day."""
        levels = [
            SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.ALBUM_NAME, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.TRACK_NUMBER, direction=SortDirection.ASC),
        ]
        result = multi_level_sort(sample_playlist, levels, SortContext())

        # 2016-11-18: Bruno Mars "24K Magic" AND The Weeknd "Starboy"
        # Album name breaks the tie (24K < Starboy alphabetically)
        nov_18_tracks = [t for t in result if t.album_release_date == "2016-11-18"]
        assert nov_18_tracks[0].album_name == "24K Magic"


    def test_duplicate_songs_on_compilations(self, sample_playlist):
        """Same song on different albums - needs album context to differentiate."""
        levels = [
            SortLevel(attribute=SortAttribute.TITLE, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.ASC),
        ]
        result = multi_level_sort(sample_playlist, levels, SortContext())

        # "Blinding Lights" appears twice - original and compilation
        blinding = [t for t in result if t.title == "Blinding Lights"]
        assert len(blinding) == 2
        assert blinding[0].album_name == "After Hours"  # 2020 original first
        assert blinding[1].album_name == "The Highlights"  # 2021 compilation


class TestEdgeCases:
    """Edge cases with missing data, nulls, etc."""

    def test_null_album_date_handling(self, sample_playlist):
        """Tracks with null release date go to end."""
        levels = [
            SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.ASC),
        ]
        result = multi_level_sort(sample_playlist, levels, SortContext())

        # "Mystery Song" has null date, should be last
        assert result[-1].title == "Mystery Song"

    def test_null_album_handling(self, sample_playlist):
        """Tracks with null album still sortable."""
        levels = [
            SortLevel(attribute=SortAttribute.ALBUM_NAME, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.TRACK_NUMBER, direction=SortDirection.ASC),
        ]
        result = multi_level_sort(sample_playlist, levels, SortContext())

        # Should not crash - null album track still included
        assert len(result) == 20

    def test_all_same_artist(self):
        """Playlist with single artist - artist level has no effect."""
        tracks = [
            TrackForSorting(
                video_id=f"v{i}",
                set_video_id=f"set_v{i}",
                title=f"Song {i}",
                artist_name="Same Artist",
                album_release_date=f"202{i}-01-01",
                album_track_number=i,
            )
            for i in range(1, 6)
        ]
        levels = [
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE, direction=SortDirection.ASC),
        ]
        result = multi_level_sort(tracks, levels, SortContext())

        # L1 (artist) does nothing, L2 (date) determines order
        assert result[0].album_release_date == "2021-01-01"

    def test_empty_favourites_falls_through(self, sample_playlist):
        """Empty favourites list - all tracks get inf rank, L2 decides."""
        levels = [
            SortLevel(attribute=SortAttribute.FAVOURITE_ARTISTS, direction=SortDirection.ASC),
            SortLevel(attribute=SortAttribute.ARTIST_NAME, direction=SortDirection.ASC),
        ]
        context = SortContext(artist_rankings={})  # No favourites
        result = multi_level_sort(sample_playlist, levels, context)

        # Falls through to artist name (all have same inf rank)
        assert result[0].artist_name == "Bruno Mars"


class TestCombinationMatrix:
    """
    Exhaustive analysis of all 2-level combinations.
    Documents which are valid, invalid, and unusual.
    """

    # All 7 attributes
    ALL_ATTRS = [
        SortAttribute.TITLE,
        SortAttribute.DURATION,
        SortAttribute.ARTIST_NAME,
        SortAttribute.ALBUM_NAME,
        SortAttribute.ALBUM_RELEASE_DATE,
        SortAttribute.TRACK_NUMBER,
        SortAttribute.FAVOURITE_ARTISTS,
    ]

    def test_enumerate_valid_2level_combinations(self):
        """Count and document all valid 2-level combinations."""
        valid_combinations = []
        invalid_combinations = []

        for a1, a2 in permutations(self.ALL_ATTRS, 2):
            try:
                SortRequest(
                    headers_raw="Cookie: test=value",
                    sort_levels=[
                        SortLevel(attribute=a1),
                        SortLevel(attribute=a2),
                    ],
                )
                valid_combinations.append((a1.value, a2.value))
            except ValidationError:
                invalid_combinations.append((a1.value, a2.value))

        # Document the counts
        print(f"\n=== 2-Level Combination Analysis ===")
        print(f"Valid combinations: {len(valid_combinations)}")
        print(f"Invalid combinations: {len(invalid_combinations)}")
        print(f"\nValid:")
        for c in valid_combinations:
            print(f"  {c[0]} → {c[1]}")
        print(f"\nInvalid:")
        for c in invalid_combinations:
            print(f"  {c[0]} → {c[1]}")

        # There are 7 attrs, so 7*6 = 42 permutations of 2
        assert len(valid_combinations) + len(invalid_combinations) == 42

    def test_enumerate_valid_3level_combinations(self):
        """Count valid 3-level combinations (sampling, not exhaustive)."""
        # 7*6*5 = 210 combinations - just sample key ones
        sample_combinations = [
            # The presets
            (SortAttribute.ARTIST_NAME, SortAttribute.ALBUM_RELEASE_DATE, SortAttribute.TRACK_NUMBER),
            (SortAttribute.ALBUM_RELEASE_DATE, SortAttribute.TRACK_NUMBER, SortAttribute.TITLE),
            # Unusual
            (SortAttribute.DURATION, SortAttribute.ALBUM_NAME, SortAttribute.TRACK_NUMBER),
            (SortAttribute.TITLE, SortAttribute.ARTIST_NAME, SortAttribute.ALBUM_NAME),
        ]

        for combo in sample_combinations:
            try:
                SortRequest(
                    headers_raw="Cookie: test=value",
                    sort_levels=[SortLevel(attribute=a) for a in combo],
                )
                print(f"✓ {' → '.join(a.value for a in combo)}")
            except ValidationError as e:
                print(f"✗ {' → '.join(a.value for a in combo)}: {e}")


class TestSortingDepthRecommendations:
    """
    Tests that help determine recommended max depth.
    """

    def test_diminishing_returns_past_4_levels(self, sample_playlist):
        """Adding a 5th level typically has no effect with our attributes."""
        # 4-level sort
        levels_4 = [
            SortLevel(attribute=SortAttribute.FAVOURITE_ARTISTS),
            SortLevel(attribute=SortAttribute.ARTIST_NAME),
            SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE),
            SortLevel(attribute=SortAttribute.TRACK_NUMBER),
        ]
        # Add 5th level (title as final tiebreaker)
        levels_5 = levels_4 + [
            SortLevel(attribute=SortAttribute.TITLE),
        ]

        context = SortContext(artist_rankings={"Queen": 0})
        result_4 = multi_level_sort(sample_playlist, levels_4, context)
        result_5 = multi_level_sort(sample_playlist, levels_5, context)

        # For this dataset, 4 levels is already fully deterministic
        # 5th level changes nothing
        same_order = all(
            r4.video_id == r5.video_id
            for r4, r5 in zip(result_4, result_5)
        )

        # With our sample data, track numbers within same album are unique
        # so title as L5 never breaks any ties
        assert same_order, "5th level should have no effect when 4 levels are deterministic"

    def test_practical_max_depth_is_4(self):
        """Verify that 4 is the practical maximum before hitting all attributes."""
        # With 7 attributes, max theoretical depth is 7
        # But validation rules limit useful combinations

        # These 4-level combinations cover the most practical use cases:
        practical_4_levels = [
            # Favourites First preset (the longest preset)
            [SortAttribute.FAVOURITE_ARTISTS, SortAttribute.ARTIST_NAME,
             SortAttribute.ALBUM_RELEASE_DATE, SortAttribute.TRACK_NUMBER],

            # Alternative with album name instead of date
            [SortAttribute.FAVOURITE_ARTISTS, SortAttribute.ARTIST_NAME,
             SortAttribute.ALBUM_NAME, SortAttribute.TRACK_NUMBER],

            # Title-based sort with full context
            [SortAttribute.TITLE, SortAttribute.ARTIST_NAME,
             SortAttribute.ALBUM_RELEASE_DATE, SortAttribute.DURATION],
        ]

        for combo in practical_4_levels:
            request = SortRequest(
                headers_raw="Cookie: test=value",
                sort_levels=[SortLevel(attribute=a) for a in combo],
            )
            assert len(request.sort_levels) == 4
