import { useState } from "react";
import { API_BASE_URL } from "../config";
import type { LastFmPeriod, TopArtistsResponse } from "../types";
import "./FavouriteArtistsInput.css";

interface FavouriteArtistsInputProps {
  value: string[];
  onChange: (artists: string[]) => void;
  disabled?: boolean;
}

const PERIOD_LABELS: Record<LastFmPeriod, string> = {
  overall: "All Time",
  "12month": "Last Year",
  "6month": "Last 6 Months",
  "3month": "Last 3 Months",
  "1month": "Last Month",
  "7day": "Last Week",
};

type InputMethod = "manual" | "lastfm";

export const FavouriteArtistsInput = ({
  value,
  onChange,
  disabled = false,
}: FavouriteArtistsInputProps) => {
  const [inputMethod, setInputMethod] = useState<InputMethod>("manual");
  const [manualInput, setManualInput] = useState(value.join("\n"));

  // Last.fm state
  const [lastfmUsername, setLastfmUsername] = useState("");
  const [lastfmPeriod, setLastfmPeriod] = useState<LastFmPeriod>("overall");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleManualInputChange = (text: string) => {
    setManualInput(text);
    // Parse newline-separated artists (supports artists with commas in names)
    const artists = text
      .split("\n")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);
    onChange(artists);
  };

  const handleFetchLastFm = async () => {
    if (!lastfmUsername.trim()) {
      setError("Please enter a Last.fm username");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/lastfm/top-artists`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: lastfmUsername.trim(),
          period: lastfmPeriod,
          limit: 50,
        }),
      });

      const data: TopArtistsResponse = await response.json();

      if (data.success) {
        onChange(data.artists);
        setManualInput(data.artists.join("\n"));
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="favourite-artists-input">
      {/* Method Toggle */}
      <div className="method-toggle">
        <button
          type="button"
          className={`toggle-btn ${inputMethod === "manual" ? "active" : ""}`}
          onClick={() => setInputMethod("manual")}
          disabled={disabled}
        >
          ✏️ Manual
        </button>
        <button
          type="button"
          className={`toggle-btn ${inputMethod === "lastfm" ? "active" : ""}`}
          onClick={() => setInputMethod("lastfm")}
          disabled={disabled}
        >
          🎧 Last.fm
        </button>
      </div>

      {/* Manual Input */}
      {inputMethod === "manual" && (
        <div className="manual-input-section">
          <textarea
            className="artists-textarea"
            placeholder="Enter one artist per line, e.g.:&#10;Queen&#10;Metallica&#10;Pink Floyd"
            value={manualInput}
            onChange={(e) => handleManualInputChange(e.target.value)}
            disabled={disabled}
            rows={3}
          />
          {value.length > 0 && (
            <p className="artist-count">{value.length} artists selected</p>
          )}
        </div>
      )}

      {/* Last.fm Input */}
      {inputMethod === "lastfm" && (
        <div className="lastfm-input-section">
          <div className="lastfm-row">
            <input
              type="text"
              className="lastfm-username"
              placeholder="Last.fm username"
              value={lastfmUsername}
              onChange={(e) => setLastfmUsername(e.target.value)}
              disabled={disabled || isLoading}
            />
            <select
              className="lastfm-period"
              value={lastfmPeriod}
              onChange={(e) => setLastfmPeriod(e.target.value as LastFmPeriod)}
              disabled={disabled || isLoading}
            >
              {Object.entries(PERIOD_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
            <button
              type="button"
              className="btn btn-sm fetch-btn"
              onClick={handleFetchLastFm}
              disabled={disabled || isLoading || !lastfmUsername.trim()}
            >
              {isLoading ? "Loading..." : "Fetch"}
            </button>
          </div>

          {error && <p className="error-message">⚠️ {error}</p>}

          {value.length > 0 && (
            <div className="fetched-artists">
              <p className="artist-count">✅ {value.length} artists loaded</p>
              <p className="artist-preview">
                {value.slice(0, 5).join(", ")}
                {value.length > 5 && `, +${value.length - 5} more`}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Info Callout */}
      <div className="info-callout">
        <svg
          className="info-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
        <span className="info-text">
          Non-favourites will be sorted by artist name.
        </span>
      </div>
    </div>
  );
};
