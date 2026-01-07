"""YouTube Music service using ytmusicapi."""

import json
import re
import asyncio
import time
import logging

from ytmusicapi import YTMusic

from ..common.schemas import Playlist
from ..common.sorting import SortContext, SortLevel, TrackForSorting, multi_level_sort
from ..common.utils import sanitize_cookie, is_valid_origin


logger = logging.getLogger(__name__)

# YouTube-specific allowed origins
YOUTUBE_ORIGINS = [
    r"^https://music\.youtube\.com$",
    r"^https://www\.youtube\.com$",
    r"^https://youtube\.com$",
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
            raise ValueError(
                "Invalid headers. Make sure you copy the full request headers."
            )

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

    async def get_playlist_tracks(self, playlist_id: str) -> list[TrackForSorting]:
        """Fetch tracks from playlist and enrich with album release dates and track order."""
        # Use asyncio.to_thread for the initial playlist fetch as it's a blocking I/O call
        raw = await asyncio.to_thread(
            self._client.get_playlist, playlist_id, limit=None
        )
        raw_tracks = raw.get("tracks", [])
        album_data = await self._fetch_album_data(raw_tracks)

        tracks = []
        for t in raw_tracks:
            album_id = t.get("album", {}).get("id") if t.get("album") else None
            video_id = t["videoId"]
            track_title = t.get("title", "")
            album_name = t.get("album", {}).get("name") if t.get("album") else None

            # Get album info
            album_info = album_data.get(album_id, {}) if album_id else {}
            release_date = album_info.get("date")

            # Try to find track number: first by videoId, then by title
            track_order_by_id = album_info.get("track_order_by_id", {})
            track_order_by_title = album_info.get("track_order_by_title", {})

            track_number = track_order_by_id.get(video_id)
            if track_number is None:
                # Fallback: match by normalized title
                normalized_title = track_title.strip().lower()
                track_number = track_order_by_title.get(normalized_title, 9999)

            tracks.append(
                TrackForSorting(
                    video_id=video_id,
                    set_video_id=t["setVideoId"],
                    title=track_title,
                    artist_name=t["artists"][0]["name"] if t.get("artists") else None,
                    album_name=album_name,
                    album_release_date=release_date,
                    album_track_number=track_number,
                    duration_ms=t.get("duration_seconds", 0) * 1000
                    if t.get("duration_seconds")
                    else None,
                )
            )

        logger.debug(f"Processed {len(tracks)} tracks from {len(album_data)} albums")
        return tracks

    async def _fetch_album_data(self, tracks: list) -> dict[str, dict]:
        """Batch fetch album info concurrently. Returns {album_id: {date, track_order_by_id, track_order_by_title}}."""
        start_time = time.time()
        album_ids = {
            t.get("album", {}).get("id")
            for t in tracks
            if t.get("album") and t.get("album", {}).get("id")
        }
        # Calculate track counts per album in the current playlist
        playlist_album_counts = {}
        for t in tracks:
            alb = t.get("album", {})
            if alb and alb.get("id"):
                playlist_album_counts[alb["id"]] = (
                    playlist_album_counts.get(alb["id"], 0) + 1
                )

        album_data = {}

        # Limit concurrency to avoid overwhelming the system or API
        sem = asyncio.Semaphore(10)

        async def fetch_single_album(album_id: str):
            async with sem:
                try:
                    # Run the blocking get_album call in a separate thread
                    album = await asyncio.to_thread(self._client.get_album, album_id)

                    # Get release date from first track's upload date (most reliable)
                    release_date = None
                    album_tracks = album.get("tracks", [])
                    if album_tracks and album_tracks[0].get("videoId"):
                        try:
                            # Run the blocking get_song call in a separate thread
                            song = await asyncio.to_thread(
                                self._client.get_song, album_tracks[0]["videoId"]
                            )
                            upload_date = (
                                song.get("microformat", {})
                                .get("microformatDataRenderer", {})
                                .get("uploadDate")
                            )
                            if upload_date:
                                release_date = upload_date.split("T")[0]
                        except Exception:
                            pass

                    # Fallback: Year only
                    if not release_date:
                        year = album.get("year", "9999")
                        release_date = f"{year}-01-01"

                    # Build track order mapping: video_id -> position AND title -> position
                    track_order_by_id = {}
                    track_order_by_title = {}
                    album_tracks = album.get("tracks", [])
                    for idx, track in enumerate(album_tracks, start=1):
                        if track.get("videoId"):
                            track_order_by_id[track["videoId"]] = idx
                        if track.get("title"):
                            # Normalize title for matching (lowercase, strip whitespace)
                            normalized_title = track["title"].strip().lower()
                            track_order_by_title[normalized_title] = idx

                    # This is thread-safe because we're running primarily in the event loop here
                    # effectively only the I/O parts are threaded.
                    album_data[album_id] = {
                        "date": release_date,
                        "track_order_by_id": track_order_by_id,
                        "track_order_by_title": track_order_by_title,
                    }

                    # Get primary artist for logging
                    primary_artist = "Unknown"
                    if album.get("artists"):
                        primary_artist = album["artists"][0].get("name", "Unknown")

                    count_in_playlist = playlist_album_counts.get(album_id, 0)
                    logger.debug(
                        f"Artist: {primary_artist:<20} | Album: {album.get('title', 'unknown'):<30} | Date: {release_date} | Tracks: {count_in_playlist}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to fetch album {album_id}: {e}")
                    pass

        # Execute all fetches concurrently
        await asyncio.gather(*[fetch_single_album(aid) for aid in album_ids])

        elapsed = time.time() - start_time
        logger.info(
            f"[BENCHMARK] Fetched {len(album_ids)} albums in {elapsed:.2f} seconds (Concurrency: 10)"
        )

        return album_data

    async def sort_playlist(
        self,
        playlist_id: str,
        sort_levels: list[SortLevel],
        context: SortContext,
    ) -> int:
        """Sort playlist using multi-level sorting.

        Args:
            playlist_id: ID of the playlist to sort.
            sort_levels: Ordered list of sort levels (primary first).
            context: Context with additional data (e.g., artist rankings).

        Returns:
            Number of tracks reordered (0 if already sorted).
        """
        tracks = await self.get_playlist_tracks(playlist_id)
        if not tracks:
            return 0  # Empty playlist
        sorted_tracks = multi_level_sort(tracks, sort_levels, context)
        return await self._apply_sorted_order(playlist_id, tracks, sorted_tracks)

    async def _apply_sorted_order(
        self,
        playlist_id: str,
        original: list[TrackForSorting],
        sorted_tracks: list[TrackForSorting],
    ) -> int:
        """Apply sorted order. Skips API calls if already sorted.

        Returns:
            Number of tracks reordered (0 if already sorted).

        Compares current order with target order - if identical, returns immediately.
        Otherwise, removes all tracks and re-adds them in sorted order.
        """
        start_total = time.time()

        # Build setVideoId lists for comparison
        current_order = [t.set_video_id for t in original]
        target_order = [t.set_video_id for t in sorted_tracks]

        # Check if already sorted - skip API calls entirely
        if current_order == target_order:
            logger.info(
                "[BENCHMARK] Playlist already sorted - skipping API calls (0 seconds)"
            )
            return 0  # Already sorted - 0 tracks reordered

        # Pre-validate auth before any destructive operation
        # This catches expired tokens BEFORE we remove any tracks
        start_prevalidate = time.time()
        try:
            await asyncio.to_thread(self._client.get_account_info)
            elapsed_prevalidate = time.time() - start_prevalidate
            logger.debug("Auth pre-validation passed")
            logger.info(
                f"[BENCHMARK] Auth pre-validation: {elapsed_prevalidate:.2f} seconds"
            )
        except Exception as auth_error:
            logger.error(f"Auth pre-validation failed: {auth_error}")
            raise ValueError(
                "Your session has expired. Please update your browser headers and try again."
            )

        # Remove all tracks
        start_remove = time.time()
        await asyncio.to_thread(
            self._client.remove_playlist_items,
            playlist_id,
            [{"videoId": t.video_id, "setVideoId": t.set_video_id} for t in original],
        )
        elapsed_remove = time.time() - start_remove
        logger.info(
            f"[BENCHMARK] Removed {len(original)} tracks in {elapsed_remove:.2f} seconds"
        )

        # Try to add sorted tracks
        try:
            start_add = time.time()
            await asyncio.to_thread(
                self._client.add_playlist_items,
                playlist_id,
                [t.video_id for t in sorted_tracks],
                duplicates=True,
            )
            elapsed_add = time.time() - start_add
            logger.info(
                f"[BENCHMARK] Added {len(sorted_tracks)} tracks in {elapsed_add:.2f} seconds"
            )

            elapsed_total = time.time() - start_total
            logger.info(
                f"[BENCHMARK] Total sort application time: {elapsed_total:.2f} seconds"
            )

            return len(sorted_tracks)  # N tracks reordered
        except Exception as add_error:
            # Add failed - try to restore original tracks
            logger.error(f"Failed to add sorted tracks: {add_error}")
            try:
                await asyncio.to_thread(
                    self._client.add_playlist_items,
                    playlist_id,
                    [t.video_id for t in original],
                    duplicates=True,
                )
                # User-friendly message - log the technical details
                logger.error(f"Restore successful after add failure: {add_error}")
                raise ValueError(
                    "YouTube Music rejected the changes. This can happen due to rate limiting "
                    "or sync conflicts. Please wait a moment and try again."
                )
            except Exception as restore_error:
                logger.critical(
                    f"CRITICAL: Sort and restore both failed! "
                    f"Add error: {add_error}, Restore error: {restore_error}"
                )
                raise ValueError(
                    "Something went wrong and we couldn't restore the original order. "
                    "Please check your playlist in YouTube Music."
                )

    def _parse_youtube_headers(self, raw: str) -> dict | None:
        """
        Parse raw HTTP headers for YouTube Music API.
        Extracts and validates YouTube-specific headers.
        """
        # Size limit check
        if len(raw) > 50000:
            return None

        # Remove control characters
        raw = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", raw)

        headers = {}
        lines = raw.strip().split("\n")

        for line in lines:
            # Skip request/response lines
            if line.startswith(("GET ", "POST ", "PUT ", "DELETE ", "PATCH ")):
                continue
            if line.strip().startswith("HTTP/"):
                continue

            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                # Skip overly long values
                if len(value) > 10000:
                    continue

                # Remove control characters from value
                value = re.sub(r"[\x00-\x1f\x7f]", "", value)

                # YouTube-specific header extraction
                if key.lower() == "cookie":
                    headers["Cookie"] = sanitize_cookie(value)
                elif key.lower() == "authorization":
                    headers["Authorization"] = value
                elif key.lower() == "x-goog-authuser":
                    if re.match(r"^\d+$", value):
                        headers["X-Goog-AuthUser"] = value
                elif key.lower() == "x-origin":
                    if is_valid_origin(value, YOUTUBE_ORIGINS):
                        headers["X-Origin"] = value
                elif key.lower() == "origin":
                    if is_valid_origin(value, YOUTUBE_ORIGINS):
                        headers["Origin"] = value

        # Cookie is required for YouTube
        if "Cookie" not in headers:
            return None

        # Set default origin if not present
        if "Origin" not in headers and "X-Origin" not in headers:
            headers["Origin"] = "https://music.youtube.com"

        return headers
