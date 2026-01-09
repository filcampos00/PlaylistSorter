---
description: Run code quality checks (lint/format/test) and commit changes
---

1. **Backend: Run Ruff Check (Fix)**
   Run the following command to lint and auto-fix backend code:
   ```powershell
   .\.venv\Scripts\ruff check --fix backend
   ```

2. **Backend: Run Ruff Format**
   Run the following command to format backend code:
   ```powershell
   .\.venv\Scripts\ruff format backend
   ```

3. **Backend: Run Tests**
   Run backend tests to ensure no regressions:
   ```powershell
   .\.venv\Scripts\pytest backend
   ```

4. **Frontend: Lint and Fix**
   Run ESLint with auto-fix in the `frontend` directory.
   Command: `npm run lint -- --fix`
   Directory: `frontend`

5. **Frontend: Build and Typecheck**
   Run the build script to verify types and build process in the `frontend` directory.
   Command: `npm run build`
   Directory: `frontend`

6. **Check Status**
   Check the git status to see modified files (including auto-fixes):
   ```powershell
   git status
   ```

7. **Commit Changes**
   If all previous steps passed, proceed to commit the changes.
   Ask the user for a commit message if one wasn't provided, then run:
   ```powershell
   git add .
   git commit -m "Your commit message"
   ```
