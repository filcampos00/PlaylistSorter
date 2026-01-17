import { useState } from "react";
import { ArrowLeft, ChevronDown } from "lucide-react";
import { useAuthStore } from "@/store";
import { YouTubeIcon } from "@/components/Icons";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/components/ThemeProvider";
import { cn } from "@/lib/utils";

interface LoginPageProps {
  onBack?: () => void;
}

export function LoginPage({ onBack }: LoginPageProps) {
  const [headersInput, setHeadersInput] = useState("");
  const [showHelp, setShowHelp] = useState(false);
  const { login, isLoading, error, clearError } = useAuthStore();
  const { theme } = useTheme();
  const isLight = theme === "light";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!headersInput.trim()) return;
    await login(headersInput);
  };

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Diagonal gradient background - fixed so it doesn't shift on scroll */}
      <div
        className={cn(
          "fixed inset-0 bg-gradient-to-br",
          isLight
            ? "from-purple-100 via-white to-pink-100"
            : "from-zinc-950 via-zinc-900 to-purple-950"
        )}
      />

      {/* Theme Toggle */}
      <div className="absolute right-4 top-4 z-20">
        <ThemeToggle />
      </div>

      {/* Content - anchored at top with padding instead of centered */}
      <div className="relative z-10 flex min-h-screen flex-col items-center px-4 pt-20 pb-12">
        <div className="w-full max-w-md">
          {/* Card - solid background matching Figma style */}
          <div
            className={cn(
              "rounded-2xl border p-8",
              isLight
                ? "border-zinc-200 bg-white shadow-lg"
                : "border-zinc-800 bg-zinc-900"
            )}
          >
            {/* Back Button - inside card */}
            {onBack && (
              <button
                onClick={onBack}
                className={cn(
                  "mb-6 flex items-center gap-2 text-sm transition-colors",
                  isLight
                    ? "text-zinc-600 hover:text-zinc-900"
                    : "text-zinc-400 hover:text-white"
                )}
              >
                <ArrowLeft className="h-4 w-4" />
                Back
              </button>
            )}

            {/* Header */}
            <div className="mb-8 flex flex-col items-center text-center">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-red-500/10">
                <YouTubeIcon size={28} />
              </div>
              <h1
                className={cn(
                  "text-2xl font-bold",
                  isLight ? "text-zinc-900" : "text-white"
                )}
              >
                Connect YouTube Music
              </h1>
              <p
                className={cn(
                  "mt-2 text-sm",
                  isLight ? "text-zinc-600" : "text-zinc-400"
                )}
              >
                Paste your browser authentication headers to get started.
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label
                  htmlFor="headers"
                  className={cn(
                    "block text-sm font-medium",
                    isLight ? "text-zinc-700" : "text-zinc-300"
                  )}
                >
                  Authentication Headers
                </label>
                <textarea
                  id="headers"
                  value={headersInput}
                  onChange={(e) => {
                    setHeadersInput(e.target.value);
                    if (error) clearError();
                  }}
                  placeholder="Paste your browser headers here..."
                  rows={6}
                  disabled={isLoading}
                  className={cn(
                    "w-full rounded-xl border px-4 py-3 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary",
                    isLight
                      ? "border-zinc-200 bg-zinc-50 text-zinc-900 placeholder:text-zinc-400"
                      : "border-zinc-700 bg-zinc-800 text-white placeholder:text-zinc-500",
                    isLoading && "opacity-50 cursor-not-allowed"
                  )}
                />
              </div>

              {/* Error Message */}
              {error && (
                <div className="rounded-lg border border-red-500/50 bg-red-500/10 px-4 py-3 text-sm text-red-500">
                  ⚠️ {error}
                </div>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                size="lg"
                disabled={isLoading || !headersInput.trim()}
                className="w-full bg-red-500 text-white hover:bg-red-600 disabled:opacity-50"
              >
                {isLoading ? "Validating..." : "Connect"}
              </Button>
            </form>

            {/* Help Section */}
            <div className="mt-6">
              <button
                type="button"
                onClick={() => setShowHelp(!showHelp)}
                className={cn(
                  "flex w-full items-center justify-between rounded-lg px-4 py-3 text-sm transition-colors",
                  isLight
                    ? "bg-zinc-100 text-zinc-700 hover:bg-zinc-200"
                    : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
                )}
              >
                <span>How to get your headers</span>
                <ChevronDown
                  className={cn(
                    "h-4 w-4 transition-transform",
                    showHelp && "rotate-180"
                  )}
                />
              </button>

              {showHelp && (
                <div
                  className={cn(
                    "mt-3 rounded-lg p-4 text-sm",
                    isLight ? "bg-zinc-50 text-zinc-600" : "bg-zinc-800 text-zinc-400"
                  )}
                >
                  <ol className="list-decimal space-y-2 pl-4">
                    <li>
                      Open a new tab and go to <strong>YouTube Music</strong>
                    </li>
                    <li>Open Developer Tools (F12 or Ctrl+Shift+I)</li>
                    <li>
                      Select the <strong>Network</strong> tab
                    </li>
                    <li>
                      Filter by <code className={cn("rounded px-1", isLight ? "bg-zinc-200" : "bg-zinc-700")}>browse</code> in the filter box
                    </li>
                    <li>
                      Click on any request named <code className={cn("rounded px-1", isLight ? "bg-zinc-200" : "bg-zinc-700")}>browse</code>
                    </li>
                    <li>
                      Find <strong>Request Headers</strong>
                    </li>
                    <li>Copy all headers</li>
                    <li>Paste them into the box above</li>
                  </ol>
                  <p className="mt-4 text-xs opacity-75">
                    Note: Ensure you copy the <em>Request Headers</em>, not
                    Response Headers.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
