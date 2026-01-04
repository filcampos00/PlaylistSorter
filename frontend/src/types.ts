/**
 * Shared TypeScript types for the application.
 */

export interface Playlist {
    playlist_id: string;
    title: string;
    thumbnail_url: string | null;
    track_count: number | null;
}
