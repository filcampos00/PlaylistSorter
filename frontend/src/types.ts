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
  | "artist_name_desc";

export interface SortResponse {
    success: boolean;
    message: string;
    tracks_reordered: number;
}
