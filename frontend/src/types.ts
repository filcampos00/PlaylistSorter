/**
 * Shared TypeScript types for the application.
 */

export interface Playlist {
  playlist_id: string;
  title: string;
  thumbnail_url: string | null;
  track_count: number | null;
}

// --- Multi-Level Sorting Types ---

export type SortAttribute =
  | "artist_name"
  | "album_name"
  | "album_release_date"
  | "track_number"
  | "favourite_artists"
  | "title";

export type SortDirection = "asc" | "desc";

export interface SortLevel {
  attribute: SortAttribute;
  direction: SortDirection;
}

// --- API Types ---

export type LastFmPeriod =
  | "overall"
  | "12month"
  | "6month"
  | "3month"
  | "1month"
  | "7day";

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

// --- Preset Configurations ---

export const PRESET_DISCOGRAPHY: SortLevel[] = [
  { attribute: "artist_name", direction: "asc" },
  { attribute: "album_release_date", direction: "asc" },
  { attribute: "track_number", direction: "asc" },
];

export const PRESET_LATEST_RELEASES: SortLevel[] = [
  { attribute: "album_release_date", direction: "desc" },
  { attribute: "track_number", direction: "asc" },
];

export const PRESET_FAVOURITES_FIRST: SortLevel[] = [
  { attribute: "favourite_artists", direction: "asc" },
  { attribute: "artist_name", direction: "asc" },
  { attribute: "album_release_date", direction: "desc" },
  { attribute: "track_number", direction: "asc" },
];

// --- UI Labels ---

export const SORT_ATTRIBUTE_LABELS: Record<SortAttribute, string> = {
  artist_name: "Artist Name",
  album_name: "Album Name",
  album_release_date: "Album Release Date",
  track_number: "Track Number",
  favourite_artists: "Favourite Artists",
  title: "Title",
};

export const SORT_DIRECTION_LABELS: Record<
  SortAttribute,
  { asc: string; desc: string }
> = {
  artist_name: { asc: "A → Z", desc: "Z → A" },
  album_name: { asc: "A → Z", desc: "Z → A" },
  album_release_date: { asc: "Oldest First", desc: "Newest First" },
  track_number: { asc: "1 → 99", desc: "99 → 1" },
  favourite_artists: { asc: "By Rank", desc: "Reverse Rank" },
  title: { asc: "A → Z", desc: "Z → A" },
};
