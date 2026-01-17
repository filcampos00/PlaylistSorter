import { useEffect, useState } from "react";
import { useAuthStore } from "@/store";
import { API_BASE_URL } from "@/config";
import { Header } from "@/components/Header";
import { PlaylistCard, PlaylistCardSkeleton } from "@/components/PlaylistCard";
import { SortModal } from "@/components/SortModal";
import { ToastContainer, useToast } from "@/components/ui/toast";
import { useTheme } from "@/components/ThemeProvider";
import { cn } from "@/lib/utils";
import type { Playlist, SortLevel } from "@/types";

export function DashboardPage() {
  const { channelName, authHeaders, logout } = useAuthStore();
  const { theme } = useTheme();
  const isLight = theme === "light";
  const { toasts, success, error: showError, dismissToast } = useToast();

  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal state
  const [selectedPlaylist, setSelectedPlaylist] = useState<Playlist | null>(null);
  const [isSorting, setIsSorting] = useState(false);

  // Fetch playlists on mount
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
        setError(
          err instanceof Error ? err.message : "Failed to fetch playlists"
        );
      } finally {
        setIsLoading(false);
      }
    };

    fetchPlaylists();
  }, [authHeaders]);

  // Handle sort
  const handleSort = async (levels: SortLevel[], favouriteArtists?: string[]) => {
    if (!selectedPlaylist || !authHeaders) return;

    const playlistName = selectedPlaylist.title;
    setIsSorting(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/youtube/playlists/${selectedPlaylist.playlist_id}/sort`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            headers_raw: authHeaders,
            sort_levels: levels,
            favourite_artists: favouriteArtists || [],
          }),
        }
      );

      const data = await response.json();

      // Close modal immediately
      setSelectedPlaylist(null);

      if (data.success) {
        success(`"${playlistName}" sorted successfully!`);
      } else {
        showError(data.message || "Sort failed");
      }
    } catch (err) {
      setSelectedPlaylist(null);
      showError(err instanceof Error ? err.message : "Sort failed");
    } finally {
      setIsSorting(false);
    }
  };

  // Handle shuffle
  const handleShuffle = async () => {
    if (!selectedPlaylist || !authHeaders) return;

    const playlistName = selectedPlaylist.title;
    setIsSorting(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/youtube/playlists/${selectedPlaylist.playlist_id}/shuffle`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            headers_raw: authHeaders,
          }),
        }
      );

      const data = await response.json();

      // Close modal immediately
      setSelectedPlaylist(null);

      if (data.success) {
        success(`"${playlistName}" shuffled successfully!`);
      } else {
        showError(data.message || "Shuffle failed");
      }
    } catch (err) {
      setSelectedPlaylist(null);
      showError(err instanceof Error ? err.message : "Shuffle failed");
    } finally {
      setIsSorting(false);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />

      {/* Diagonal gradient background */}
      <div
        className={cn(
          "fixed inset-0 -z-10 bg-gradient-to-br",
          isLight
            ? "from-purple-100 via-white to-pink-100"
            : "from-zinc-950 via-zinc-900 to-purple-950"
        )}
      />

      {/* Header */}
      <Header userName={channelName || undefined} onLogout={logout} />

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <h2 className="mb-6 text-2xl font-semibold">Your Playlists</h2>

        {/* Loading State */}
        {isLoading && (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
            {Array.from({ length: 10 }).map((_, i) => (
              <PlaylistCardSkeleton key={i} />
            ))}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="rounded-xl border border-destructive/50 bg-destructive/10 p-6 text-center">
            <p className="mb-4 text-destructive">⚠️ {error}</p>
            <button
              className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
              onClick={() => window.location.reload()}
            >
              Retry
            </button>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && playlists.length === 0 && (
          <div className="py-12 text-center text-muted-foreground">
            <p>No playlists found.</p>
          </div>
        )}

        {/* Playlist Grid */}
        {!isLoading && !error && playlists.length > 0 && (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
            {playlists.map((playlist) => (
              <PlaylistCard
                key={playlist.playlist_id}
                id={playlist.playlist_id}
                name={playlist.title}
                trackCount={playlist.track_count}
                thumbnailUrl={playlist.thumbnail_url || undefined}
                isSelected={selectedPlaylist?.playlist_id === playlist.playlist_id}
                onSelect={() => setSelectedPlaylist(playlist)}
              />
            ))}
          </div>
        )}
      </main>

      {/* Sort Modal */}
      {selectedPlaylist && (
        <SortModal
          open={true}
          playlist={selectedPlaylist}
          onClose={() => setSelectedPlaylist(null)}
          onSort={handleSort}
          onShuffle={handleShuffle}
          isSorting={isSorting}
        />
      )}
    </div>
  );
}
