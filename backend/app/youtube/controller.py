"""YouTube Music API routes (controller)."""

from fastapi import APIRouter, Depends

from ..common.schemas import AuthTestResponse, PlaylistsResponse, SortResponse
from ..common.sorting import SortContext, SortOption
from .dependencies import get_youtube_service, get_strategy, get_sort_context
from .service import YouTubeService

router = APIRouter(prefix="/youtube", tags=["YouTube Music"])


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
        print(f"Error during authentication: {str(e)}")
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
    sort_by: SortOption,
    youtube: YouTubeService = Depends(get_youtube_service),
    context: SortContext = Depends(get_sort_context),
):
    """
    Sort a playlist by the specified criteria.

    Args:
        playlist_id: The ID of the playlist to sort.
        sort_by: The sorting option (e.g., album_release_date_asc).
    """
    try:
        strategy = get_strategy(sort_by)
        count = youtube.sort_playlist(playlist_id, strategy, context)
        return SortResponse(
            success=True,
            message=f"Sorted {count} tracks by {sort_by.value}",
            tracks_reordered=count,
        )
    except ValueError as e:
        return SortResponse(success=False, message=str(e))
    except Exception as e:
        return SortResponse(success=False, message=f"Failed to sort playlist: {str(e)}")
