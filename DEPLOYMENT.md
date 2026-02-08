# 🚀 Deployment Guide

Complete guide for deploying ChatPDF to production.

- **Backend**: Railway (FastAPI + ChromaDB)
- **Frontend**: Vercel (Next.js)

---

## ✅ Pre-Deployment Checklist

### Backend (Railway)

- [ ] Gemini API key obtained from [aistudio.google.com](https://aistudio.google.com)
- [ ] GitHub repository pushed
- [ ] All dependencies in `requirements.txt`
- [ ] `Dockerfile` configured

### Frontend (Vercel)

- [ ] GitHub repository pushed
- [ ] Backend deployed first (need Railway URL)
- [ ] All dependencies in `package.json`

---

## 📦 Backend Deployment (Railway)

### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your `ChatPdf` repository
6. Set root directory to `/backend` (if monorepo)

### Step 2: Configure Environment Variables

In Railway project settings → Variables:

```env
GEMINI_API_KEY=your-actual-gemini-key-here
GEMINI_MODEL=gemini-2.0-flash
CHROMA_PERSIST_DIR=./chroma_db
DATABASE_URL=sqlite:///./chatpdf.db
UPLOAD_DIRECTORY=./uploads
MAX_FILE_SIZE=10000000
SECRET_KEY=generate-random-secret-here
FRONTEND_URL=https://your-app.vercel.app
PORT=8000
```

**Important:**

- Get `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com)
- Generate `SECRET_KEY` using: `openssl rand -hex 32`
- Update `FRONTEND_URL` after Vercel deployment

### Step 3: Deploy

Railway will automatically:

- Detect `Dockerfile`
- Build container
- Deploy to unique URL (e.g., `https://chatpdf-backend-production.up.railway.app`)

### Step 4: Verify Deployment

Test endpoints:

```bash
# Health check
curl https://your-backend.railway.app/health

# API docs
open https://your-backend.railway.app/docs
```

Expected health response:

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "gemini": { "status": "healthy" },
    "chromadb": { "status": "healthy" },
    "storage": { "status": "healthy" }
  }
}
```

---

## 🌐 Frontend Deployment (Vercel)

### Step 1: Install Vercel CLI (Optional)

```bash
npm install -g vercel
```

### Step 2: Deploy via GitHub (Recommended)

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click **"Add New Project"**
4. Import your `ChatPdf` repository
5. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` (if monorepo)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### Step 3: Set Environment Variables

In Vercel project settings → Environment Variables:

| Key                   | Value                                  | Environment                      |
| --------------------- | -------------------------------------- | -------------------------------- |
| `NEXT_PUBLIC_API_URL` | `https://your-backend.railway.app/api` | Production, Preview, Development |

**Important:** Use your actual Railway backend URL (from Step 1 above)

### Step 4: Deploy

Vercel will automatically:

- Install dependencies
- Run `npm run build`
- Deploy to unique URL (e.g., `https://chatpdf.vercel.app`)

### Step 5: Update Backend CORS

Go back to Railway and update the `FRONTEND_URL` variable:

```env
FRONTEND_URL=https://chatpdf.vercel.app
```

Railway will auto-redeploy with new CORS settings.

---

## 🔄 Post-Deployment Updates

### Automatic Deployments

Both platforms support auto-deploy on git push:

**Railway**: Pushes to `main` branch → auto-deploy backend
**Vercel**: Pushes to `main` branch → auto-deploy frontend

### Manual Redeployment

**Railway:**

1. Go to project → Deployments
2. Click "Deploy" on latest commit

**Vercel:**

1. Go to project → Deployments
2. Click "Redeploy" on latest deployment

---

## 🧪 Testing Production

### Test Upload Flow

```bash
# Upload a test PDF
curl -X POST https://your-backend.railway.app/api/upload \
  -F "file=@test.pdf"

# Response: {"document_id": "...", "filename": "...", ...}
```

### Test Chat Flow

```bash
# Ask a question
curl -X POST https://your-backend.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?", "document_ids": ["your-doc-id"]}'
```

### Test Frontend

1. Open `https://your-app.vercel.app`
2. Upload a PDF
3. Ask questions
4. Check browser console for errors

---

## 🐛 Troubleshooting

### Backend Issues

**❌ 500 Error on /upload**

- Check Railway logs: Project → Deployments → View Logs
- Verify `GEMINI_API_KEY` is set correctly
- Ensure uploads directory exists (Dockerfile creates it)

**❌ CORS errors**

- Verify `FRONTEND_URL` matches your Vercel URL exactly
- Check Railway logs for CORS middleware errors

**❌ ChromaDB errors**

- Check Railway persistent storage is enabled
- Verify `CHROMA_PERSIST_DIR` path

### Frontend Issues

**❌ API calls fail with 404**

- Verify `NEXT_PUBLIC_API_URL` includes `/api` suffix
- Check Railway backend is running

**❌ Environment variable not working**

- Redeploy after adding env vars (Vercel requires rebuild)
- Check variable name starts with `NEXT_PUBLIC_`

---

## 📊 Monitoring

### Railway

- **Logs**: Project → Deployments → Logs
- **Metrics**: Project → Metrics (CPU, Memory, Network)
- **Health**: `https://your-backend.railway.app/health`

### Vercel

- **Logs**: Project → Deployments → Function Logs
- **Analytics**: Project → Analytics (views, performance)
- **Speed Insights**: Project → Speed Insights

---

## 💰 Cost Estimation

### Free Tier Limits

**Railway:**

- $5/month free credit
- ~500 hours/month of uptime
- 1GB RAM, shared CPU
- Suitable for low-traffic apps

**Vercel:**

- 100GB bandwidth/month
- 100 deployments/day
- Unlimited static sites
- **Generous free tier** ✅

### Estimated Monthly Cost (after free tier):

- **0-100 users**: Free
- **100-1000 users**: ~$5-10/month (Railway overages)
- **1000+ users**: Upgrade to Railway Pro ($20/month)

---

## 🔐 Security Best Practices

✅ **Implemented:**

- HTTPS enforced (Railway + Vercel default)
- CORS restricted to frontend domain
- Environment variables for secrets
- Security headers in Vercel config

⚠️ **TODO for Production:**

- [ ] Add rate limiting (Railway middleware)
- [ ] Implement user authentication
- [ ] Enable Railway backups
- [ ] Set up error tracking (Sentry)
- [ ] Add uptime monitoring (UptimeRobot)

---

## 📝 Environment Variables Summary

### Backend (.env)

```env
GEMINI_API_KEY=<from aistudio.google.com>
GEMINI_MODEL=gemini-2.0-flash
CHROMA_PERSIST_DIR=./chroma_db
DATABASE_URL=sqlite:///./chatpdf.db
UPLOAD_DIRECTORY=./uploads
MAX_FILE_SIZE=10000000
SECRET_KEY=<openssl rand -hex 32>
FRONTEND_URL=https://your-app.vercel.app
PORT=8000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api
```

---

## 🎉 Deployment Complete!

Your ChatPDF app is now live:

- **Frontend**: https://your-app.vercel.app
- **Backend API**: https://your-backend.railway.app
- **API Docs**: https://your-backend.railway.app/docs
- **Health Check**: https://your-backend.railway.app/health

**Next Steps:**

1. Test all features in production
2. Monitor Railway + Vercel dashboards
3. Share the URL with users 🚀
4. Consider adding analytics (Google Analytics, PostHog)

---

## 📚 Additional Resources

- [Railway Docs](https://docs.railway.app)
- [Vercel Docs](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
