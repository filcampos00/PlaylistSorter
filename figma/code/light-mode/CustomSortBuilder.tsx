import { Plus, Trash2 } from 'lucide-react';
import type { SortLevel, SortCriterion, SortDirection } from './SortModal';

interface CustomSortBuilderProps {
  levels: SortLevel[];
  onChange: (levels: SortLevel[]) => void;
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

// Validation rules from the documentation
const hasAlbumContext = (levels: SortLevel[]): boolean => {
  return levels.some(l => 
    l.criterion === 'album_name' || 
    l.criterion === 'album_release_date' ||
    l.criterion === 'artist_name'
  );
};

const hasTrackNumber = (levels: SortLevel[]): boolean => {
  return levels.some(l => l.criterion === 'track_number');
};

const getAvailableCriteria = (levels: SortLevel[], levelIndex: number): SortCriterion[] => {
  const allCriteria: SortCriterion[] = [
    'title',
    'duration',
    'artist_name',
    'album_name',
    'album_release_date',
    'track_number',
    'favourite_artists',
  ];

  const usedCriteria = levels.map(l => l.criterion);
  const previousLevels = levels.slice(0, levelIndex);
  
  return allCriteria.filter(criterion => {
    // Rule: No duplicates
    if (usedCriteria.includes(criterion)) return false;
    
    // Rule: favourite_artists only at Level 1 (index 0)
    if (criterion === 'favourite_artists' && levelIndex !== 0) return false;
    
    // Rule: track_number requires prior album context
    if (criterion === 'track_number' && !hasAlbumContext(previousLevels)) return false;
    
    // Rule: No album attributes after track_number
    if (hasTrackNumber(previousLevels)) {
      if (['album_name', 'album_release_date', 'artist_name'].includes(criterion)) {
        return false;
      }
    }
    
    return true;
  });
};

export function CustomSortBuilder({ levels, onChange }: CustomSortBuilderProps) {
  const handleAddLevel = () => {
    if (levels.length >= 3) return;
    
    const available = getAvailableCriteria(levels, levels.length);
    if (available.length === 0) return;
    
    onChange([
      ...levels,
      { criterion: available[0], direction: 'asc' },
    ]);
  };

  const handleRemoveLevel = (index: number) => {
    onChange(levels.filter((_, i) => i !== index));
  };

  const handleCriterionChange = (index: number, criterion: SortCriterion) => {
    const updated = [...levels];
    updated[index] = { criterion, direction: updated[index].direction };
    onChange(updated);
  };

  const handleDirectionChange = (index: number, direction: SortDirection) => {
    const updated = [...levels];
    updated[index] = { ...updated[index], direction };
    onChange(updated);
  };

  const canAddMore = levels.length < 3;
  const availableForNext = getAvailableCriteria(levels, levels.length);

  return (
    <div className="space-y-4">
      {levels.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600 mb-2">
            Build your own sorting criteria
          </p>
          <p className="text-sm text-gray-500 mb-6">
            Add up to 3 levels
          </p>
          <button
            onClick={handleAddLevel}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-purple-600 hover:bg-purple-700 text-white transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add First Level
          </button>
        </div>
      ) : (
        <>
          {/* Existing Levels */}
          {levels.map((level, index) => {
            const available = getAvailableCriteria(
              levels.filter((_, i) => i !== index),
              index
            );
            
            return (
              <div
                key={index}
                className="bg-gray-50 border border-gray-200 rounded-lg p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-full bg-purple-100 border border-purple-300 flex items-center justify-center text-sm text-purple-700">
                      {index + 1}
                    </div>
                    <span className="text-sm text-gray-600">
                      Level {index + 1}
                    </span>
                  </div>
                  <button
                    onClick={() => handleRemoveLevel(index)}
                    className="text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                {/* Criterion Select */}
                <select
                  value={level.criterion}
                  onChange={(e) => handleCriterionChange(index, e.target.value as SortCriterion)}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-900 mb-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {available.map(criterion => (
                    <option key={criterion} value={criterion}>
                      {CRITERION_LABELS[criterion]}
                    </option>
                  ))}
                </select>

                {/* Direction Toggle */}
                <div className="flex gap-2">
                  <button
                    onClick={() => handleDirectionChange(index, 'asc')}
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
                    onClick={() => handleDirectionChange(index, 'desc')}
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
            );
          })}

          {/* Add Level Button */}
          {canAddMore && availableForNext.length > 0 && (
            <button
              onClick={handleAddLevel}
              className="w-full py-3 rounded-lg border-2 border-dashed border-gray-300 hover:border-purple-400 hover:bg-purple-50 text-gray-500 hover:text-purple-600 transition-all flex items-center justify-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Level {levels.length + 1}
            </button>
          )}
        </>
      )}
    </div>
  );
}