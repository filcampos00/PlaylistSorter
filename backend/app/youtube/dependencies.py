"""FastAPI dependencies for YouTube Music module."""

from ..common.schemas import AuthHeaders
from ..common.sorting import SortContext
from .service import YouTubeService


def get_youtube_service(payload: AuthHeaders) -> YouTubeService:
    """
    Dependency that creates a YouTubeService from auth headers.

    Args:
        payload: The auth headers from the request body.

    Returns:
        An authenticated YouTubeService instance.

    Raises:
        ValueError: If headers are invalid or authentication fails.
    """
    return YouTubeService(payload.headers_raw)


def get_sort_context() -> SortContext:
    """Provide sorting context. Extend later for user preferences."""
    return SortContext()
