import { useState } from "react";
import { ChevronRight, Check, Shuffle } from "lucide-react";
import { Modal, ModalHeader, ModalContent, ModalFooter } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { PresetEditor } from "@/components/PresetEditor";
import { CustomSortBuilder } from "@/components/CustomSortBuilder";
import { FavouriteArtistsInput } from "@/components/FavouriteArtistsInput";
import { cn } from "@/lib/utils";
import type { SortLevel, Playlist } from "@/types";
import {
    PRESET_DISCOGRAPHY,
    PRESET_LATEST_RELEASES,
    PRESET_FAVOURITES_FIRST,
} from "@/types";

interface SortModalProps {
    open: boolean;
    playlist: Playlist;
    onClose: () => void;
    onSort: (levels: SortLevel[], favouriteArtists?: string[]) => void;
    onShuffle: () => void;
    isSorting: boolean;
}

interface PresetConfig {
    id: string;
    name: string;
    description: string;
    levels: SortLevel[];
}

const PRESETS: PresetConfig[] = [
    {
        id: "discography",
        name: "Discography",
        description: "Organize by artist discography",
        levels: PRESET_DISCOGRAPHY,
    },
    {
        id: "latest_releases",
        name: "Latest Releases",
        description: "Newest albums first",
        levels: PRESET_LATEST_RELEASES,
    },
    {
        id: "favourites_first",
        name: "Favourites First",
        description: "Prioritize your favourite artists",
        levels: PRESET_FAVOURITES_FIRST,
    },
];

type ViewMode = "select" | "preset-edit" | "custom";

export function SortModal({
    open,
    playlist,
    onClose,
    onSort,
    onShuffle,
    isSorting,
}: SortModalProps) {
    const [viewMode, setViewMode] = useState<ViewMode>("select");
    const [selectedPreset, setSelectedPreset] = useState<PresetConfig | null>(null);
    const [editedLevels, setEditedLevels] = useState<SortLevel[]>([]);
    const [customLevels, setCustomLevels] = useState<SortLevel[]>([]);
    const [sortComplete, setSortComplete] = useState(false);

    // Favourite artists state
    const [favouriteArtists, setFavouriteArtists] = useState<string[]>([]);

    // Check if current levels include favourite_artists
    const hasFavouritesLevel = (levels: SortLevel[]) =>
        levels.some((l) => l.attribute === "favourite_artists");

    const handlePresetSelect = (preset: PresetConfig) => {
        setSelectedPreset(preset);
        setEditedLevels([...preset.levels]);
        setViewMode("preset-edit");
        // Reset favourite artists when selecting a new preset
        setFavouriteArtists([]);
    };

    const handleCustomClick = () => {
        setViewMode("custom");
        setCustomLevels([]);
        setFavouriteArtists([]);
    };

    const handleApplySort = () => {
        const levels = viewMode === "preset-edit" ? editedLevels : customLevels;
        const artists = hasFavouritesLevel(levels) ? favouriteArtists : undefined;
        onSort(levels, artists);
    };

    const handleBack = () => {
        setViewMode("select");
        setSelectedPreset(null);
        setEditedLevels([]);
        setFavouriteArtists([]);
    };

    const handleClose = () => {
        setViewMode("select");
        setSelectedPreset(null);
        setEditedLevels([]);
        setCustomLevels([]);
        setFavouriteArtists([]);
        setSortComplete(false);
        onClose();
    };

    // Check if can apply - favourites preset requires at least one artist
    const currentLevels = viewMode === "preset-edit" ? editedLevels : customLevels;
    const needsFavourites = hasFavouritesLevel(currentLevels);
    const canApply =
        (viewMode === "preset-edit" && (!needsFavourites || favouriteArtists.length > 0)) ||
        (viewMode === "custom" && customLevels.length > 0 && (!needsFavourites || favouriteArtists.length > 0));

    return (
        <Modal open={open} onClose={handleClose} preventClose={isSorting}>
            <ModalHeader onClose={handleClose} disabled={isSorting}>
                <h2 className="text-xl font-semibold">
                    {viewMode === "select" && "Sort Playlist"}
                    {viewMode === "preset-edit" && selectedPreset?.name}
                    {viewMode === "custom" && "Custom Sort"}
                </h2>
                <p className="text-sm text-muted-foreground">
                    {playlist.title} • {playlist.track_count} tracks
                </p>
            </ModalHeader>

            <ModalContent>
                {sortComplete ? (
                    <div className="flex flex-col items-center justify-center py-12">
                        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-success">
                            <Check className="h-8 w-8 text-white" />
                        </div>
                        <h3 className="mb-2 text-lg font-semibold">Playlist Sorted!</h3>
                        <p className="text-center text-muted-foreground">
                            Your playlist has been reorganized successfully
                        </p>
                    </div>
                ) : (
                    <>
                        {/* Preset Selection View */}
                        {viewMode === "select" && (
                            <div className="space-y-3">
                                <p className="text-sm text-muted-foreground">
                                    Choose a preset or create your own sorting rules:
                                </p>

                                {/* Preset options */}
                                {PRESETS.map((preset) => (
                                    <button
                                        key={preset.id}
                                        onClick={() => handlePresetSelect(preset)}
                                        className="group w-full rounded-xl border border-border bg-secondary/30 p-5 text-left transition-all hover:border-purple-500 hover:bg-secondary/50"
                                    >
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <h3 className="font-semibold transition-colors group-hover:text-primary">
                                                    {preset.name}
                                                </h3>
                                                <p className="text-sm text-muted-foreground">
                                                    {preset.description}
                                                </p>
                                            </div>
                                            <ChevronRight className="h-5 w-5 text-muted-foreground transition-colors group-hover:text-primary" />
                                        </div>
                                    </button>
                                ))}

                                {/* Custom Sort option */}
                                <button
                                    onClick={handleCustomClick}
                                    className="group w-full rounded-xl border border-border bg-secondary/30 p-5 text-left transition-all hover:border-purple-500 hover:bg-secondary/50"
                                >
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <h3 className="font-semibold transition-colors group-hover:text-primary">
                                                Custom Sort
                                            </h3>
                                            <p className="text-sm text-muted-foreground">
                                                Build your own sorting criteria
                                            </p>
                                        </div>
                                        <ChevronRight className="h-5 w-5 text-muted-foreground transition-colors group-hover:text-primary" />
                                    </div>
                                </button>

                                {/* Shuffle option */}
                                <button
                                    onClick={onShuffle}
                                    disabled={isSorting}
                                    className={cn(
                                        "group w-full rounded-xl border border-border bg-secondary/30 p-5 text-left transition-all hover:border-purple-500 hover:bg-secondary/50",
                                        isSorting && "opacity-50 cursor-not-allowed"
                                    )}
                                >
                                    <div className="flex items-center gap-3">
                                        <Shuffle className="h-5 w-5 text-muted-foreground transition-colors group-hover:text-primary" />
                                        <div>
                                            <h3 className="font-semibold transition-colors group-hover:text-primary">Shuffle</h3>
                                            <p className="text-sm text-muted-foreground">
                                                Randomize the playlist order
                                            </p>
                                        </div>
                                    </div>
                                </button>
                            </div>
                        )}

                        {/* Preset Editing View */}
                        {viewMode === "preset-edit" && selectedPreset && (
                            <div className="space-y-4">
                                <PresetEditor
                                    levels={editedLevels}
                                    onChange={setEditedLevels}
                                />

                                {/* Show FavouriteArtistsInput if preset uses favourite_artists */}
                                {hasFavouritesLevel(editedLevels) && (
                                    <div className="mt-4 pt-4 border-t border-border">
                                        <h4 className="text-sm font-medium mb-3">Your Favourite Artists</h4>
                                        <FavouriteArtistsInput
                                            value={favouriteArtists}
                                            onChange={setFavouriteArtists}
                                            disabled={isSorting}
                                        />
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Custom Sort Builder View */}
                        {viewMode === "custom" && (
                            <div className="space-y-4">
                                <CustomSortBuilder
                                    levels={customLevels}
                                    onChange={setCustomLevels}
                                />

                                {/* Show FavouriteArtistsInput if custom levels include favourite_artists */}
                                {hasFavouritesLevel(customLevels) && (
                                    <div className="mt-4 pt-4 border-t border-border">
                                        <h4 className="text-sm font-medium mb-3">Your Favourite Artists</h4>
                                        <FavouriteArtistsInput
                                            value={favouriteArtists}
                                            onChange={setFavouriteArtists}
                                            disabled={isSorting}
                                        />
                                    </div>
                                )}
                            </div>
                        )}
                    </>
                )}
            </ModalContent>

            {!sortComplete && (
                <ModalFooter>
                    {viewMode !== "select" && (
                        <Button variant="ghost" onClick={handleBack} disabled={isSorting}>
                            ← Back
                        </Button>
                    )}
                    <div className="flex-1" />
                    <Button variant="secondary" onClick={handleClose} disabled={isSorting}>
                        Cancel
                    </Button>
                    {viewMode !== "select" && (
                        <Button onClick={handleApplySort} disabled={!canApply || isSorting}>
                            {isSorting ? "Sorting..." : "Apply Sort"}
                        </Button>
                    )}
                </ModalFooter>
            )}
        </Modal>
    );
}
