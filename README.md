# Smart Recruitment & Resume Screening System (SRRSS)

AI-driven recruitment platform with three user experiences (Candidate, Recruiter, Admin), a Node.js API gateway, and a Python AI microservice for resume parsing and scoring.

## Project Structure

- `frontend/` React + Tailwind UI
- `backend/` Node.js + Express API and RBAC
- `ai-service/` FastAPI NLP service (parse, score, bias detection)
- `infra/` Docker compose and deployment support
- `docs/` architecture, API, deployment, and user documentation

## Quick Start

1. Backend
	- `cd backend`
	- `npm ci`
	- `npm run dev`
2. AI Service
	- `cd ai-service`
	- `python -m venv .venv`
	- `.venv\Scripts\activate`
	- `pip install -r requirements.txt`
	- `uvicorn app.main:app --reload --port 8000`
3. Frontend
	- `cd frontend`
	- `npm ci`
	- `npm run dev`

## Testing

- Backend: `cd backend && npm test`
- Frontend: `cd frontend && npm run test`
- AI service: `cd ai-service && pytest -q`

## CI/CD

GitHub Actions workflow is available in `.github/workflows/ci.yml`.
