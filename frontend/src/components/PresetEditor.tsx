import { cn } from "@/lib/utils";
import type { SortLevel, SortDirection } from "@/types";
import { SORT_ATTRIBUTE_LABELS, SORT_DIRECTION_LABELS } from "@/types";

interface PresetEditorProps {
    levels: SortLevel[];
    onChange: (levels: SortLevel[]) => void;
}

export function PresetEditor({ levels, onChange }: PresetEditorProps) {
    const handleDirectionChange = (index: number, direction: SortDirection) => {
        const updated = [...levels];
        updated[index] = { ...updated[index], direction };
        onChange(updated);
    };

    return (
        <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
                Adjust the sorting direction for each level:
            </p>

            {levels.map((level, index) => (
                <div
                    key={index}
                    className="rounded-lg border border-border bg-secondary/30 p-3"
                >
                    <div className="mb-2 flex items-center gap-2">
                        <div className="flex h-6 w-6 items-center justify-center rounded-full border border-primary/50 bg-primary/20 text-xs font-medium text-primary">
                            {index + 1}
                        </div>
                        <span className="text-sm font-medium">
                            {SORT_ATTRIBUTE_LABELS[level.attribute]}
                        </span>
                    </div>

                    {/* Direction Toggle Buttons */}
                    <div className="flex gap-2">
                        <button
                            type="button"
                            onClick={() => handleDirectionChange(index, "asc")}
                            className={cn(
                                "flex-1 rounded-lg px-3 py-2 text-sm transition-all",
                                level.direction === "asc"
                                    ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                                    : "bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground"
                            )}
                        >
                            {SORT_DIRECTION_LABELS[level.attribute].asc}
                        </button>
                        <button
                            type="button"
                            onClick={() => handleDirectionChange(index, "desc")}
                            className={cn(
                                "flex-1 rounded-lg px-3 py-2 text-sm transition-all",
                                level.direction === "desc"
                                    ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                                    : "bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground"
                            )}
                        >
                            {SORT_DIRECTION_LABELS[level.attribute].desc}
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );
}
