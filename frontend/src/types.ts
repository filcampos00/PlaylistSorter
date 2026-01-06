/**
 * Shared TypeScript types for the application.
 */

export interface Playlist {
    playlist_id: string;
    title: string;
    thumbnail_url: string | null;
    track_count: number | null;
}

export type SortOption = 
  | "album_release_date_asc" 
  | "album_release_date_desc"
  | "artist_name_asc"
  | "artist_name_desc"
  | "favourite_artists_first";

export type LastFmPeriod = 
  | "overall"
  | "12month"
  | "6month"
  | "3month"
  | "1month"
  | "7day";

export type AlbumOrder = "newest" | "oldest";

export interface SortResponse {
    success: boolean;
    message: string;
    tracks_reordered: number;
}

export interface TopArtistsResponse {
    success: boolean;
    message: string;
    artists: string[];
}
