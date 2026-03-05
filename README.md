# PlaylistSorter

A web app to sort and organize your YouTube Music playlists — including by your favourite artists, automatically pulled from your Last.fm listening history.

---

## Features

- Fetch your YouTube Music playlists
- **Multi-level sorting** by:
  - Artist Name, Album Name, Track Title, Duration
  - Album Release Date, Track Number
  - Favourites First (ranked list of preferred artists)
- Sort **presets**: Discography, Latest Releases, Favourites First
- **Custom sort builder** — compose your own sort levels
- **Shuffle** playlists randomly
- **Last.fm integration** — auto-fill your favourite artists from your listening history
- Dark / Light theme

---

## How Authentication Works

YouTube Music does not offer a public API. This app uses the [`ytmusicapi`](https://ytmusicapi.readthedocs.io/) library to interact with it.

`ytmusicapi` supports two authentication methods: OAuth and browser headers. OAuth is currently broken due to a [known issue](https://github.com/sigma67/ytmusicapi/issues/813) with YouTube's InnerTube API (broken since August 2025), and the library maintainer's official recommendation is to use **browser-based authentication** as a workaround.

On the login page, the app walks you through how to copy your request headers from your browser's developer tools. No Google account login or credentials are required.

> **Note:** Headers may expire after ~30 minutes and will need to be re-pasted.

---

## Tech Stack

| Layer    | Technology                                                           |
| -------- | -------------------------------------------------------------------- |
| Frontend | React 19.2, TypeScript 5.9, Vite 7.2, Tailwind CSS 4.1, Zustand 5.0  |
| Backend  | Python 3.12, FastAPI 0.128, uvicorn 0.40, `ytmusicapi` 1.11, `httpx` |
| APIs     | YouTube Music (via browser headers), Last.fm                         |

---

## Prerequisites

- Python 3.12+
- Node.js 24+ and npm
- A [Last.fm API key](https://www.last.fm/api/account/create) *(only required for Last.fm integration)*

---

## Setup & Running

```bash
# 1. Clone the repository
git clone https://github.com/filcampos00/PlaylistSorter.git
cd PlaylistSorter

# 2. Set up environment variables
cp .env.example .env       # macOS/Linux
copy .env.example .env     # Windows
# Edit .env and add your LASTFM_API_KEY

# 3. Set up the backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r backend/requirements.txt

# 4. Set up the frontend
cd frontend
npm install
cd ..

# 5. Run the app
python scripts/start_all.py
```

Once running:

| Service      | URL                        |
| ------------ | -------------------------- |
| Frontend     | http://localhost:5182      |
| Backend API  | http://localhost:8182      |
| Swagger docs | http://localhost:8182/docs |

---

## Environment Variables

| Variable         | Required | Description                                                                        |
| ---------------- | -------- | ---------------------------------------------------------------------------------- |
| `LASTFM_API_KEY` | Yes      | Last.fm API key — get one at [last.fm/api](https://www.last.fm/api/account/create) |

Copy `.env.example` to `.env` and fill in the value.

---

## Scripts

All scripts are in `scripts/` and run from the project root:

| Script             | Description                                                |
| ------------------ | ---------------------------------------------------------- |
| `start_all.py`     | Starts both backend and frontend servers simultaneously    |
| `start_backend.py` | Starts only the FastAPI backend (useful for API-only work) |
| `clean_project.py` | Removes build artifacts, caches, and temp files            |

---

## Project Structure

```
PlaylistSorter/
├── backend/              # FastAPI application
│   └── app/
│       ├── youtube/      # YouTube Music controller & service
│       ├── lastfm/       # Last.fm integration
│       └── common/       # Shared schemas & sorting strategies
├── frontend/             # React + Vite application
│   └── src/
│       ├── pages/        # LoginPage, DashboardPage
│       └── components/   # UI components
├── scripts/              # Dev utility scripts
└── .env.example
```

---

## Known Limitations

- **Release dates** — Sorting by release date uses YouTube's upload date, not the original album release date. Classic or remastered albums may sort incorrectly.
- **Header expiry** — Browser headers may expire and need to be re-pasted periodically.

---

## Spotify — Why It's Not Supported

Spotify integration was planned, however it was dropped due to Spotify's increasingly restrictive API policies:

- **December 2025** — New app registrations were frozen
- **Early 2026** — Spotify [restored registrations](https://developer.spotify.com/blog/2026-02-06-update-on-developer-access-and-platform-security) but introduced very restrictive changes to their API

The backend was designed to be platform-agnostic, but this project will not be continued.

---

## About This Project

PlaylistSorter was built as a personal exploration of **AI-assisted development** using [Antigravity IDE](https://antigravity.google/). It is not affiliated with YouTube Music or Last.fm. The software is provided as-is, with no warranties.

---

## License

[MIT](LICENSE) © 2026 filcampos00
