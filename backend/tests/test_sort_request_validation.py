"""Unit tests for SortRequest validation rules."""

import pytest
from pydantic import ValidationError

from app.common.schemas import SortRequest
from app.common.sorting import SortAttribute, SortLevel


class TestSortRequestValidation:
    """Tests for sort level compatibility validation."""

    def test_valid_discography_order(self):
        """Artist → Album Date → Track Number is valid."""
        request = SortRequest(
            headers_raw="Cookie: test=value",
            sort_levels=[
                SortLevel(attribute=SortAttribute.ARTIST_NAME),
                SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE),
                SortLevel(attribute=SortAttribute.TRACK_NUMBER),
            ],
        )
        assert len(request.sort_levels) == 3

    def test_valid_latest_releases(self):
        """Album Date → Track Number is valid."""
        request = SortRequest(
            headers_raw="Cookie: test=value",
            sort_levels=[
                SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE),
                SortLevel(attribute=SortAttribute.TRACK_NUMBER),
            ],
        )
        assert len(request.sort_levels) == 2

    def test_valid_album_name_then_track(self):
        """Album Name → Track Number is valid."""
        request = SortRequest(
            headers_raw="Cookie: test=value",
            sort_levels=[
                SortLevel(attribute=SortAttribute.ALBUM_NAME),
                SortLevel(attribute=SortAttribute.TRACK_NUMBER),
            ],
        )
        assert len(request.sort_levels) == 2

    def test_valid_favourites_first(self):
        """Favourite Artists → Artist → Album Date → Track is valid."""
        request = SortRequest(
            headers_raw="Cookie: test=value",
            sort_levels=[
                SortLevel(attribute=SortAttribute.FAVOURITE_ARTISTS),
                SortLevel(attribute=SortAttribute.ARTIST_NAME),
                SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE),
                SortLevel(attribute=SortAttribute.TRACK_NUMBER),
            ],
        )
        assert len(request.sort_levels) == 4

    def test_invalid_track_number_alone(self):
        """Track Number alone (no album context) is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            SortRequest(
                headers_raw="Cookie: test=value",
                sort_levels=[
                    SortLevel(attribute=SortAttribute.TRACK_NUMBER),
                ],
            )
        assert "requires Album Name or Album Release Date" in str(exc_info.value)

    def test_invalid_track_number_before_album(self):
        """Artist → Track Number (no album context) is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            SortRequest(
                headers_raw="Cookie: test=value",
                sort_levels=[
                    SortLevel(attribute=SortAttribute.ARTIST_NAME),
                    SortLevel(attribute=SortAttribute.TRACK_NUMBER),
                ],
            )
        assert "requires Album Name or Album Release Date" in str(exc_info.value)

    def test_invalid_album_after_track_number(self):
        """Album Date → Track → Album Name is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            SortRequest(
                headers_raw="Cookie: test=value",
                sort_levels=[
                    SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE),
                    SortLevel(attribute=SortAttribute.TRACK_NUMBER),
                    SortLevel(attribute=SortAttribute.ALBUM_NAME),
                ],
            )
        assert "cannot appear after Track Number" in str(exc_info.value)

    def test_invalid_album_release_date_after_track(self):
        """Album Name → Track → Album Release Date is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            SortRequest(
                headers_raw="Cookie: test=value",
                sort_levels=[
                    SortLevel(attribute=SortAttribute.ALBUM_NAME),
                    SortLevel(attribute=SortAttribute.TRACK_NUMBER),
                    SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE),
                ],
            )
        assert "cannot appear after Track Number" in str(exc_info.value)

    def test_invalid_duplicate_attributes(self):
        """Duplicate attributes are invalid."""
        with pytest.raises(ValidationError) as exc_info:
            SortRequest(
                headers_raw="Cookie: test=value",
                sort_levels=[
                    SortLevel(attribute=SortAttribute.ARTIST_NAME),
                    SortLevel(attribute=SortAttribute.ARTIST_NAME),
                ],
            )
        assert "Duplicate sort attribute" in str(exc_info.value)

    def test_invalid_favourites_not_first(self):
        """Favourite Artists not at L1 is invalid (must be first)."""
        with pytest.raises(ValidationError) as exc_info:
            SortRequest(
                headers_raw="Cookie: test=value",
                sort_levels=[
                    SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE),
                    SortLevel(attribute=SortAttribute.FAVOURITE_ARTISTS),
                    SortLevel(attribute=SortAttribute.TRACK_NUMBER),
                ],
            )
        assert "must be the first sort level" in str(exc_info.value)

    def test_valid_both_album_attributes(self):
        """Album Name + Album Release Date together is valid."""
        request = SortRequest(
            headers_raw="Cookie: test=value",
            sort_levels=[
                SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE),
                SortLevel(attribute=SortAttribute.ALBUM_NAME),
                SortLevel(attribute=SortAttribute.TRACK_NUMBER),
            ],
        )
        assert len(request.sort_levels) == 3

    def test_valid_single_level_artist(self):
        """Single level Artist Name is valid."""
        request = SortRequest(
            headers_raw="Cookie: test=value",
            sort_levels=[
                SortLevel(attribute=SortAttribute.ARTIST_NAME),
            ],
        )
        assert len(request.sort_levels) == 1

    def test_valid_single_level_album_date(self):
        """Single level Album Release Date is valid."""
        request = SortRequest(
            headers_raw="Cookie: test=value",
            sort_levels=[
                SortLevel(attribute=SortAttribute.ALBUM_RELEASE_DATE),
            ],
        )
        assert len(request.sort_levels) == 1

    def test_invalid_empty_levels(self):
        """Empty sort_levels is invalid."""
        with pytest.raises(ValidationError):
            SortRequest(
                headers_raw="Cookie: test=value",
                sort_levels=[],
            )
