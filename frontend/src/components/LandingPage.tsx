import React from 'react';
import './LandingPage.css';

const YouTubeIcon = () => (
    <svg viewBox="0 0 176 176" width="20" height="20" fill="none">
        <circle cx="88" cy="88" r="88" fill="#FF0000" />
        <path fill="#FFFFFF" d="M88 46c23.1 0 42 18.8 42 42s-18.8 42-42 42-42-18.8-42-42 18.9-42 42-42m0-4c-25.4 0-46 20.6-46 46s20.6 46 46 46 46-20.6 46-46-20.6-46-46-46" />
        <path fill="#FFFFFF" d="m72 111 39-24-39-22z" />
    </svg>
);

const SpotifyIcon = () => (
    <svg viewBox="0 0 24 24" width="20" height="20" fill="none">
        <path fill="#1DB954" d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S16.666 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z" />
    </svg>
);

export const LandingPage: React.FC = () => {
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
                    Sort your massive playlists on YouTube Music and Spotify.
                    Stop scrolling endlessly to find that one song.
                </p>

                <div className="cta-group fade-in delay-300">
                    <button className="btn btn-youtube">
                        <YouTubeIcon />
                        Connect YouTube Music
                    </button>
                    <button className="btn btn-spotify">
                        <SpotifyIcon />
                        Connect Spotify
                    </button>
                </div>

            </div>
        </div>
    );
};
