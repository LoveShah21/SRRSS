# SRRSS Deployment Guide

## 1. Local Development

### Prerequisites
- Node.js 20+
- Python 3.11+
- MongoDB (local or Atlas)
- Docker (optional, for compose)

### Environment
- Copy `backend/.env.example` to `backend/.env`
- Copy `frontend/.env.example` to `frontend/.env`

### Run Services Manually
1. Backend
   - `cd backend`
   - `npm ci`
   - `npm run dev`
2. AI Service
   - `cd ai-service`
   - `python -m venv .venv`
   - `.venv\\Scripts\\activate`
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload --port 8000`
3. Frontend
   - `cd frontend`
   - `npm ci`
   - `npm run dev`

## 2. Docker Compose

From `infra/`:
- `docker compose up --build`

Services:
- Frontend: `http://localhost:4173`
- Backend: `http://localhost:5000`
- AI service: `http://localhost:8000`
- MongoDB: `mongodb://localhost:27017`

## 3. Cloud Deployment Targets

### Frontend (Vercel)
- Root: `frontend/`
- Build command: `npm run build`
- Output: `dist`
- Env: `VITE_API_BASE_URL=https://<backend-host>/api/v1`

### Backend (Heroku/Render/Fly)
- Root: `backend/`
- Start command: `npm start`
- Env:
  - `MONGODB_URI=<mongodb-atlas-uri>`
  - `JWT_SECRET=<strong-secret>`
  - `AI_SERVICE_URL=https://<ai-host>/api/v1`

### AI Service (Render/Fly/EC2)
- Root: `ai-service/`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 4. MongoDB Atlas Template

Use connection string format:
`mongodb+srv://<user>:<password>@<cluster>/<db>?retryWrites=true&w=majority`

Recommended collections:
- `users`
- `jobs`
- `applications`
- `auditlogs`

## 5. CI/CD

GitHub Actions workflow: `.github/workflows/ci.yml`
- Backend: `npm test`
- Frontend: `npm run test` and `npm run build`
- AI service: `pytest -q`
