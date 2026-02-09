# 🚀 Quick Deploy Checklist

## Backend (Railway)

```bash
# 1. Ensure all files are committed
git add backend/
git commit -m "Backend ready for Railway deployment"
git push origin main

# 2. Go to https://railway.app
# 3. New Project → Deploy from GitHub → Select repo
# 4. Set root directory: backend (if monorepo)

# 5. Add environment variables in Railway dashboard:
GEMINI_API_KEY=<your-key>
GEMINI_MODEL=gemini-2.0-flash
CHROMA_PERSIST_DIR=./chroma_db
DATABASE_URL=sqlite:///./chatpdf.db
UPLOAD_DIRECTORY=./uploads
MAX_FILE_SIZE=10000000
SECRET_KEY=<generate with: openssl rand -hex 32>
FRONTEND_URL=https://your-app.vercel.ap
PORT=8000

# 6. Wait for deployment (~3-5 minutes)
# 7. Test: curl https://your-backend.railway.app/health
# 8. Copy Railway URL for frontend config
```

**Railway URL**: `https://chatpdf-production-XXXX.up.railway.app`

---

## Frontend (Vercel)

```bash
# 1. Update .env.local with Railway URL
echo "NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api" > frontend/.env.local

# 2. Test locally first
cd frontend
npm run build  # Ensure build succeeds
npm start      # Test production build

# 3. Commit and push
git add frontend/
git commit -m "Frontend ready for Vercel deployment"
git push origin main

# 4. Go to https://vercel.com
# 5. New Project → Import from GitHub → Select repo
# 6. Root Directory: frontend (if monorepo)

# 7. Add environment variable in Vercel:
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api

# 8. Click Deploy
# 9. Copy Vercel URL
```

**Vercel URL**: `https://chatpdf-XXXX.vercel.app`

---

## Final Step: Update CORS

```bash
# In Railway dashboard, update environment variable:
FRONTEND_URL=https://chatpdf-XXXX.vercel.app

# Railway will auto-redeploy with new CORS settings
```

---

## Verification

```bash
# Test backend health
curl https://your-backend.railway.app/health

# Test frontend
open https://your-app.vercel.app

# Test upload (from frontend UI)
# 1. Visit frontend URL
# 2. Upload a PDF
# 3. Ask a question
# 4. Verify response
```

---

## Deployment URLs (Fill after deploy)

| Service           | URL                              | Status     |
| ----------------- | -------------------------------- | ---------- |
| Backend (Railway) | `https://_____.railway.app`      | ⏳ Pending |
| Frontend (Vercel) | `https://_____.vercel.app`       | ⏳ Pending |
| API Docs          | `https://_____.railway.app/docs` | ⏳ Pending |

---

## Common Issues

**CORS Error**: Update `FRONTEND_URL` in Railway to match Vercel URL
**Build Failed**: Check logs in Railway/Vercel dashboard
**Env Vars Not Working**: Redeploy after adding variables

---

## Done! 🎉

Both services are deployed. Monitor:

- Railway: https://railway.app/dashboard
- Vercel: https://vercel.com/dashboard
