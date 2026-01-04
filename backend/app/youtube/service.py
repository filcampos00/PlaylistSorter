"""YouTube Music service using ytmusicapi."""

import json
import re

from ytmusicapi import YTMusic

from ..common.schemas import Playlist
from ..common.utils import sanitize_cookie, is_valid_origin

# YouTube-specific allowed origins
YOUTUBE_ORIGINS = [
    r'^https://music\.youtube\.com$',
    r'^https://www\.youtube\.com$',
    r'^https://youtube\.com$',
]


class YouTubeService:
    """Service class for YouTube Music operations."""

    def __init__(self, raw_headers: str):
        """
        Initialize YTMusic client with raw browser headers.

        Args:
            raw_headers: Raw HTTP headers copied from browser DevTools.

        Raises:
            ValueError: If headers cannot be parsed or are invalid.
        """
        headers_dict = self._parse_youtube_headers(raw_headers)
        if not headers_dict:
            raise ValueError("Invalid headers. Make sure you copy the full request headers.")

        headers_json = json.dumps(headers_dict)
        self._client = YTMusic(headers_json)

    def get_account_info(self) -> dict:
        """Get the authenticated user's account info."""
        return self._client.get_account_info()

    def get_library_playlists(self, limit: int = 50) -> list[Playlist]:
        """
        Fetch user's library playlists.

        Args:
            limit: Maximum number of playlists to fetch.

        Returns:
            List of Playlist objects.
        """
        raw_playlists = self._client.get_library_playlists(limit=limit)

        playlists = []
        for p in raw_playlists:
            # Get thumbnail URL (use first available size)
            thumbnail_url = None
            if p.get("thumbnails"):
                thumbnail_url = p["thumbnails"][0].get("url")

            playlists.append(
                Playlist(
                    playlist_id=p.get("playlistId", ""),
                    title=p.get("title", "Untitled"),
                    thumbnail_url=thumbnail_url,
                    track_count=p.get("count"),
                )
            )

        return playlists

    def _parse_youtube_headers(self, raw: str) -> dict | None:
        """
        Parse raw HTTP headers for YouTube Music API.
        Extracts and validates YouTube-specific headers.
        """
        # Size limit check
        if len(raw) > 50000:
            return None

        # Remove control characters
        raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw)

        headers = {}
        lines = raw.strip().split('\n')

        for line in lines:
            # Skip request/response lines
            if line.startswith(('GET ', 'POST ', 'PUT ', 'DELETE ', 'PATCH ')):
                continue
            if line.strip().startswith('HTTP/'):
                continue

            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Skip overly long values
                if len(value) > 10000:
                    continue

                # Remove control characters from value
                value = re.sub(r'[\x00-\x1f\x7f]', '', value)

                # YouTube-specific header extraction
                if key.lower() == 'cookie':
                    headers['Cookie'] = sanitize_cookie(value)
                elif key.lower() == 'authorization':
                    headers['Authorization'] = value
                elif key.lower() == 'x-goog-authuser':
                    if re.match(r'^\d+$', value):
                        headers['X-Goog-AuthUser'] = value
                elif key.lower() == 'x-origin':
                    if is_valid_origin(value, YOUTUBE_ORIGINS):
                        headers['X-Origin'] = value
                elif key.lower() == 'origin':
                    if is_valid_origin(value, YOUTUBE_ORIGINS):
                        headers['Origin'] = value

        # Cookie is required for YouTube
        if 'Cookie' not in headers:
            return None

        # Set default origin if not present
        if 'Origin' not in headers and 'X-Origin' not in headers:
            headers['Origin'] = 'https://music.youtube.com'

        return headers
