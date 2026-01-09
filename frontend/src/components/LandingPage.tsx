import React from "react";
import { YouTubeIcon, SpotifyIcon } from "./Icons";
import "./LandingPage.css";

interface LandingPageProps {
  onConnectYouTube?: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onConnectYouTube,
}) => {
  return (
    <div className="landing-page">
      {/* Background Ambience */}
      <div className="bg-orb orb-primary" />
      <div className="bg-orb orb-secondary" />

      <div className="hero-content fade-in">
        {/* Hero Section */}
        <div className="badge fade-in">
          <span>✨ Finally, a way to sort playlists</span>
        </div>

        <h1 className="hero-title fade-in delay-100">
          Tame Your <br />
          <span className="highlight-text">Music Library</span>
        </h1>

        <p className="hero-desc fade-in delay-200">
          Sort your massive playlists on YouTube Music and Spotify. Stop
          scrolling endlessly to find that one song.
        </p>

        <div className="cta-group fade-in delay-300">
          <button className="btn btn-youtube" onClick={onConnectYouTube}>
            <YouTubeIcon />
            Connect YouTube Music
          </button>
          <button className="btn btn-spotify" disabled title="Coming soon">
            <SpotifyIcon />
            Connect Spotify
          </button>
        </div>
      </div>
    </div>
  );
};
