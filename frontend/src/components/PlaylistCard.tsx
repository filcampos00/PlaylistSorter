import { useState } from "react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface PlaylistCardProps {
    id: string;
    name: string;
    trackCount: number | null;
    thumbnailUrl?: string;
    isSelected?: boolean;
    onSelect: () => void;
}

export function PlaylistCard({
    name,
    trackCount,
    thumbnailUrl,
    isSelected,
    onSelect,
}: PlaylistCardProps) {
    const [imageError, setImageError] = useState(false);

    return (
        <Card
            className={cn(
                "group relative cursor-pointer overflow-hidden transition-all hover:-translate-y-1 hover:shadow-lg hover:shadow-primary/10",
                isSelected && "ring-2 ring-primary shadow-lg shadow-primary/20"
            )}
            onClick={onSelect}
        >
            {/* Thumbnail */}
            <div className="relative aspect-square overflow-hidden bg-muted">
                {thumbnailUrl && !imageError ? (
                    <img
                        src={thumbnailUrl}
                        alt={name}
                        className="h-full w-full object-cover transition-transform group-hover:scale-105"
                        onError={() => setImageError(true)}
                    />
                ) : (
                    // Fallback placeholder - centered emoji
                    <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-muted to-background text-4xl">
                        🎵
                    </div>
                )}

                {/* Hover overlay with Sort button */}
                <div className="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 transition-opacity group-hover:opacity-100">
                    <Button size="sm" className="shadow-xl">
                        Sort Playlist
                    </Button>
                </div>
            </div>

            {/* Info */}
            <div className="p-4">
                <h3 className="truncate font-semibold">{name}</h3>
                {trackCount !== null && (
                    <p className="text-sm text-muted-foreground">{trackCount} tracks</p>
                )}
            </div>

            {/* Selected badge */}
            {isSelected && (
                <div className="absolute right-2 top-2 rounded-md bg-primary px-2 py-1 text-xs font-medium text-primary-foreground">
                    ✓ Selected
                </div>
            )}
        </Card>
    );
}

// Skeleton loader for playlist cards
export function PlaylistCardSkeleton() {
    return (
        <Card className="overflow-hidden">
            <div className="aspect-square animate-pulse bg-muted" />
            <div className="p-4 space-y-2">
                <div className="h-5 w-3/4 animate-pulse rounded bg-muted" />
                <div className="h-4 w-1/2 animate-pulse rounded bg-muted" />
            </div>
        </Card>
    );
}
