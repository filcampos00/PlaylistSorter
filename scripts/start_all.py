"""
Script to start both backend and frontend servers simultaneously.

This script spawns the backend (FastAPI on port 8182) and frontend (Vite on port 5182)
as separate processes and handles graceful shutdown on Ctrl+C.
"""

import os
import signal
import subprocess
import sys

from dotenv import load_dotenv


def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Calculate the project root (parent of scripts/)
    project_root = os.path.abspath(os.path.join(script_dir, ".."))

    # Load .env from project root
    dotenv_path = os.path.join(project_root, ".env")
    load_dotenv(dotenv_path)

    # Calculate directory paths
    backend_dir = os.path.join(project_root, "backend")
    frontend_dir = os.path.join(project_root, "frontend")

    # Validate directories exist
    if not os.path.exists(backend_dir):
        print(f"Error: Backend directory not found at {backend_dir}")
        sys.exit(1)

    if not os.path.exists(frontend_dir):
        print(f"Error: Frontend directory not found at {frontend_dir}")
        sys.exit(1)

    print("=" * 60)
    print("Starting Playlist Sorter")
    print("=" * 60)
    print(f"Backend:  http://127.0.0.1:8182")
    print(f"Frontend: http://127.0.0.1:5182")
    print("=" * 60)
    print("Press Ctrl+C to stop all servers\n")

    processes = []

    try:
        # Start backend server
        print("[Backend] Starting...")
        backend_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--reload",
                "--port",
                "8182",
            ],
            cwd=backend_dir,
            # Use CREATE_NEW_PROCESS_GROUP on Windows for proper signal handling
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            if sys.platform == "win32"
            else 0,
        )
        processes.append(("Backend", backend_process))

        # Start frontend server
        print("[Frontend] Starting...")
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            shell=True,  # Required for npm on Windows
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            if sys.platform == "win32"
            else 0,
        )
        processes.append(("Frontend", frontend_process))

        # Wait for processes (this will block until interrupted)
        for name, process in processes:
            process.wait()

    except KeyboardInterrupt:
        print("\n\nShutting down servers...")

        for name, process in processes:
            print(f"[{name}] Stopping...")
            if sys.platform == "win32":
                # On Windows, send CTRL_BREAK_EVENT
                process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                # On Unix, send SIGTERM
                process.terminate()

        # Wait for processes to terminate gracefully
        for name, process in processes:
            try:
                process.wait(timeout=5)
                print(f"[{name}] Stopped")
            except subprocess.TimeoutExpired:
                print(f"[{name}] Force killing...")
                process.kill()

        print("\nAll servers stopped.")


if __name__ == "__main__":
    main()
