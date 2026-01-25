import { Play, Clock } from 'lucide-react';
import type { Track } from './PlaylistDetail';

interface TrackListProps {
  tracks: Track[];
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

export function TrackList({ tracks }: TrackListProps) {
  return (
    <div className="bg-zinc-900/30 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="grid grid-cols-[auto_2fr_1.5fr_1fr_auto] gap-4 px-6 py-3 border-b border-zinc-800/50 text-sm text-zinc-500">
        <div className="w-8">#</div>
        <div>TITLE</div>
        <div>ALBUM</div>
        <div>RELEASE DATE</div>
        <div className="w-12 text-right">
          <Clock className="w-4 h-4 inline" />
        </div>
      </div>

      {/* Tracks */}
      <div>
        {tracks.map((track, index) => (
          <div
            key={track.id}
            className="grid grid-cols-[auto_2fr_1.5fr_1fr_auto] gap-4 px-6 py-3 hover:bg-zinc-800/40 transition-colors group"
          >
            <div className="w-8 flex items-center text-zinc-500 group-hover:text-zinc-100">
              <span className="group-hover:hidden">{index + 1}</span>
              <Play className="w-4 h-4 hidden group-hover:block fill-current" />
            </div>
            <div>
              <div className="text-zinc-100 mb-1">{track.title}</div>
              <div className="text-sm text-zinc-500">{track.artist}</div>
            </div>
            <div className="flex items-center text-zinc-400 text-sm">
              {track.album}
            </div>
            <div className="flex items-center text-zinc-400 text-sm">
              {formatDate(track.releaseDate)}
            </div>
            <div className="w-12 flex items-center justify-end text-zinc-500 text-sm">
              {formatDuration(track.duration)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
