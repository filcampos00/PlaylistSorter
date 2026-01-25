import { Plus, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import type { SortLevel, SortAttribute, SortDirection } from "@/types";
import { SORT_ATTRIBUTE_LABELS, SORT_DIRECTION_LABELS } from "@/types";

interface CustomSortBuilderProps {
    levels: SortLevel[];
    onChange: (levels: SortLevel[]) => void;
}

const MAX_LEVELS = 3;

const ALL_ATTRIBUTES: SortAttribute[] = [
    "title",
    "duration",
    "artist_name",
    "album_name",
    "album_release_date",
    "track_number",
    "favourite_artists",
];

// Validation helper functions
const hasAlbumContext = (levels: SortLevel[]): boolean => {
    return levels.some(
        (l) =>
            l.attribute === "album_name" ||
            l.attribute === "album_release_date" ||
            l.attribute === "artist_name"
    );
};

const hasTrackNumber = (levels: SortLevel[]): boolean => {
    return levels.some((l) => l.attribute === "track_number");
};

const getAvailableAttributes = (
    levels: SortLevel[],
    levelIndex: number
): SortAttribute[] => {
    const usedAttributes = levels.map((l) => l.attribute);
    const previousLevels = levels.slice(0, levelIndex);

    return ALL_ATTRIBUTES.filter((attr) => {
        // No duplicates
        if (usedAttributes.includes(attr)) return false;

        // favourite_artists only at Level 1
        if (attr === "favourite_artists" && levelIndex !== 0) return false;

        // track_number requires prior album context
        if (attr === "track_number" && !hasAlbumContext(previousLevels))
            return false;

        // No album attributes after track_number
        if (hasTrackNumber(previousLevels)) {
            if (["album_name", "album_release_date", "artist_name"].includes(attr)) {
                return false;
            }
        }

        return true;
    });
};

export function CustomSortBuilder({ levels, onChange }: CustomSortBuilderProps) {
    const handleAddLevel = () => {
        if (levels.length >= MAX_LEVELS) return;

        const available = getAvailableAttributes(levels, levels.length);
        if (available.length === 0) return;

        onChange([...levels, { attribute: available[0], direction: "asc" }]);
    };

    const handleRemoveLevel = (index: number) => {
        onChange(levels.filter((_, i) => i !== index));
    };

    const handleAttributeChange = (index: number, attribute: SortAttribute) => {
        const updated = [...levels];
        updated[index] = { attribute, direction: updated[index].direction };
        onChange(updated);
    };

    const handleDirectionChange = (index: number, direction: SortDirection) => {
        const updated = [...levels];
        updated[index] = { ...updated[index], direction };
        onChange(updated);
    };

    const canAddMore = levels.length < MAX_LEVELS;
    const availableForNext = getAvailableAttributes(levels, levels.length);

    // Empty state
    if (levels.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-12 text-center">
                <p className="mb-2 text-muted-foreground">
                    Build your own sorting criteria
                </p>
                <p className="mb-6 text-sm text-muted-foreground">Add up to 3 levels</p>
                <Button onClick={handleAddLevel}>
                    <Plus className="h-4 w-4" />
                    Add First Level
                </Button>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {levels.map((level, index) => {
                const availableForThis = getAvailableAttributes(
                    levels.filter((_, i) => i !== index),
                    index
                );

                return (
                    <div
                        key={index}
                        className="rounded-lg border border-border bg-secondary/30 p-4"
                    >
                        <div className="mb-3 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="flex h-7 w-7 items-center justify-center rounded-full border border-primary/50 bg-primary/20 text-sm font-medium text-primary">
                                    {index + 1}
                                </div>
                                <span className="text-sm text-muted-foreground">
                                    Level {index + 1}
                                </span>
                            </div>
                            <button
                                onClick={() => handleRemoveLevel(index)}
                                className="text-muted-foreground hover:text-destructive transition-colors"
                            >
                                <Trash2 className="h-4 w-4" />
                            </button>
                        </div>

                        {/* Attribute Select */}
                        <select
                            value={level.attribute}
                            onChange={(e) =>
                                handleAttributeChange(index, e.target.value as SortAttribute)
                            }
                            className="mb-3 w-full rounded-lg border border-border bg-muted px-4 py-2.5 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                            {availableForThis.map((attr) => (
                                <option key={attr} value={attr}>
                                    {SORT_ATTRIBUTE_LABELS[attr]}
                                </option>
                            ))}
                        </select>

                        {/* Direction Toggle */}
                        <div className="flex gap-2">
                            <button
                                type="button"
                                onClick={() => handleDirectionChange(index, "asc")}
                                className={cn(
                                    "flex-1 rounded-lg px-4 py-2.5 text-sm transition-all",
                                    level.direction === "asc"
                                        ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                                )}
                            >
                                {SORT_DIRECTION_LABELS[level.attribute].asc}
                            </button>
                            <button
                                type="button"
                                onClick={() => handleDirectionChange(index, "desc")}
                                className={cn(
                                    "flex-1 rounded-lg px-4 py-2.5 text-sm transition-all",
                                    level.direction === "desc"
                                        ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                                )}
                            >
                                {SORT_DIRECTION_LABELS[level.attribute].desc}
                            </button>
                        </div>
                    </div>
                );
            })}

            {/* Add Level Button */}
            {canAddMore && availableForNext.length > 0 && (
                <button
                    onClick={handleAddLevel}
                    className="flex w-full items-center justify-center gap-2 rounded-lg border-2 border-dashed border-border py-3 text-muted-foreground transition-all hover:border-primary/50 hover:bg-primary/5 hover:text-primary"
                >
                    <Plus className="h-4 w-4" />
                    Add Level {levels.length + 1}
                </button>
            )}
        </div>
    );
}
