import { useState } from "react";
import { useAuthStore } from "../store";
import { YouTubeIcon } from "../components/Icons";
import "./LoginPage.css";

interface LoginPageProps {
  onBack?: () => void;
}

export const LoginPage = ({ onBack }: LoginPageProps) => {
  const [headersInput, setHeadersInput] = useState("");
  const { login, isLoading, error, clearError } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!headersInput.trim()) return;
    await login(headersInput);
  };

  return (
    <div className="login-page">
      {/* Background Ambience */}
      <div className="bg-orb orb-primary" />
      <div className="bg-orb orb-secondary" />

      <div className="login-container fade-in">
        {onBack && (
          <button className="back-button" onClick={onBack}>
            ← Back
          </button>
        )}
        <div className="login-header">
          <YouTubeIcon size={32} />
          <h1>Connect YouTube Music</h1>
          <p className="login-desc">
            Paste your browser authentication headers to get started.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="headers">Authentication Headers</label>
            <textarea
              id="headers"
              value={headersInput}
              onChange={(e) => {
                setHeadersInput(e.target.value);
                if (error) clearError();
              }}
              placeholder="Paste your browser headers here..."
              rows={8}
              disabled={isLoading}
            />
          </div>

          {error && (
            <div className="error-message fade-in">
              <span>⚠️</span> {error}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-youtube"
            disabled={isLoading || !headersInput.trim()}
          >
            {isLoading ? "Validating..." : "Connect"}
          </button>
        </form>

        <details className="help-section">
          <summary>How to get your headers</summary>
          <div className="help-content">
            <ol>
              <li>
                Open a new tab and go to <strong>Youtube Music</strong>
              </li>
              <li>Open Developer Tools (F12 or Ctrl+Shift+I)</li>
              <li>
                Select the <strong>Network</strong> tab
              </li>
              <li>
                Filter by <code>browse</code> in the filter box
              </li>
              <li>
                Click on any request named <code>browse</code> (left side)
              </li>
              <li>
                Find <strong>Request Headers</strong>
              </li>
              <li>Copy all headers</li>
              <li>Paste them into the box above</li>
            </ol>
            <p className="note">
              Note: Ensure you copy the <em>Request Headers</em>, not Response
              Headers.
            </p>
          </div>
        </details>
      </div>
    </div>
  );
};
