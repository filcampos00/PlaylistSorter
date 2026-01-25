import * as React from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

interface ModalProps {
    open: boolean;
    onClose: () => void;
    children: React.ReactNode;
    className?: string;
    preventClose?: boolean;
}

export function Modal({ open, onClose, children, className, preventClose }: ModalProps) {
    // Close on escape key (unless preventClose is true)
    React.useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === "Escape" && !preventClose) onClose();
        };

        if (open) {
            document.addEventListener("keydown", handleEscape);
            document.body.style.overflow = "hidden";
        }

        return () => {
            document.removeEventListener("keydown", handleEscape);
            document.body.style.overflow = "";
        };
    }, [open, onClose, preventClose]);

    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                onClick={preventClose ? undefined : onClose}
            />

            {/* Modal Content */}
            <div
                className={cn(
                    "relative z-10 flex w-full max-w-2xl max-h-[90vh] flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-2xl",
                    "animate-in fade-in-0 zoom-in-95 duration-200",
                    className
                )}
            >
                {children}
            </div>
        </div>
    );
}

interface ModalHeaderProps {
    children: React.ReactNode;
    onClose?: () => void;
    className?: string;
    disabled?: boolean;
}

export function ModalHeader({ children, onClose, className, disabled }: ModalHeaderProps) {
    return (
        <div
            className={cn(
                "flex items-start justify-between border-b border-border p-6",
                className
            )}
        >
            <div>{children}</div>
            {onClose && (
                <button
                    onClick={disabled ? undefined : onClose}
                    disabled={disabled}
                    className={cn(
                        "text-muted-foreground hover:text-foreground transition-colors",
                        disabled && "opacity-50 cursor-not-allowed"
                    )}
                >
                    <X className="h-5 w-5" />
                </button>
            )}
        </div>
    );
}

interface ModalContentProps {
    children: React.ReactNode;
    className?: string;
}

export function ModalContent({ children, className }: ModalContentProps) {
    return (
        <div className={cn("flex-1 overflow-y-auto p-6", className)}>
            {children}
        </div>
    );
}

interface ModalFooterProps {
    children: React.ReactNode;
    className?: string;
}

export function ModalFooter({ children, className }: ModalFooterProps) {
    return (
        <div
            className={cn(
                "flex items-center gap-3 border-t border-border p-6",
                className
            )}
        >
            {children}
        </div>
    );
}
