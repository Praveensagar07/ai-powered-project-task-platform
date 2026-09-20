# Production Deployment Guide

This guide describes how to deploy the **AI-Powered Project & Task Management Platform** across cloud hosting providers (Render, Railway, Vercel, or Docker).

---

## 1. Architecture Overview

- **Backend (FastAPI):** Deployable on Render Web Service, Railway, Fly.io, or any container host.
- **Database (PostgreSQL):** Render PostgreSQL, Supabase, Neon, or Railway PostgreSQL.
- **Frontend (React / Vite):** Deployable on Vercel, Netlify, or Render Static Sites.

---

## 2. Backend Deployment (Render / Railway)

### Environment Variables
Configure the following in your deployment dashboard:

```env
APP_ENV=production
DEBUG=false
PORT=8000
API_PREFIX=/api
DATABASE_URL=postgresql+psycopg://user:password@hostname:5432/dbname
JWT_SECRET=generate-a-secure-random-string-at-least-32-chars-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
AI_PROVIDER=openai
AI_API_KEY=sk-your-openai-or-gemini-key
AI_MODEL=gpt-4o-mini
CORS_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:5173
SEED_DEMO_DATA=false
```

### Build & Start Commands
- **Root Directory:** `backend`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 3. Frontend Deployment (Vercel / Netlify)

### Environment Variables
```env
VITE_API_BASE_URL=https://your-backend-service.onrender.com/api
```

### Build & Output Settings
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`

### SPA Routing Configuration (Vercel `vercel.json`)
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

---

## 4. Local Full-Stack Development

### 1. Start Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
API Documentation: `http://localhost:8000/docs`

### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev
```
Application: `http://localhost:5173`
Demo credentials: `praveen@example.com` / `Password123!`
