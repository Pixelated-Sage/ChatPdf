# 🚀 Railway Deployment Fixes

The build failure was likely caused by **image size bloat** or **dependency conflicts**. We've optimized the Dockerfile to be leaner and more robust.

## 🛠️ Changes Applied

### 1. Reduced Image Size (~2GB → ~500MB)

- **Problem**: `sentence-transformers` was pulling the massive 800MB+ GPU version of PyTorch by default.
- **Fix**: Updated `Dockerfile` to explicitly install the **CPU-only** version of PyTorch first. This drastically reduces the build size and prevents timeouts during the export phase.

### 2. Simplified Dependencies

- **Problem**: `pysqlite3-binary` can cause build issues on some architectures and isn't needed for Python 3.11 (which has a modern SQLite version built-in).
- **Fix**: Removed `pysqlite3-binary` from `requirements.txt`. The code adapts automatically.

### 3. Fixed Startup Command

- **Problem**: The Dockerfile `CMD` instructions used the exec form `["uvicorn", ...]` which **does not** expand the `$PORT` variable provided by Railway.
- **Fix**: Changed `CMD` to shell form to correctly bind to the Railway-assigned port:
  ```dockerfile
  CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
  ```

## 📋 Next Steps

1. **Commit & Push**:
   Deploy these changes to your repository. Railway should trigger a new build automatically.

   ```bash
   git add backend/Dockerfile backend/requirements.txt
   git commit -m "fix(deploy): optimize docker build and fix startup command"
   git push
   ```

2. **Verify Environment Variables**:
   Ensure these variables are set in your Railway project settings:
   - `GEMINI_API_KEY`: Your API key
   - `FRONTEND_URL`: The URL of your deployed frontend (e.g., `https://chatpdf-frontend.up.railway.app`) to fix CORS.

3. **Check Build Logs**:
   The new build should be much faster. Look for `Downloading ... torch ... cpu` in the logs.
