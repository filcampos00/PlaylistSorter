import { LogOut } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Button } from "@/components/ui/button";

interface HeaderProps {
    userName?: string;
    onLogout: () => void;
}

export function Header({ userName, onLogout }: HeaderProps) {
    return (
        <header className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
                {/* Logo */}
                <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
                        <span className="text-lg">🎵</span>
                    </div>
                    <span className="text-lg font-semibold">Playlist Sorter</span>
                </div>

                {/* Right side */}
                <div className="flex items-center gap-4">
                    <ThemeToggle />

                    {userName && (
                        <span className="hidden text-sm text-muted-foreground sm:block">
                            {userName}
                        </span>
                    )}

                    <Button variant="ghost" size="sm" onClick={onLogout}>
                        <LogOut className="h-4 w-4" />
                        <span className="hidden sm:inline">Logout</span>
                    </Button>
                </div>
            </div>
        </header>
    );
}
