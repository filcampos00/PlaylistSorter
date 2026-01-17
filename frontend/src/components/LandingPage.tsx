import { YouTubeIcon, SpotifyIcon } from "./Icons";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/components/ThemeProvider";
import { cn } from "@/lib/utils";

interface LandingPageProps {
  onConnectYouTube?: () => void;
}

export function LandingPage({ onConnectYouTube }: LandingPageProps) {
  const { theme } = useTheme();
  const isLight = theme === "light";

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Diagonal gradient background */}
      <div
        className={cn(
          "absolute inset-0 bg-gradient-to-br",
          isLight
            ? "from-purple-100 via-white to-pink-100"
            : "from-zinc-950 via-zinc-900 to-purple-950"
        )}
      />

      {/* Theme Toggle */}
      <div className="absolute right-4 top-4 z-20">
        <ThemeToggle />
      </div>

      {/* Hero Content */}
      <div className="relative z-10 flex min-h-screen flex-col items-center justify-center px-4 text-center">
        {/* Badge */}
        <div
          className={cn(
            "mb-8 inline-block rounded-full border px-4 py-2 text-sm font-medium backdrop-blur-lg",
            isLight
              ? "border-purple-200 bg-purple-100/50 text-purple-600"
              : "border-white/10 bg-white/5 text-purple-400"
          )}
        >
          ✨ Finally, a way to sort playlists
        </div>

        {/* Title */}
        <h1
          className={cn(
            "mb-6 text-5xl font-bold leading-tight tracking-tight md:text-6xl",
            isLight ? "text-zinc-900" : "text-white"
          )}
        >
          Tame Your <br />
          <span
            className={cn(
              "bg-gradient-to-r bg-clip-text text-transparent",
              isLight
                ? "from-purple-500 to-purple-700"
                : "from-purple-300 to-purple-500"
            )}
          >
            Music Library
          </span>
        </h1>

        {/* Subtitle */}
        <p
          className={cn(
            "mb-10 max-w-xl text-lg",
            isLight ? "text-zinc-600" : "text-zinc-400"
          )}
        >
          Sort your massive playlists on YouTube Music and Spotify. Stop
          scrolling endlessly to find that one song.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-wrap justify-center gap-4">
          <Button
            size="lg"
            onClick={onConnectYouTube}
            className="border border-zinc-300 bg-white text-black shadow-[0_0_20px_rgba(255,0,85,0.4)] hover:bg-zinc-50 hover:shadow-[0_0_30px_rgba(255,0,85,0.6)]"
          >
            <YouTubeIcon />
            Connect YouTube Music
          </Button>
          <Button
            size="lg"
            disabled
            title="Coming soon"
            className="border border-zinc-300 bg-white text-black opacity-50 shadow-[0_0_20px_rgba(29,185,84,0.2)] cursor-not-allowed"
          >
            <SpotifyIcon />
            Connect Spotify
          </Button>
        </div>
      </div>
    </div>
  );
}
