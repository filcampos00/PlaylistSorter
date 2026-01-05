import { useEffect, useState } from "react";
import { useAuthStore } from "../store";
import { API_BASE_URL } from "../config";
import type { Playlist, SortOption } from "../types";
import "./DashboardPage.css";

export const DashboardPage = () => {
    const { channelName, authHeaders, logout } = useAuthStore();
    const [playlists, setPlaylists] = useState<Playlist[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Sorting State
    const [selectedPlaylistId, setSelectedPlaylistId] = useState<string | null>(null);
    const [sortBy, setSortBy] = useState<SortOption>("album_release_date_asc");
    const [isSorting, setIsSorting] = useState(false);
    const [sortResult, setSortResult] = useState<{ success: boolean; message: string } | null>(null);

    useEffect(() => {
        const fetchPlaylists = async () => {
            if (!authHeaders) return;

            try {
                const response = await fetch(`${API_BASE_URL}/youtube/playlists`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ headers_raw: authHeaders }),
                });

                const data = await response.json();

                if (data.success) {
                    setPlaylists(data.playlists);
                } else {
                    setError(data.message);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to fetch playlists");
            } finally {
                setIsLoading(false);
            }
        };

        fetchPlaylists();
    }, [authHeaders]);

    const handleSort = async () => {
        if (!selectedPlaylistId || !authHeaders) return;

        setIsSorting(true);
        setSortResult(null);

        try {
            const response = await fetch(
                `${API_BASE_URL}/youtube/playlists/${selectedPlaylistId}/sort?sort_by=${sortBy}`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        headers_raw: authHeaders,
                    }),
                }
            );

            const data = await response.json();

            setSortResult({
                success: data.success,
                message: data.message,
            });

            // Clear selection on success after short delay
            if (data.success) {
                setTimeout(() => {
                    setSortResult(null);
                    setSelectedPlaylistId(null);
                }, 3000);
            }
        } catch (err) {
            setSortResult({
                success: false,
                message: err instanceof Error ? err.message : "Sort failed",
            });
        } finally {
            setIsSorting(false);
        }
    };

    const selectedPlaylist = playlists.find((p) => p.playlist_id === selectedPlaylistId);

    return (
        <div className="dashboard-page">
            {/* Background Ambience */}
            <div className="bg-orb orb-primary" />
            <div className="bg-orb orb-secondary" />

            <div className="dashboard-container fade-in">
                <header className="dashboard-header">
                    <h1>🎵 Playlist Sorter</h1>
                    <div className="user-info">
                        <span className="channel-name">{channelName || "Connected"}</span>
                        <button className="btn btn-outline btn-sm" onClick={logout}>
                            Logout
                        </button>
                    </div>
                </header>

                <main className="dashboard-content">
                    {isLoading ? (
                        <div className="loading-state">
                            <div className="spinner" />
                            <p>Loading your playlists...</p>
                        </div>
                    ) : error ? (
                        <div className="error-state">
                            <p>⚠️ {error}</p>
                            <button
                                className="btn btn-outline"
                                onClick={() => window.location.reload()}
                            >
                                Retry
                            </button>
                        </div>
                    ) : playlists.length === 0 ? (
                        <div className="empty-state">
                            <p>No playlists found.</p>
                        </div>
                    ) : (
                        <div className="playlists-grid">
                            {playlists.map((playlist) => (
                                <div
                                    key={playlist.playlist_id}
                                    className={`playlist-card ${selectedPlaylistId === playlist.playlist_id ? "selected" : ""
                                        }`}
                                    onClick={() => {
                                        setSelectedPlaylistId(playlist.playlist_id);
                                        setSortResult(null);
                                    }}
                                >
                                    <div className="playlist-thumbnail">
                                        {playlist.thumbnail_url ? (
                                            <img
                                                src={playlist.thumbnail_url}
                                                alt={playlist.title}
                                                onError={(e) => {
                                                    // Replace broken image with placeholder
                                                    e.currentTarget.style.display = 'none';
                                                    e.currentTarget.nextElementSibling?.classList.remove('hidden');
                                                }}
                                            />
                                        ) : null}
                                        <div className={`placeholder-thumbnail ${playlist.thumbnail_url ? 'hidden' : ''}`}>
                                            🎵
                                        </div>
                                    </div>
                                    <div className="playlist-info">
                                        <h3>{playlist.title}</h3>
                                        {playlist.track_count !== null && (
                                            <p className="track-count">{playlist.track_count} tracks</p>
                                        )}
                                    </div>
                                    {selectedPlaylistId === playlist.playlist_id && (
                                        <div className="selection-badge">✔ Selected</div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </main>

                {/* Floating Sort Controls */}
                {selectedPlaylistId && selectedPlaylist && (
                    <div className="sort-controls-panel slide-up">
                        <div className="sort-controls-content">
                            <div className="sort-info">
                                <span className="sort-label">Sort <strong>{selectedPlaylist.title}</strong> by:</span>
                                <select
                                    className="sort-select"
                                    value={sortBy}
                                    onChange={(e) => setSortBy(e.target.value as SortOption)}
                                    disabled={isSorting}
                                >
                                    <option value="album_release_date_asc">
                                        Album Release Date (Oldest First)
                                    </option>
                                    <option value="album_release_date_desc">
                                        Album Release Date (Newest First)
                                    </option>
                                </select>
                            </div>

                            <div className="sort-actions">
                                <button
                                    className="btn btn-primary sort-btn"
                                    onClick={handleSort}
                                    disabled={isSorting}
                                >
                                    {isSorting ? "Sorting..." : "Sort Now"}
                                </button>
                                <button
                                    className="btn btn-text cancel-btn"
                                    onClick={() => setSelectedPlaylistId(null)}
                                    disabled={isSorting}
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>

                        {sortResult && (
                            <div className={`sort-result-toast ${sortResult.success ? "success" : "error"}`}>
                                {sortResult.success ? "✅" : "⚠️"} {sortResult.message}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};
