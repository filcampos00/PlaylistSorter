import { useState } from 'react';
import { PlaylistCard } from './components/PlaylistCard';
import { Header } from './components/Header';
import { SortModal } from './components/SortModal';

// Mock playlist data
const playlists = [
  {
    id: '1',
    name: 'Chill Vibes',
    trackCount: 42,
    thumbnail: 'https://images.unsplash.com/photo-1644855640845-ab57a047320e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtdXNpYyUyMGFsYnVtJTIwY292ZXJ8ZW58MXx8fHwxNzY4MTgwMzczfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
  },
  {
    id: '2',
    name: 'Workout Mix',
    trackCount: 58,
    thumbnail: 'https://images.unsplash.com/photo-1709731191876-899e32264420?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb25jZXJ0JTIwc3RhZ2UlMjBsaWdodHN8ZW58MXx8fHwxNzY4MjI2NzI3fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
  },
  {
    id: '3',
    name: 'Late Night Jazz',
    trackCount: 35,
    thumbnail: 'https://images.unsplash.com/photo-1644885956764-2dc1e3ebc6d2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx2aW55bCUyMHJlY29yZCUyMGFic3RyYWN0fGVufDF8fHx8MTc2ODI1MDU2OXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
  },
  {
    id: '4',
    name: 'Focus & Study',
    trackCount: 67,
    thumbnail: 'https://images.unsplash.com/photo-1649956736509-f359d191bbcb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoZWFkcGhvbmVzJTIwbXVzaWN8ZW58MXx8fHwxNzY4MjQ1ODcxfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
  },
  {
    id: '5',
    name: 'Rock Classics',
    trackCount: 89,
    thumbnail: 'https://images.unsplash.com/photo-1610620146780-26908fab50ec?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxndWl0YXIlMjBpbnN0cnVtZW50fGVufDF8fHx8MTc2ODIzMDMyMnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
  },
  {
    id: '6',
    name: 'Electronic Dreams',
    trackCount: 44,
    thumbnail: 'https://images.unsplash.com/photo-1618107095181-e3ba0f53ee59?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxkaiUyMHR1cm50YWJsZXxlbnwxfHx8fDE3NjgyNTA1NzB8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
  },
];

export type Playlist = typeof playlists[0];

export default function App() {
  const [playlistToSort, setPlaylistToSort] = useState<Playlist | null>(null);

  const handleLogout = () => {
    console.log('Logout clicked');
    // Add logout logic here
  };

  const handleSortPlaylist = (playlist: Playlist) => {
    setPlaylistToSort(playlist);
  };

  const handleCloseSortModal = () => {
    setPlaylistToSort(null);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <Header onLogout={handleLogout} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-zinc-400 tracking-wide">Your Playlists</h2>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {playlists.map((playlist) => (
            <PlaylistCard
              key={playlist.id}
              name={playlist.name}
              trackCount={playlist.trackCount}
              thumbnail={playlist.thumbnail}
              onSort={() => handleSortPlaylist(playlist)}
            />
          ))}
        </div>
      </main>

      {/* Sort Modal */}
      {playlistToSort && (
        <SortModal
          playlist={playlistToSort}
          onClose={handleCloseSortModal}
        />
      )}
    </div>
  );
}
