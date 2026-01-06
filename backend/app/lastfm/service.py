"""Last.fm API service for fetching user top artists."""

import os
import logging
from typing import Optional

import httpx

from .schemas import LastFmPeriod


logger = logging.getLogger(__name__)

LASTFM_API_URL = "https://ws.audioscrobbler.com/2.0/"


class LastFmService:
    """Service class for Last.fm API operations."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Last.fm service.

        Args:
            api_key: Last.fm API key. If not provided, reads from LASTFM_API_KEY env var.

        Raises:
            ValueError: If no API key is available.
        """
        self.api_key = api_key or os.getenv("LASTFM_API_KEY")
        if not self.api_key:
            raise ValueError("LASTFM_API_KEY not configured")

    async def get_top_artists(
        self,
        username: str,
        period: LastFmPeriod = LastFmPeriod.OVERALL,
        limit: int = 50,
    ) -> list[str]:
        """
        Fetch a user's top artists from Last.fm.

        Args:
            username: Last.fm username.
            period: Time period for top artists (e.g., overall, 12month, 7day).
            limit: Maximum number of artists to return (1-1000).

        Returns:
            List of artist names (strings).

        Raises:
            ValueError: If username not found or API error occurs.
        """
        params = {
            "method": "user.getTopArtists",
            "user": username,
            "api_key": self.api_key,
            "format": "json",
            "period": period.value,
            "limit": min(max(1, limit), 1000),  # Clamp to valid range
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(LASTFM_API_URL, params=params)
                data = response.json()

                # Check for API errors
                if "error" in data:
                    error_code = data.get("error")
                    error_msg = data.get("message", "Unknown error")

                    if error_code == 6:  # User not found
                        raise ValueError(f"Last.fm user '{username}' not found")
                    else:
                        raise ValueError(f"Last.fm API error: {error_msg}")

                # Extract artist names
                top_artists = data.get("topartists", {}).get("artist", [])
                artist_names = [artist["name"] for artist in top_artists]

                logger.info(
                    f"Fetched {len(artist_names)} top artists for user '{username}' "
                    f"(period: {period.value})"
                )

                return artist_names

            except httpx.TimeoutException:
                raise ValueError("Last.fm API request timed out")
            except httpx.RequestError as e:
                raise ValueError(f"Failed to connect to Last.fm: {e}")
