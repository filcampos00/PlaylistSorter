---
trigger: always_on
---

# Project Patterns

## Backend (FastAPI)
- port:8182
- **Controller/Service Pattern**: Use controllers for endpoints and services for business logic
  - `main.py` should only contain FastAPI default endpoints
- **Asynchronous Operations**: Use `async/await` for all I/O bound operations
- use `scripts\start_backend.py` to start backend server
- Always use python virtual environment
- There is requirements.txt and requirements-dev.txt

## Frontend (React)
- port:5182
- **Vite for Tooling**: Use Vite for fast builds and hot module replacement
- **Component-Based UI**: Keep components small and focused on a single responsibility

# Project Principles

## 1. Transparency & Traceability
- Every major decision should be documented in `.notes/`
- Logs are available at `logs/playlist_sorter.log`


## 2. Modular API Design
- Backend logic should be platform-agnostic where possible to support future platform expansion
- Use `ytmusicapi` for YouTube Music specific operations
- Use `spotipy` for Spotify operations