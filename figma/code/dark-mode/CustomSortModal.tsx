import { useState } from 'react';
import { X, ArrowUp, ArrowDown } from 'lucide-react';
import type { CustomSortConfig } from './PlaylistDetail';

interface CustomSortModalProps {
  currentConfig: CustomSortConfig;
  onApply: (config: CustomSortConfig) => void;
  onClose: () => void;
}

type SortField = 'artist' | 'album' | 'release-date' | 'title' | 'play-count';
type SortOrder = 'asc' | 'desc';

const FIELD_LABELS: Record<SortField, string> = {
  'artist': 'Artist',
  'album': 'Album',
  'release-date': 'Release Date',
  'title': 'Title',
  'play-count': 'Play Count',
};

export function CustomSortModal({ currentConfig, onApply, onClose }: CustomSortModalProps) {
  const [config, setConfig] = useState<CustomSortConfig>(currentConfig);

  const handleApply = () => {
    onApply(config);
  };

  const availableSecondaryFields = Object.keys(FIELD_LABELS).filter(
    field => field !== config.primary
  ) as SortField[];

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-zinc-900 rounded-xl max-w-lg w-full shadow-2xl border border-zinc-800">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-zinc-800">
          <h2>Custom Sort</h2>
          <button
            onClick={onClose}
            className="text-zinc-500 hover:text-zinc-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Primary Sort */}
          <div>
            <label className="block text-sm text-zinc-400 mb-3">Primary Sort</label>
            <div className="space-y-2">
              <select
                value={config.primary}
                onChange={(e) => setConfig({
                  ...config,
                  primary: e.target.value as SortField,
                  secondary: config.secondary === e.target.value ? undefined : config.secondary,
                })}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {Object.entries(FIELD_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
              
              <div className="flex gap-2">
                <button
                  onClick={() => setConfig({ ...config, primaryOrder: 'asc' })}
                  className={`
                    flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg transition-all
                    ${config.primaryOrder === 'asc'
                      ? 'bg-purple-600 text-white'
                      : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                    }
                  `}
                >
                  <ArrowUp className="w-4 h-4" />
                  Ascending
                </button>
                <button
                  onClick={() => setConfig({ ...config, primaryOrder: 'desc' })}
                  className={`
                    flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg transition-all
                    ${config.primaryOrder === 'desc'
                      ? 'bg-purple-600 text-white'
                      : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                    }
                  `}
                >
                  <ArrowDown className="w-4 h-4" />
                  Descending
                </button>
              </div>
            </div>
          </div>

          {/* Secondary Sort */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm text-zinc-400">Secondary Sort (Optional)</label>
              {config.secondary && (
                <button
                  onClick={() => setConfig({ ...config, secondary: undefined, secondaryOrder: undefined })}
                  className="text-xs text-purple-400 hover:text-purple-300"
                >
                  Clear
                </button>
              )}
            </div>
            <div className="space-y-2">
              <select
                value={config.secondary || ''}
                onChange={(e) => setConfig({
                  ...config,
                  secondary: e.target.value ? e.target.value as SortField : undefined,
                  secondaryOrder: e.target.value ? (config.secondaryOrder || 'asc') : undefined,
                })}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">None</option>
                {availableSecondaryFields.map((field) => (
                  <option key={field} value={field}>{FIELD_LABELS[field]}</option>
                ))}
              </select>
              
              {config.secondary && (
                <div className="flex gap-2">
                  <button
                    onClick={() => setConfig({ ...config, secondaryOrder: 'asc' })}
                    className={`
                      flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg transition-all
                      ${config.secondaryOrder === 'asc'
                        ? 'bg-purple-600 text-white'
                        : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                      }
                    `}
                  >
                    <ArrowUp className="w-4 h-4" />
                    Ascending
                  </button>
                  <button
                    onClick={() => setConfig({ ...config, secondaryOrder: 'desc' })}
                    className={`
                      flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg transition-all
                      ${config.secondaryOrder === 'desc'
                        ? 'bg-purple-600 text-white'
                        : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                      }
                    `}
                  >
                    <ArrowDown className="w-4 h-4" />
                    Descending
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex gap-3 p-6 border-t border-zinc-800">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleApply}
            className="flex-1 px-4 py-2.5 rounded-lg bg-purple-600 hover:bg-purple-700 text-white transition-colors"
          >
            Apply Sort
          </button>
        </div>
      </div>
    </div>
  );
}
