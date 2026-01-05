"""Unit tests for YouTubeService."""

import pytest
from unittest.mock import patch
from app.youtube.service import YouTubeService

@pytest.fixture
def mock_yt_client():
    with patch("app.youtube.service.YTMusic") as mock:
        yield mock.return_value

@pytest.fixture
def service(mock_yt_client):
    # Pass valid-looking headers to bypass validation
    valid_headers = "Cookie: SID=123\nAuthorization: SAPISID"
    return YouTubeService(valid_headers)

class TestFetchAlbumData:
    """Tests for _fetch_album_data logic."""

    def test_fetch_album_with_track_fallback(self, service, mock_yt_client):
        """Test fallback to fetching track uploadDate when album date is missing."""
        
        # Mock input tracks
        tracks = [{"album": {"id": "alb1"}, "videoId": "v1"}]
        
        # Mock get_album response (no releaseDate, no description)
        mock_yt_client.get_album.return_value = {
            "title": "Test Album",
            "year": "2025",
            "tracks": [{"videoId": "v1", "title": "Song 1"}]
        }
        
        # Mock get_song response (contains uploadDate)
        mock_yt_client.get_song.return_value = {
            "microformat": {
                "microformatDataRenderer": {
                    "uploadDate": "2025-03-10"
                }
            }
        }
        
        album_data = service._fetch_album_data(tracks)
        
        # Verify fallback worked
        assert album_data["alb1"]["date"] == "2025-03-10"
        # Verify get_song was called
        mock_yt_client.get_song.assert_called_with("v1")

    def test_fetch_album_year_fallback(self, service, mock_yt_client):
        """Test fallback to Year-01-01 when even track fallback fails."""
        
        tracks = [{"album": {"id": "alb2"}, "videoId": "v2"}]
        
        # Mock album (no date)
        mock_yt_client.get_album.return_value = {
            "title": "Year Album",
            "year": "1999",
            "tracks": [{"videoId": "v2", "title": "Song A"}]
        }
        
        # Mock get_song failure (raises exception)
        mock_yt_client.get_song.side_effect = Exception("Song fetch failed")
        
        album_data = service._fetch_album_data(tracks)
        
        # Verify fallback to year
        assert album_data["alb2"]["date"] == "1999-01-01"


