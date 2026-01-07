import { useState } from "react";
import type { SortAttribute, SortLevel } from "../types";
import {
  SORT_ATTRIBUTE_LABELS,
  SORT_DIRECTION_LABELS,
  PRESET_DISCOGRAPHY,
  PRESET_LATEST_RELEASES,
  PRESET_FAVOURITES_FIRST,
} from "../types";
import "./SortLevelBuilder.css";

interface SortLevelBuilderProps {
  value: SortLevel[];
  onChange: (levels: SortLevel[]) => void;
  disabled?: boolean;
}

const ALL_ATTRIBUTES: SortAttribute[] = [
  "artist_name",
  "album_name",
  "album_release_date",
  "track_number",
  "favourite_artists",
  "title",
  "duration",
];

const PRESETS = [
  {
    id: "discography",
    label: "📀 Discography",
    description: "Artist A-Z → Oldest albums → Track order",
    levels: PRESET_DISCOGRAPHY,
  },
  {
    id: "latest",
    label: "🆕 Latest Releases",
    description: "Newest albums first → Track order",
    levels: PRESET_LATEST_RELEASES,
  },
  {
    id: "favourites",
    label: "⭐ Favourites First",
    description: "Your favourite artists at the top",
    levels: PRESET_FAVOURITES_FIRST,
  },
];

/**
 * Determines which attributes are valid for a given position based on preceding levels.
 * Rules:
 * 1. Track number requires album context (album_name or album_release_date before it)
 * 2. Album attributes can't come after track number
 * 3. Duplicates are allowed (for swapping)
 * 4. favourite_artists must be at L1 (index 0) only
 */
const getSelectableAttributes = (
  index: number,
  currentLevels: SortLevel[],
  currentAttr: SortAttribute
): SortAttribute[] => {
  const precedingAttrs = currentLevels.slice(0, index).map((l) => l.attribute);

  const hasAlbumContext =
    precedingAttrs.includes("album_name") ||
    precedingAttrs.includes("album_release_date");
  const hasTrackNumber = precedingAttrs.includes("track_number");

  return ALL_ATTRIBUTES.filter((attr) => {
    // Always show current attribute
    if (attr === currentAttr) return true;

    // Rule 4: favourite_artists must be at L1 only
    if (attr === "favourite_artists" && index !== 0) return false;

    // Rule 1: Track number needs album context
    if (attr === "track_number" && !hasAlbumContext) return false;

    // Rule 2: Album attributes can't come after track number
    if (
      hasTrackNumber &&
      (attr === "album_name" || attr === "album_release_date")
    ) {
      return false;
    }

    // Show all other attributes (including used ones - for swapping)
    return true;
  });
};

const MAX_SORT_LEVELS = 4;

const getValidAttributesForNewLevel = (
  currentLevels: SortLevel[]
): SortAttribute[] => {
  // Max 4 levels
  if (currentLevels.length >= MAX_SORT_LEVELS) return [];

  const usedAttrs = new Set(currentLevels.map((l) => l.attribute));
  const allAttrs = currentLevels.map((l) => l.attribute);
  const newIndex = currentLevels.length;

  const hasAlbumContext =
    allAttrs.includes("album_name") || allAttrs.includes("album_release_date");
  const hasTrackNumber = allAttrs.includes("track_number");

  return ALL_ATTRIBUTES.filter((attr) => {
    // Rule 3: No duplicates
    if (usedAttrs.has(attr)) return false;

    // Rule 4: favourite_artists only at L1
    if (attr === "favourite_artists" && newIndex !== 0) return false;

    // Rule 1: Track number needs album context
    if (attr === "track_number" && !hasAlbumContext) return false;

    // Rule 2: Album attributes can't come after track number
    if (
      hasTrackNumber &&
      (attr === "album_name" || attr === "album_release_date")
    ) {
      return false;
    }
    return true;
  });
};

const validateLevels = (levels: SortLevel[]): SortLevel[] => {
  return levels.filter((level, idx) => {
    if (level.attribute !== "track_number") return true;
    const preceding = levels.slice(0, idx).map((l) => l.attribute);
    return (
      preceding.includes("album_name") ||
      preceding.includes("album_release_date")
    );
  });
};



/** Check if levels match a preset's structure (attributes only, ignoring directions) */
const levelsMatchStructure = (a: SortLevel[], b: SortLevel[]): boolean => {
  if (a.length !== b.length) return false;
  return a.every((level, i) => level.attribute === b[i].attribute);
};

export const SortLevelBuilder = ({
  value,
  onChange,
  disabled = false,
}: SortLevelBuilderProps) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Check which preset (if any) matches current levels (structure, ignoring direction)
  const activePresetByStructure = PRESETS.find((p) =>
    levelsMatchStructure(value, p.levels)
  );

  const applyPreset = (levels: SortLevel[]) => {
    onChange([...levels]);
    setShowAdvanced(false);
  };

  const addLevel = () => {
    if (value.length >= MAX_SORT_LEVELS) return;
    const available = getValidAttributesForNewLevel(value);
    if (available.length === 0) return;
    onChange([...value, { attribute: available[0], direction: "asc" }]);
  };

  const removeLevel = (index: number) => {
    const newLevels = value.filter((_, i) => i !== index);
    onChange(validateLevels(newLevels));
  };

  const updateLevel = (index: number, updates: Partial<SortLevel>) => {
    let newLevels = [...value];

    // If changing attribute, check if it's used elsewhere and swap
    if (updates.attribute) {
      const newAttr = updates.attribute;
      const otherIndex = newLevels.findIndex(
        (l, i) => i !== index && l.attribute === newAttr
      );

      if (otherIndex !== -1) {
        // Swap: give the other level our current attribute
        newLevels[otherIndex] = {
          ...newLevels[otherIndex],
          attribute: newLevels[index].attribute,
        };
      }
    }

    // Apply the update
    newLevels = newLevels.map((level, i) =>
      i === index ? { ...level, ...updates } : level
    );

    onChange(validateLevels(newLevels));
  };

  const updateDirection = (index: number, direction: "asc" | "desc") => {
    const newLevels = value.map((level, i) =>
      i === index ? { ...level, direction } : level
    );
    onChange(newLevels);
  };

  const canAddMoreLevels = getValidAttributesForNewLevel(value).length > 0;

  return (
    <div className="sort-level-builder">
      {/* Simple View: Preset Buttons + Editable Directions */}
      {!showAdvanced && (
        <div className="preset-section">
          <div className="preset-grid">
            {PRESETS.map((preset) => (
              <button
                key={preset.id}
                type="button"
                className={`preset-card ${activePresetByStructure?.id === preset.id ? "active" : ""}`}
                onClick={() => applyPreset(preset.levels)}
                disabled={disabled}
              >
                <span className="preset-label">{preset.label}</span>
                <span className="preset-description">{preset.description}</span>
              </button>
            ))}
          </div>

          {/* Editable directions for active preset */}
          {activePresetByStructure && (
            <div className="preset-directions">
              <div className="preset-directions-header">
                <span className="preset-directions-title">
                  {activePresetByStructure.label} sorting:
                </span>
              </div>
              <div className="preset-directions-list">
                {value.map((level, index) => (
                  <div key={index} className="preset-direction-row">
                    <span className="preset-attr-label">
                      {SORT_ATTRIBUTE_LABELS[level.attribute]}
                    </span>
                    <select
                      className="direction-select-compact"
                      value={level.direction}
                      onChange={(e) =>
                        updateDirection(index, e.target.value as "asc" | "desc")
                      }
                      disabled={disabled}
                    >
                      <option value="asc">
                        {SORT_DIRECTION_LABELS[level.attribute].asc}
                      </option>
                      <option value="desc">
                        {SORT_DIRECTION_LABELS[level.attribute].desc}
                      </option>
                    </select>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Advanced View: Multi-level Builder */}
      {showAdvanced && (
        <div className="advanced-builder">
          <div className="sort-levels-list">
            {value.map((level, index) => {
              const validAttrs = getSelectableAttributes(
                index,
                value,
                level.attribute
              );

              return (
                <div key={index} className="sort-level-row">
                  <span className="level-number">{index + 1}.</span>

                  <select
                    className="attribute-select"
                    value={level.attribute}
                    onChange={(e) =>
                      updateLevel(index, {
                        attribute: e.target.value as SortAttribute,
                      })
                    }
                    disabled={disabled}
                  >
                    {validAttrs.map((attr) => (
                      <option key={attr} value={attr}>
                        {SORT_ATTRIBUTE_LABELS[attr]}
                      </option>
                    ))}
                  </select>

                  <select
                    className="direction-select"
                    value={level.direction}
                    onChange={(e) =>
                      updateLevel(index, {
                        direction: e.target.value as "asc" | "desc",
                      })
                    }
                    disabled={disabled}
                  >
                    <option value="asc">
                      {SORT_DIRECTION_LABELS[level.attribute].asc}
                    </option>
                    <option value="desc">
                      {SORT_DIRECTION_LABELS[level.attribute].desc}
                    </option>
                  </select>

                  <button
                    type="button"
                    className="remove-level-btn"
                    onClick={() => removeLevel(index)}
                    disabled={disabled || value.length <= 1}
                    title="Remove level"
                  >
                    ✕
                  </button>
                </div>
              );
            })}
          </div>

          {canAddMoreLevels && (
            <button
              type="button"
              className="add-level-btn"
              onClick={addLevel}
              disabled={disabled}
            >
              + Add Sort Level
            </button>
          )}
        </div>
      )}

      {/* Toggle between Simple and Advanced */}
      <button
        type="button"
        className="mode-toggle"
        onClick={() => setShowAdvanced(!showAdvanced)}
        disabled={disabled}
      >
        {showAdvanced ? "← Use Presets" : "⚙️ Custom Sort"}
      </button>
    </div>
  );
};
