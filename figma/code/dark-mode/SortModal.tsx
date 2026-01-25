import { useState } from 'react';
import { X, Check, ChevronRight } from 'lucide-react';
import type { Playlist } from '../App';
import { PresetCard } from './PresetCard';
import { CustomSortBuilder } from './CustomSortBuilder';

interface SortModalProps {
  playlist: Playlist;
  onClose: () => void;
}

export type SortCriterion = 
  | 'title'
  | 'duration'
  | 'artist_name'
  | 'album_name'
  | 'album_release_date'
  | 'track_number'
  | 'favourite_artists';

export type SortDirection = 'asc' | 'desc';

export interface SortLevel {
  criterion: SortCriterion;
  direction: SortDirection;
}

export interface PresetConfig {
  id: string;
  name: string;
  description: string;
  levels: SortLevel[];
}

const PRESETS: PresetConfig[] = [
  {
    id: 'discography',
    name: 'Discography',
    description: 'Organize by artist discography',
    levels: [
      { criterion: 'artist_name', direction: 'asc' },
      { criterion: 'album_release_date', direction: 'asc' },
      { criterion: 'track_number', direction: 'asc' },
    ],
  },
  {
    id: 'latest_releases',
    name: 'Latest Releases',
    description: 'Newest albums and tracks first',
    levels: [
      { criterion: 'album_release_date', direction: 'desc' },
      { criterion: 'track_number', direction: 'asc' },
    ],
  },
  {
    id: 'favourites_first',
    name: 'Favourites First',
    description: 'Prioritize your favorite artists',
    levels: [
      { criterion: 'favourite_artists', direction: 'asc' },
      { criterion: 'artist_name', direction: 'asc' },
      { criterion: 'album_release_date', direction: 'asc' },
      { criterion: 'track_number', direction: 'asc' },
    ],
  },
];

type ViewMode = 'select' | 'preset-edit' | 'custom';

export function SortModal({ playlist, onClose }: SortModalProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('select');
  const [selectedPreset, setSelectedPreset] = useState<PresetConfig | null>(null);
  const [editedPresetLevels, setEditedPresetLevels] = useState<SortLevel[]>([]);
  const [customLevels, setCustomLevels] = useState<SortLevel[]>([]);
  const [isSorting, setIsSorting] = useState(false);
  const [sortComplete, setSortComplete] = useState(false);

  const handlePresetSelect = (preset: PresetConfig) => {
    setSelectedPreset(preset);
    setEditedPresetLevels([...preset.levels]);
    setViewMode('preset-edit');
  };

  const handleCustomClick = () => {
    setViewMode('custom');
    setCustomLevels([]);
  };

  const handlePresetDirectionChange = (levelIndex: number, newDirection: SortDirection) => {
    const updated = [...editedPresetLevels];
    updated[levelIndex] = { ...updated[levelIndex], direction: newDirection };
    setEditedPresetLevels(updated);
  };

  const handleApplySort = (levels: SortLevel[]) => {
    setIsSorting(true);
    
    // Simulate API call
    setTimeout(() => {
      console.log('Applying sort with levels:', levels);
      setIsSorting(false);
      setSortComplete(true);
      
      setTimeout(() => {
        onClose();
      }, 1500);
    }, 1000);
  };

  const handleBackToSelect = () => {
    setViewMode('select');
    setSelectedPreset(null);
    setEditedPresetLevels([]);
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-zinc-900 rounded-2xl max-w-2xl w-full shadow-2xl border border-zinc-800 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex-shrink-0 border-b border-zinc-800 p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="mb-1">
                {viewMode === 'select' && 'Sort Playlist'}
                {viewMode === 'preset-edit' && selectedPreset?.name}
                {viewMode === 'custom' && 'Custom Sort'}
              </h2>
              <p className="text-sm text-zinc-400">
                {playlist.name} • {playlist.trackCount} tracks
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-zinc-500 hover:text-zinc-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {sortComplete ? (
            <div className="flex flex-col items-center justify-center py-16 px-6">
              <div className="w-16 h-16 rounded-full bg-green-600 flex items-center justify-center mb-4">
                <Check className="w-8 h-8 text-white" />
              </div>
              <h3 className="mb-2">Playlist Sorted!</h3>
              <p className="text-zinc-400 text-center">
                Your playlist has been reorganized successfully
              </p>
            </div>
          ) : (
            <>
              {viewMode === 'select' && (
                <div className="p-6 space-y-4">
                  <p className="text-sm text-zinc-400 mb-2">
                    Choose a preset or create your own sorting rules:
                  </p>
                  
                  {/* Preset Cards */}
                  {PRESETS.map((preset) => (
                    <button
                      key={preset.id}
                      onClick={() => handlePresetSelect(preset)}
                      className="w-full text-left p-5 rounded-xl bg-zinc-800/30 border border-zinc-700 hover:border-zinc-600 hover:bg-zinc-800/50 transition-all group"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="mb-1 group-hover:text-purple-400 transition-colors">
                            {preset.name}
                          </h3>
                          <p className="text-sm text-zinc-500">
                            {preset.description}
                          </p>
                        </div>
                        <ChevronRight className="w-5 h-5 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
                      </div>
                    </button>
                  ))}

                  {/* Custom Sort Button */}
                  <button
                    onClick={handleCustomClick}
                    className="w-full text-left p-5 rounded-xl bg-zinc-800/30 border border-zinc-700 hover:border-zinc-600 hover:bg-zinc-800/50 transition-all group"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="mb-1 group-hover:text-purple-400 transition-colors">
                          Custom Sort
                        </h3>
                        <p className="text-sm text-zinc-500">
                          Build your own sorting criteria
                        </p>
                      </div>
                      <ChevronRight className="w-5 h-5 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
                    </div>
                  </button>
                </div>
              )}

              {viewMode === 'preset-edit' && selectedPreset && (
                <div className="p-6">
                  <p className="text-sm text-zinc-400 mb-4">
                    Adjust the sorting direction for each level:
                  </p>
                  <PresetCard
                    levels={editedPresetLevels}
                    onDirectionChange={handlePresetDirectionChange}
                  />
                </div>
              )}

              {viewMode === 'custom' && (
                <div className="p-6">
                  <CustomSortBuilder
                    levels={customLevels}
                    onChange={setCustomLevels}
                  />
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        {!sortComplete && (
          <div className="flex-shrink-0 border-t border-zinc-800 p-6">
            <div className="flex gap-3">
              {viewMode !== 'select' ? (
                <button
                  onClick={handleBackToSelect}
                  disabled={isSorting}
                  className="px-4 py-2.5 rounded-lg text-zinc-400 hover:text-zinc-200 transition-colors disabled:opacity-50"
                >
                  ← Back
                </button>
              ) : null}
              
              <div className="flex-1" />
              
              <button
                onClick={onClose}
                disabled={isSorting}
                className="px-6 py-2.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              
              {viewMode !== 'select' && (
                <button
                  onClick={() => {
                    const levels = viewMode === 'preset-edit' ? editedPresetLevels : customLevels;
                    handleApplySort(levels);
                  }}
                  disabled={isSorting || (viewMode === 'custom' && customLevels.length === 0)}
                  className="px-6 py-2.5 rounded-lg bg-purple-600 hover:bg-purple-700 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSorting ? 'Sorting...' : 'Apply Sort'}
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}