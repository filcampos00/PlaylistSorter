import { Music2, ArrowDownUp } from 'lucide-react';

interface PlaylistCardProps {
  name: string;
  trackCount: number;
  thumbnail: string;
  onSort: () => void;
}

export function PlaylistCard({ name, trackCount, thumbnail, onSort }: PlaylistCardProps) {
  return (
    <div className="group cursor-pointer">
      <div className="relative aspect-square rounded-xl overflow-hidden bg-gray-100 mb-4 shadow-md ring-1 ring-gray-200">
        <img
          src={thumbnail}
          alt={name}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-black/0 to-black/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        
        {/* Sort button on hover */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onSort();
            }}
            className="flex items-center gap-2 px-6 py-3 rounded-lg bg-purple-600 hover:bg-purple-700 text-white shadow-xl transform scale-90 group-hover:scale-100 transition-all"
          >
            <ArrowDownUp className="w-5 h-5" />
            <span>Sort Playlist</span>
          </button>
        </div>
      </div>
      
      <div className="px-1">
        <h3 className="mb-1 group-hover:text-purple-600 transition-colors truncate">
          {name}
        </h3>
        <p className="text-sm text-gray-500">
          {trackCount} {trackCount === 1 ? 'track' : 'tracks'}
        </p>
      </div>
    </div>
  );
}