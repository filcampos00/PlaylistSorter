"""YouTube Music service using ytmusicapi."""

import json
import re

from ytmusicapi import YTMusic

from ..common.schemas import Playlist
from ..common.sorting import SortContext, SortStrategy, TrackForSorting
from ..common.utils import sanitize_cookie, is_valid_origin

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

    def get_playlist_tracks(self, playlist_id: str) -> list[TrackForSorting]:
        """Fetch tracks from playlist and enrich with album release dates and track order."""
        raw = self._client.get_playlist(playlist_id, limit=None)
        raw_tracks = raw.get("tracks", [])
        album_data = self._fetch_album_data(raw_tracks)

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
                )
            )

        print(f"[DEBUG] Processed {len(tracks)} tracks from {len(album_data)} albums")
        return tracks

    def _fetch_album_data(self, tracks: list) -> dict[str, dict]:
        """Batch fetch album info. Returns {album_id: {date, track_order_by_id, track_order_by_title}}."""
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
        for album_id in album_ids:
            try:
                album = self._client.get_album(album_id)

                # Get release date from first track's upload date (most reliable)
                release_date = None
                source = "Track Fallback"
                album_tracks = album.get("tracks", [])
                if album_tracks and album_tracks[0].get("videoId"):
                    try:
                        song = self._client.get_song(album_tracks[0]["videoId"])
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
                    source = "Year Only"

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

                album_data[album_id] = {
                    "date": release_date,
                    "track_order_by_id": track_order_by_id,
                    "track_order_by_title": track_order_by_title,
                }

                count_in_playlist = playlist_album_counts.get(album_id, 0)
                print(
                    f"[DEBUG] Album: {album.get('title', 'unknown'):<30} | Date: {release_date} | Source: {source:<15} | Tracks: {count_in_playlist}"
                )
            except Exception as e:
                print(f"[DEBUG] Failed to fetch album {album_id}: {e}")
                pass
        return album_data

    def sort_playlist(
        self, playlist_id: str, strategy: SortStrategy, context: SortContext
    ) -> int:
        """Sort playlist using injected strategy."""
        tracks = self.get_playlist_tracks(playlist_id)
        if not tracks:
            return 0
        sorted_tracks = strategy.sort(tracks, context)
        return self._apply_sorted_order(playlist_id, tracks, sorted_tracks)

    def _apply_sorted_order(
        self,
        playlist_id: str,
        original: list[TrackForSorting],
        sorted_tracks: list[TrackForSorting],
    ) -> int:
        """Remove all tracks and re-add in sorted order (same playlist).

        If add fails after remove, attempts to restore original tracks.
        """
        # Remove all tracks
        self._client.remove_playlist_items(
            playlist_id,
            [{"videoId": t.video_id, "setVideoId": t.set_video_id} for t in original],
        )

        # Try to add sorted tracks
        try:
            self._client.add_playlist_items(
                playlist_id, [t.video_id for t in sorted_tracks], duplicates=True
            )
            return len(sorted_tracks)
        except Exception as add_error:
            # Add failed - try to restore original tracks
            try:
                self._client.add_playlist_items(
                    playlist_id, [t.video_id for t in original], duplicates=True
                )
                raise ValueError(
                    f"Sort failed, original tracks restored. Error: {add_error}"
                )
            except Exception as restore_error:
                raise ValueError(
                    f"CRITICAL: Sort failed and restore failed! "
                    f"Original error: {add_error}, Restore error: {restore_error}"
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
