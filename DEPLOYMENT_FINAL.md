# Final Deployment Configuration Guide

Your application is ready for production. To make it go live, follow these exact steps to link your Vercel Frontend and Railway Backend.

## 1. Backend Configuration (Railway)

**URL:** `https://chatpdf-production-ba7f.up.railway.app/`

Go to your Railway Project Dashboard -> Settings -> Environment Variables.
Ensure the following variables are set:

| Variable         | Value                              | Description                                 |
| :--------------- | :--------------------------------- | :------------------------------------------ |
| `FRONTEND_URL`   | `https://chat-pdf-neon.vercel.app` | Whitelists your frontend for CORS requests. |
| `GEMINI_API_KEY` | `...`                              | Your Google Gemini API Key.                 |
| `PORT`           | `8000`                             | (Optional, Railway sets this automatically) |

**Status:**

- ✅ CORS is pre-configured to allow `https://chat-pdf-neon.vercel.app` even if `FRONTEND_URL` is missing (fallback added).
- ✅ Heavy dependencies (PyTorch) removed for fast startup.
- ✅ Dockerfile uses correct port binding.

---

## 2. Frontend Configuration (Vercel)

**URL:** `https://chat-pdf-neon.vercel.app/`

Go to your Vercel Project Dashboard -> Settings -> Environment Variables.
Add the following variable:

| Variable              | Value                                            | Description                                                      |
| :-------------------- | :----------------------------------------------- | :--------------------------------------------------------------- |
| `NEXT_PUBLIC_API_URL` | `https://chatpdf-production-ba7f.up.railway.app` | Points the frontend to your live backend. **No trailing slash.** |

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
   - Migrated to `google-genai` v1.0 SDK.
   - Added automatic Vector DB reset migration (handles the "function conflict" error).
   - Hardcoded Vercel URL in CORS origins as a safety fallback.
2. **Frontend**:
   - Confirmed `api.ts` uses `NEXT_PUBLIC_API_URL`.

You are good to go! 🚀
