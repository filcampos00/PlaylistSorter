import { useState, useMemo } from 'react';
import { ArrowLeft, Disc3, Calendar, Users, Settings2 } from 'lucide-react';
import type { Playlist } from '../App';
import { TrackList } from './TrackList';
import { CustomSortModal } from './CustomSortModal';

interface PlaylistDetailProps {
  playlist: Playlist;
  onBack: () => void;
}

export type SortPreset = 'discography' | 'newest' | 'favorite-artists' | 'custom';

export interface Track {
  id: string;
  title: string;
  artist: string;
  album: string;
  releaseDate: Date;
  duration: number; // in seconds
  playCount: number;
}

export interface CustomSortConfig {
  primary: 'artist' | 'album' | 'release-date' | 'title' | 'play-count';
  primaryOrder: 'asc' | 'desc';
  secondary?: 'artist' | 'album' | 'release-date' | 'title' | 'play-count';
  secondaryOrder?: 'asc' | 'desc';
}

// Mock track data
const generateTracks = (): Track[] => [
  { id: '1', title: 'Midnight Drive', artist: 'The Weeknd', album: 'After Hours', releaseDate: new Date('2020-03-20'), duration: 234, playCount: 145 },
  { id: '2', title: 'Blinding Lights', artist: 'The Weeknd', album: 'After Hours', releaseDate: new Date('2020-03-20'), duration: 200, playCount: 523 },
  { id: '3', title: 'Save Your Tears', artist: 'The Weeknd', album: 'After Hours', releaseDate: new Date('2020-03-20'), duration: 215, playCount: 312 },
  { id: '4', title: 'Levitating', artist: 'Dua Lipa', album: 'Future Nostalgia', releaseDate: new Date('2020-03-27'), duration: 203, playCount: 487 },
  { id: '5', title: 'Physical', artist: 'Dua Lipa', album: 'Future Nostalgia', releaseDate: new Date('2020-03-27'), duration: 193, playCount: 234 },
  { id: '6', title: 'Break My Soul', artist: 'Beyoncé', album: 'Renaissance', releaseDate: new Date('2022-07-29'), duration: 279, playCount: 156 },
  { id: '7', title: 'CUFF IT', artist: 'Beyoncé', album: 'Renaissance', releaseDate: new Date('2022-07-29'), duration: 225, playCount: 289 },
  { id: '8', title: 'As It Was', artist: 'Harry Styles', album: 'Harry\'s House', releaseDate: new Date('2022-05-20'), duration: 167, playCount: 612 },
  { id: '9', title: 'Anti-Hero', artist: 'Taylor Swift', album: 'Midnights', releaseDate: new Date('2022-10-21'), duration: 200, playCount: 734 },
  { id: '10', title: 'Karma', artist: 'Taylor Swift', album: 'Midnights', releaseDate: new Date('2022-10-21'), duration: 204, playCount: 421 },
];

export function PlaylistDetail({ playlist, onBack }: PlaylistDetailProps) {
  const [sortPreset, setSortPreset] = useState<SortPreset>('discography');
  const [customSort, setCustomSort] = useState<CustomSortConfig>({
    primary: 'artist',
    primaryOrder: 'asc',
  });
  const [showCustomModal, setShowCustomModal] = useState(false);
  const tracks = useMemo(() => generateTracks(), []);

  const sortedTracks = useMemo(() => {
    const sorted = [...tracks];

    if (sortPreset === 'discography') {
      // Sort by artist, then by album, then by release date
      return sorted.sort((a, b) => {
        const artistCompare = a.artist.localeCompare(b.artist);
        if (artistCompare !== 0) return artistCompare;
        
        const albumCompare = a.album.localeCompare(b.album);
        if (albumCompare !== 0) return albumCompare;
        
        return a.releaseDate.getTime() - b.releaseDate.getTime();
      });
    } else if (sortPreset === 'newest') {
      // Sort by release date, newest first
      return sorted.sort((a, b) => b.releaseDate.getTime() - a.releaseDate.getTime());
    } else if (sortPreset === 'favorite-artists') {
      // Sort by play count (as a proxy for favorites), then by artist
      return sorted.sort((a, b) => {
        const playCountCompare = b.playCount - a.playCount;
        if (playCountCompare !== 0) return playCountCompare;
        
        return a.artist.localeCompare(b.artist);
      });
    } else if (sortPreset === 'custom') {
      // Apply custom sort
      return sorted.sort((a, b) => {
        const getValue = (track: Track, field: string) => {
          switch (field) {
            case 'artist': return track.artist;
            case 'album': return track.album;
            case 'release-date': return track.releaseDate.getTime();
            case 'title': return track.title;
            case 'play-count': return track.playCount;
            default: return '';
          }
        };

        const primaryA = getValue(a, customSort.primary);
        const primaryB = getValue(b, customSort.primary);
        
        let primaryCompare: number;
        if (typeof primaryA === 'string' && typeof primaryB === 'string') {
          primaryCompare = primaryA.localeCompare(primaryB);
        } else {
          primaryCompare = (primaryA as number) - (primaryB as number);
        }
        
        if (customSort.primaryOrder === 'desc') {
          primaryCompare = -primaryCompare;
        }
        
        if (primaryCompare !== 0 || !customSort.secondary) return primaryCompare;

        // Secondary sort
        const secondaryA = getValue(a, customSort.secondary);
        const secondaryB = getValue(b, customSort.secondary);
        
        let secondaryCompare: number;
        if (typeof secondaryA === 'string' && typeof secondaryB === 'string') {
          secondaryCompare = secondaryA.localeCompare(secondaryB);
        } else {
          secondaryCompare = (secondaryA as number) - (secondaryB as number);
        }
        
        if (customSort.secondaryOrder === 'desc') {
          secondaryCompare = -secondaryCompare;
        }
        
        return secondaryCompare;
      });
    }

    return sorted;
  }, [tracks, sortPreset, customSort]);

  const handlePresetClick = (preset: SortPreset) => {
    if (preset === 'custom') {
      setShowCustomModal(true);
    } else {
      setSortPreset(preset);
    }
  };

  const handleCustomSortApply = (config: CustomSortConfig) => {
    setCustomSort(config);
    setSortPreset('custom');
    setShowCustomModal(false);
  };

  return (
    <div className="pb-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-zinc-400 hover:text-zinc-100 transition-colors mb-6"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Playlists</span>
        </button>

        <div className="flex items-start gap-6">
          <img
            src={playlist.thumbnail}
            alt={playlist.name}
            className="w-48 h-48 rounded-lg shadow-2xl object-cover"
          />
          <div className="flex-1">
            <p className="text-sm text-zinc-500 mb-2">PLAYLIST</p>
            <h1 className="mb-4">{playlist.name}</h1>
            <p className="text-zinc-400">{playlist.trackCount} tracks</p>
          </div>
        </div>
      </div>

      {/* Sort Presets */}
      <div className="mb-6">
        <h3 className="text-sm text-zinc-500 mb-3">SORT BY</h3>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => handlePresetClick('discography')}
            className={`
              flex items-center gap-2 px-4 py-2.5 rounded-lg transition-all
              ${sortPreset === 'discography'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/20'
                : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-300'
              }
            `}
          >
            <Disc3 className="w-4 h-4" />
            Discography
          </button>
          
          <button
            onClick={() => handlePresetClick('newest')}
            className={`
              flex items-center gap-2 px-4 py-2.5 rounded-lg transition-all
              ${sortPreset === 'newest'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/20'
                : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-300'
              }
            `}
          >
            <Calendar className="w-4 h-4" />
            Newest Releases
          </button>
          
          <button
            onClick={() => handlePresetClick('favorite-artists')}
            className={`
              flex items-center gap-2 px-4 py-2.5 rounded-lg transition-all
              ${sortPreset === 'favorite-artists'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/20'
                : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-300'
              }
            `}
          >
            <Users className="w-4 h-4" />
            Favorite Artists
          </button>
          
          <button
            onClick={() => handlePresetClick('custom')}
            className={`
              flex items-center gap-2 px-4 py-2.5 rounded-lg transition-all
              ${sortPreset === 'custom'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/20'
                : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-300'
              }
            `}
          >
            <Settings2 className="w-4 h-4" />
            Custom Sort
          </button>
        </div>
      </div>

      {/* Track List */}
      <TrackList tracks={sortedTracks} />

      {/* Custom Sort Modal */}
      {showCustomModal && (
        <CustomSortModal
          currentConfig={customSort}
          onApply={handleCustomSortApply}
          onClose={() => setShowCustomModal(false)}
        />
      )}
    </div>
  );
}
