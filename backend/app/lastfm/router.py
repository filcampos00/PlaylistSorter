"""Last.fm API routes."""

from fastapi import APIRouter

from .schemas import TopArtistsRequest, TopArtistsResponse
from .service import LastFmService


router = APIRouter(prefix="/lastfm", tags=["Last.fm"])


@router.post("/top-artists", response_model=TopArtistsResponse)
async def get_top_artists(request: TopArtistsRequest):
    """
    Fetch a user's top artists from Last.fm.

    Args:
        request: Contains username, period, and limit.

    Returns:
        List of artist names from the user's Last.fm profile.
    """
    try:
        service = LastFmService()
        artists = await service.get_top_artists(
            username=request.username,
            period=request.period,
            limit=request.limit,
        )

        return TopArtistsResponse(
            success=True,
            message=f"Found {len(artists)} top artists for '{request.username}'",
            artists=artists,
        )
    except ValueError as e:
        return TopArtistsResponse(
            success=False,
            message=str(e),
            artists=[],
        )
    except Exception as e:
        return TopArtistsResponse(
            success=False,
            message=f"Failed to fetch top artists: {str(e)}",
            artists=[],
        )
