import { useEffect, useState } from 'react';
import { useAuthStore } from '../store';
import { API_BASE_URL } from '../config';
import type { Playlist } from '../types';
import './DashboardPage.css';

export const DashboardPage = () => {
    const { channelName, authHeaders, logout } = useAuthStore();
    const [playlists, setPlaylists] = useState<Playlist[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchPlaylists = async () => {
            if (!authHeaders) return;

            try {
                const response = await fetch(`${API_BASE_URL}/youtube/playlists`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ headers_raw: authHeaders }),
                });

                const data = await response.json();

                if (data.success) {
                    setPlaylists(data.playlists);
                } else {
                    setError(data.message);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to fetch playlists');
            } finally {
                setIsLoading(false);
            }
        };

        fetchPlaylists();
    }, [authHeaders]);

    return (
        <div className="dashboard-page">
            {/* Background Ambience */}
            <div className="bg-orb orb-primary" />
            <div className="bg-orb orb-secondary" />

            <div className="dashboard-container fade-in">
                <header className="dashboard-header">
                    <h1>🎵 Playlist Sorter</h1>
                    <div className="user-info">
                        <span className="channel-name">{channelName || 'Connected'}</span>
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
                            <button className="btn btn-outline" onClick={() => window.location.reload()}>
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
                                <div key={playlist.playlist_id} className="playlist-card">
                                    <div className="playlist-thumbnail">
                                        {playlist.thumbnail_url ? (
                                            <img src={playlist.thumbnail_url} alt={playlist.title} />
                                        ) : (
                                            <div className="placeholder-thumbnail">🎵</div>
                                        )}
                                    </div>
                                    <div className="playlist-info">
                                        <h3>{playlist.title}</h3>
                                        {playlist.track_count !== null && (
                                            <p className="track-count">{playlist.track_count} tracks</p>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
};
