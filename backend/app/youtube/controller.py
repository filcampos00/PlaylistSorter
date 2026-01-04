"""YouTube Music API routes (controller)."""

from fastapi import APIRouter

from ..common.schemas import AuthHeaders, AuthTestResponse, PlaylistsResponse
from .service import YouTubeService

router = APIRouter(prefix="/youtube", tags=["YouTube Music"])


@router.post("/auth/test", response_model=AuthTestResponse)
async def test_auth(payload: AuthHeaders):
    """
    Test if the provided browser headers are valid for YouTube Music.
    Returns the channel name if successful.
    """
    try:
        youtube = YouTubeService(payload.headers_raw)
        account_info = youtube.get_account_info()
        channel_name = account_info.get("channelHandle", "Unknown")

        return AuthTestResponse(
            success=True,
            message="Authentication successful",
            channel_name=channel_name,
        )
    except ValueError as e:
        return AuthTestResponse(
            success=False,
            message=str(e),
            channel_name=None,
        )
    except Exception as e:
        return AuthTestResponse(
            success=False,
            message=f"Authentication failed: {str(e)}",
            channel_name=None,
        )


@router.post("/playlists", response_model=PlaylistsResponse)
async def get_playlists(payload: AuthHeaders):
    """
    Fetch user's YouTube Music playlists.
    Requires valid browser headers.
    """
    try:
        youtube = YouTubeService(payload.headers_raw)
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
