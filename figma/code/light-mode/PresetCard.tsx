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
          className="bg-gray-50 border border-gray-200 rounded-lg p-4"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full bg-purple-100 border border-purple-300 flex items-center justify-center text-sm text-purple-700">
                {index + 1}
              </div>
              <span className="font-medium text-gray-900">
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
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'bg-white border border-gray-300 text-gray-600 hover:bg-gray-50 hover:text-gray-900'
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
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'bg-white border border-gray-300 text-gray-600 hover:bg-gray-50 hover:text-gray-900'
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