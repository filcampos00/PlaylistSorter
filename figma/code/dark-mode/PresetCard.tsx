import { ArrowUpDown } from 'lucide-react';
import type { SortLevel, SortCriterion, SortDirection } from './SortModal';

interface PresetCardProps {
  levels: SortLevel[];
  onDirectionChange: (levelIndex: number, direction: SortDirection) => void;
}

const CRITERION_LABELS: Record<SortCriterion, string> = {
  title: 'Title',
  duration: 'Duration',
  artist_name: 'Artist',
  album_name: 'Album',
  album_release_date: 'Release Date',
  track_number: 'Track Number',
  favourite_artists: 'Favourite Artists',
};

const DIRECTION_LABELS: Record<SortCriterion, { asc: string; desc: string }> = {
  title: { asc: 'A → Z', desc: 'Z → A' },
  duration: { asc: 'Shortest First', desc: 'Longest First' },
  artist_name: { asc: 'A → Z', desc: 'Z → A' },
  album_name: { asc: 'A → Z', desc: 'Z → A' },
  album_release_date: { asc: 'Oldest First', desc: 'Newest First' },
  track_number: { asc: '1 → 99', desc: '99 → 1' },
  favourite_artists: { asc: 'By Rank', desc: 'Reverse Rank' },
};

export function PresetCard({ levels, onDirectionChange }: PresetCardProps) {
  return (
    <div className="space-y-3">
      {levels.map((level, index) => (
        <div
          key={index}
          className="bg-zinc-800/40 border border-zinc-700 rounded-lg p-4"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full bg-purple-600/20 border border-purple-600/50 flex items-center justify-center text-sm text-purple-300">
                {index + 1}
              </div>
              <span className="font-medium text-zinc-200">
                {CRITERION_LABELS[level.criterion]}
              </span>
            </div>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={() => onDirectionChange(index, 'asc')}
              className={`
                flex-1 px-4 py-2.5 rounded-lg text-sm transition-all
                ${level.direction === 'asc'
                  ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/20'
                  : 'bg-zinc-700/50 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-300'
                }
              `}
            >
              {DIRECTION_LABELS[level.criterion].asc}
            </button>
            <button
              onClick={() => onDirectionChange(index, 'desc')}
              className={`
                flex-1 px-4 py-2.5 rounded-lg text-sm transition-all
                ${level.direction === 'desc'
                  ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/20'
                  : 'bg-zinc-700/50 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-300'
                }
              `}
            >
              {DIRECTION_LABELS[level.criterion].desc}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}