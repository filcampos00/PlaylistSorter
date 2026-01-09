"""YouTube Music API routes (controller)."""

import logging

from fastapi import APIRouter, Depends

from ..common.schemas import (
    AuthTestResponse,
    PlaylistsResponse,
    ShuffleRequest,
    SortRequest,
    SortResponse,
)
from ..common.sorting import SortAttribute, SortContext
from .dependencies import get_youtube_service
from .service import YouTubeService

router = APIRouter(prefix="/youtube", tags=["YouTube Music"])
logger = logging.getLogger(__name__)


@router.post("/auth/test", response_model=AuthTestResponse)
async def test_auth(youtube: YouTubeService = Depends(get_youtube_service)):
    """
    Test if the provided browser headers are valid for YouTube Music.
    Returns the channel name if successful.
    """
    try:
        account_info = youtube.get_account_info()
        channel_name = account_info.get("channelHandle", "Unknown")

        return AuthTestResponse(
            success=True,
            message="Authentication successful",
            channel_name=channel_name,
        )
    except Exception as e:
        # Log the full error for debugging
        logger.error(f"Error during authentication: {str(e)}")
        # Return a friendly message to the user
        return AuthTestResponse(
            success=False,
            message="Authentication failed. Please follow the instructions below.",
            channel_name=None,
        )


@router.post("/playlists", response_model=PlaylistsResponse)
async def get_playlists(youtube: YouTubeService = Depends(get_youtube_service)):
    """
    Fetch user's YouTube Music playlists.
    Requires valid browser headers.
    """
    try:
        playlists = youtube.get_library_playlists(limit=50)

        return PlaylistsResponse(
            success=True,
            message=f"Found {len(playlists)} playlists",
            playlists=playlists,
        )
    except ValueError as e:
        return PlaylistsResponse(
            success=False,
            message=str(e),
            playlists=[],
        )
    except Exception as e:
        return PlaylistsResponse(
            success=False,
            message=f"Failed to fetch playlists: {str(e)}",
            playlists=[],
        )


@router.post("/playlists/{playlist_id}/sort", response_model=SortResponse)
async def sort_playlist(
    playlist_id: str,
    payload: SortRequest,
):
    """
    Sort a playlist by the specified criteria using multi-level sorting.

    Args:
        playlist_id: The ID of the playlist to sort.
        payload: Request body containing headers, sort_levels, and optional favourite_artists.
    """
    try:
        # Create YouTube service from headers
        youtube = YouTubeService(payload.headers_raw)

        # Build artist rankings from favourite_artists list
        # Lower rank = higher priority (appears first)
        artist_rankings = {
            artist: idx for idx, artist in enumerate(payload.favourite_artists)
        }

        # Only populate rankings if favourite_artists is used in sort_levels
        has_favourites_level = any(
            level.attribute == SortAttribute.FAVOURITE_ARTISTS
            for level in payload.sort_levels
        )
        context = SortContext(
            artist_rankings=artist_rankings if has_favourites_level else {},
        )

        count = await youtube.sort_playlist(playlist_id, payload.sort_levels, context)

        # Build user-friendly message
        if count == 0:
            message = "Playlist is already sorted"
        else:
            # Describe sort levels
            level_names = [
                level.attribute.value.replace("_", " ") for level in payload.sort_levels
            ]
            if len(level_names) == 1:
                sort_desc = level_names[0]
            else:
                sort_desc = f"{level_names[0]} (then {', '.join(level_names[1:])})"
            message = f"Sorted {count} tracks by {sort_desc}"

        return SortResponse(
            success=True,
            message=message,
            tracks_reordered=count,
        )
    except ValueError as e:
        return SortResponse(success=False, message=str(e))
    except Exception as e:
        return SortResponse(success=False, message=f"Failed to sort playlist: {str(e)}")


@router.post("/playlists/{playlist_id}/shuffle", response_model=SortResponse)
async def shuffle_playlist(
    playlist_id: str,
    payload: ShuffleRequest,
):
    """
    Shuffle playlist tracks in random order.

    Args:
        playlist_id: The ID of the playlist to shuffle.
        payload: Request body containing headers.
    """
    try:
        youtube = YouTubeService(payload.headers_raw)
        count = await youtube.shuffle_playlist(playlist_id)

        if count == 0:
            message = "Playlist has no tracks to shuffle"
        else:
            message = f"Shuffled {count} tracks"

        return SortResponse(
            success=True,
            message=message,
            tracks_reordered=count,
        )
    except ValueError as e:
        return SortResponse(success=False, message=str(e))
    except Exception as e:
        return SortResponse(
            success=False, message=f"Failed to shuffle playlist: {str(e)}"
        )
