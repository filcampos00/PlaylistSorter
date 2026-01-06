
import os
import subprocess
import sys

from dotenv import load_dotenv

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Calculate the project root (parent of scripts/)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    
    # Load .env from project root
    dotenv_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path)
    
    # Calculate the backend directory path (assuming scripts/../backend)
    backend_dir = os.path.join(project_root, 'backend')
    
    if not os.path.exists(backend_dir):
        print(f"Error: Backend directory not found at {backend_dir}")
        sys.exit(1)
        
    print(f"Starting backend server...")
    print("URL: http://127.0.0.1:8182")
    
    # Change working directory to backend
    os.chdir(backend_dir)

    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8182"],
            check=True
        )
    except KeyboardInterrupt:
        print("\nStopping backend server...")

if __name__ == "__main__":
    main()

