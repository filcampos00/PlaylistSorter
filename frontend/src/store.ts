import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { API_BASE_URL } from "./config";

type Page = "landing" | "login";

// Subset of state that gets persisted to sessionStorage
interface PersistedAuthState {
  authHeaders: string | null;
  isAuthenticated: boolean;
  channelName: string | null;
}

interface AuthState extends PersistedAuthState {
  isLoading: boolean;
  error: string | null;
  currentPage: Page;

  login: (headers: string) => Promise<boolean>;
  logout: () => void;
  clearError: () => void;
  setPage: (page: Page) => void;
}

export const useAuthStore = create<AuthState>()(
  persist<AuthState, [], [], PersistedAuthState>(
    (set) => ({
      authHeaders: null,
      isAuthenticated: false,
      channelName: null,
      isLoading: false,
      error: null,
      currentPage: "landing",

      login: async (headers: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch(`${API_BASE_URL}/youtube/auth/test`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ headers_raw: headers }),
          });

          const data = await response.json();

          if (data.success) {
            set({
              authHeaders: headers,
              isAuthenticated: true,
              channelName: data.channel_name,
              isLoading: false,
              error: null,
            });
            return true;
          } else {
            set({
              isLoading: false,
              error: data.message,
            });
            return false;
          }
        } catch (err) {
          set({
            isLoading: false,
            error: err instanceof Error ? err.message : "Connection failed",
          });
          return false;
        }
      },

      logout: () => {
        set({
          authHeaders: null,
          isAuthenticated: false,
          channelName: null,
          error: null,
          currentPage: "landing",
        });
      },

      clearError: () => {
        set({ error: null });
      },

      setPage: (page: Page) => {
        set({ currentPage: page });
      },
    }),
    {
      name: "playlist-sorter-auth",
      storage: createJSONStorage(() => sessionStorage),
      // SECURITY NOTE: Auth headers are stored in sessionStorage which is accessible to JS.
      // This is vulnerable to XSS attacks. Acceptable for local/personal use.
      // For production deployment, implement server-side session storage:
      // 1. POST headers to backend once during login
      // 2. Backend encrypts & stores headers, returns httpOnly session cookie
      // 3. Frontend only holds "authenticated" boolean, not the headers themselves
      //
      // Only persist auth-related state, not UI state like isLoading
      partialize: (state) => ({
        authHeaders: state.authHeaders,
        isAuthenticated: state.isAuthenticated,
        channelName: state.channelName,
      }),
    },
  ),
);
