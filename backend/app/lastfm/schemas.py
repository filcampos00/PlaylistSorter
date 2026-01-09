"""Schemas for Last.fm integration."""

from enum import Enum

from pydantic import BaseModel


class LastFmPeriod(str, Enum):
    """Time periods for Last.fm top artists."""

    OVERALL = "overall"
    TWELVE_MONTH = "12month"
    SIX_MONTH = "6month"
    THREE_MONTH = "3month"
    ONE_MONTH = "1month"
    SEVEN_DAY = "7day"


class TopArtistsRequest(BaseModel):
    """Request schema for fetching top artists from Last.fm."""

    username: str
    period: LastFmPeriod = LastFmPeriod.OVERALL
    limit: int = 50


class TopArtistsResponse(BaseModel):
    """Response schema for Last.fm top artists."""

    success: bool
    message: str
    artists: list[str] = []
