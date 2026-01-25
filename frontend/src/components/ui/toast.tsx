import { useEffect, useState } from "react";
import { Check, X, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface Toast {
    id: string;
    type: "success" | "error";
    message: string;
    duration?: number;
}

interface ToastItemProps {
    toast: Toast;
    onDismiss: (id: string) => void;
}

function ToastItem({ toast, onDismiss }: ToastItemProps) {
    useEffect(() => {
        const timer = setTimeout(() => {
            onDismiss(toast.id);
        }, toast.duration || 8000);

        return () => clearTimeout(timer);
    }, [toast.id, toast.duration, onDismiss]);

    return (
        <div
            className={cn(
                "flex items-center gap-3 rounded-xl border px-4 py-3 shadow-lg backdrop-blur-sm animate-in slide-in-from-right-full duration-300",
                toast.type === "success"
                    ? "border-green-500/30 bg-green-950/90 text-green-100"
                    : "border-red-500/30 bg-red-950/90 text-red-100"
            )}
        >
            {toast.type === "success" ? (
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-green-500">
                    <Check className="h-4 w-4 text-white" />
                </div>
            ) : (
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-red-500">
                    <AlertCircle className="h-4 w-4 text-white" />
                </div>
            )}
            <span className="text-sm font-medium">{toast.message}</span>
            <button
                onClick={() => onDismiss(toast.id)}
                className="ml-auto p-1 hover:opacity-70 transition-opacity"
            >
                <X className="h-4 w-4" />
            </button>
        </div>
    );
}

interface ToastContainerProps {
    toasts: Toast[];
    onDismiss: (id: string) => void;
}

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
    if (toasts.length === 0) return null;

    return (
        <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
            {toasts.map((toast) => (
                <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
            ))}
        </div>
    );
}

// Hook for managing toasts
export function useToast() {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const addToast = (type: Toast["type"], message: string, duration?: number) => {
        const id = crypto.randomUUID();
        setToasts((prev) => [...prev, { id, type, message, duration }]);
    };

    const dismissToast = (id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    };

    const success = (message: string, duration?: number) => addToast("success", message, duration);
    const error = (message: string, duration?: number) => addToast("error", message, duration || 10000);

    return { toasts, success, error, dismissToast };
}
