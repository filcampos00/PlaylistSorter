import os
import shutil
import argparse


def clean_project(dry_run=False):
    """
    Cleans the project of various cache and temporary files/directories.
    """
    targets = [
        # Python
        "**/__pycache__",
        "**/*.py[cod]",
        "**/*$py.class",
        ".ruff_cache",
        ".pytest_cache",
        ".mypy_cache",
        # Frontend
        "frontend/dist",
        "frontend/dist-ssr",
        "frontend/*.tsbuildinfo",
        # General temporary files
        "**/.DS_Store",
        "**/Thumbs.db",
    ]

    # Explicitly DO NOT clean:
    # .env, .notes, .venv, .vscode, node_modules (unless explicitly requested)

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    print(f"{'DRY RUN: ' if dry_run else ''}Cleaning project in {root_dir}")

    import glob

    for pattern in targets:
        # Recursive glob to find all matches
        full_pattern = os.path.join(root_dir, pattern)
        for path in glob.glob(full_pattern, recursive=True):
            if os.path.exists(path):
                if dry_run:
                    print(f"Would remove: {path}")
                else:
                    try:
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.remove(path)
                        print(f"Removed: {path}")
                    except Exception as e:
                        print(f"Error removing {path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean project cache and temp files.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually deleting.",
    )
    args = parser.parse_args()

    clean_project(dry_run=args.dry_run)
