# Final Deployment Configuration Guide

Your application is ready for production. To make it go live, follow these exact steps to link your Vercel Frontend and Render Backend.

## 1. Backend Configuration (Render)

**URL:** `https://your-backend-app.onrender.com`

We have provided a `render.yaml` Blueprint file at the root of the project to make this easy.

1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New** -> **Blueprint**.
3. Connect your GitHub repository containing this code.
4. Render will automatically detect the `chatpdf-backend` web service.
5. Provide the sensitive environment variables during the setup when prompted:
   - `GEMINI_API_KEY`: `Your Google Gemini API Key`
   - `FRONTEND_URL`: `https://chat-pdf-neon.vercel.app` (or your actual Vercel domain)

> **Important Note regarding Storage on Render's Free Tier**
> Render's Free Instance Plan operates with ephemeral storage. This means every time Render deploys or restarts the app (which happens daily when inactive), any uploaded PDFs, ChromaDB indexes, and the SQLite database (`/data`) will be wiped. If you want persistent storage, you will need to upgrade to at least a paid Starter plan and attach a Disk (uncomment the `disk` section in `render.yaml`).

**Status:**

- ✅ CORS is pre-configured to allow Vercel domains even if `FRONTEND_URL` is omitted (fallback added).
- ✅ Heavy dependencies removed for smaller build size.
- ✅ `render.yaml` automates the Docker deployment!

---

## 2. Frontend Configuration (Vercel)

**URL:** `https://chat-pdf-neon.vercel.app/`

Go to your Vercel Project Dashboard -> Settings -> Environment Variables.
Add the following variable:

| Variable              | Value                                   | Description                                                      |
| :-------------------- | :-------------------------------------- | :--------------------------------------------------------------- |
| `NEXT_PUBLIC_API_URL` | `https://your-backend-app.onrender.com` | Points the frontend to your live backend. **No trailing slash.** |

**Important:**

- After adding this variable, you MUST **Redeploy** the frontend in Vercel for the changes to take effect.
- Go to Deployments -> Redeploy.

---

## 3. Verification

Once both are redeployed:

1. Open `https://chat-pdf-neon.vercel.app/`
2. Upload a PDF.
3. Chat with it.

If you see any issues, check the browser console (F12) for CORS errors or Network tab for failed requests.

---

## Summary of Changes Made

1. **Backend**:
   - Swapped Railway configuration for a Render Blueprint (`render.yaml`).
   - Added automatic Vector DB reset migration (handles the "function conflict" error).
   - Hardcoded Vercel URL in CORS origins as a safety fallback.
2. **Frontend**:
   - Confirmed `api.ts` uses `NEXT_PUBLIC_API_URL`.

You are good to go! 🚀
