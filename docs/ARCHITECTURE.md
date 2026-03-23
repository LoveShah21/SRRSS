# Architecture & Technical Design (ARCHITECTURE.md)

## 1. High-Level System Architecture

SRRSS uses a robust 3-Tier Microservices-inspired architecture designed to separate UI logic, business orchestration, and heavy AI workloads.

```text
[ React Frontend ] (Candidate/Recruiter/Admin UIs)
        │
      (REST / JSON)
        ▼
[ Node.js API Gateway & Business Logic ] ─── (MongoDB Atlas) 
  (Express.js, JWT, Mongoose Auth/RBAC) ─── (AWS S3 - Files)
        │
      (REST / internal RPC)
        ▼
[ Python AI Microservice ] (FastAPI, spaCy, scikit-learn)
```

## 2. Component Responsibilities

### Tier 1: Frontend (React + Tailwind CSS)
*   **Role:** User engagement and display. Separate logical routing flows for Candidate, Recruiter, and Admin.
*   **State Management:** React Context API (or Redux for generic caching).
*   **Hosting:** Vercel.

### Tier 2: Backend API (Node.js + Express)
*   **Role:** Primary data orchestrator. Handles User Auth, Role-Based Access Controls (RBAC), and simple CRUD operations (Jobs, Interveiws, Users). 
*   **Data Layer:** Connects to MongoDB to store user profiles, job specs, and metadata. Connects to S3 to securely stream uploaded Resumes.
*   **Hosting:** Docker container on Heroku / AWS ECS.

### Tier 3: AI Service (Python + FastAPI)
*   **Role:** Performs heavy computation logic separated from the async event loop of Node.js. 
*   **Key Pipes:** 
    1.  *Resume Parsing Engine:* (spaCy) Extracts names, emails, skills, education.
    2.  *Semantic Matcher:* Compares Job embeddings vs Resume embeddings (TF-IDF/cosine similarity). 
    3.  *Bias Detector:* Checks Job descriptions for gendered/biased wording.

## 3. Polyrepo / Monorepo Folder Structure

```text
/
├─ frontend/          # React (CRA or Vite) application
├─ backend/           # Node.js Express server
│  ├─ src/
│  │  ├─ controllers/
│  │  ├─ models/      # Mongoose schemas
│  │  ├─ routes/
│  │  ├─ services/    # Logic & AI proxy calls
│  │  └─ middleware/  # JWT & RBAC
├─ ai-service/        # Python FastAPI
│  ├─ app/
│  │  ├─ api/         # Endpoints
│  │  ├─ nlp/         # spaCy logic / parsers
│  │  └─ models/      # Scoring models
├─ infra/             # Docker-compose, k8s, github actions
└─ docs/              # Architecture, UX, API definitions
```

## 4. Primary Data Models (MongoDB)

**User Collection**
*   `_id`, `name`, `email`, `passwordHash`, `role` (Admin|Recruiter|Candidate), `createdAt`
*   *Candidate Profile Embed:* `skills[]`, `experience[]`, `education[]`

**Job Collection**
*   `_id`, `title`, `description`, `department`, `status` (Open|Closed), `createdBy` (User ID), `requiredSkills[]`

**Application Collection**
*   `_id`, `jobId`, `candidateId`, `resumeUrl` (S3 link)
*   `status` (Applied|Shortlisted|Interview|Hired|Rejected)
*   `aiMatchScore` (0-100), `aiExtractedSkills[]`

**Audit Log Collection**
*   `_id`, `action`, `userId`, `timestamp`, `details`

## 5. Internal API Contracts

### Node.js <-> Frontend
*   `POST /api/v1/auth/login` -> Returns JWT.
*   `POST /api/v1/jobs` -> Recruiter creates Job.
*   `POST /api/v1/applications` -> Candidate applies (multipart/form-data for Resume).
*   `GET /api/v1/jobs/:id/candidates` -> Recruiter views ranked applicants.

### Node.js <-> Python AI Service
*   `POST /internal/ai/parse-resume` 
    *   *Req:* PDF binary stream. 
    *   *Res:* JSON `{ extracted: { name, skills, ... } }`.
*   `POST /internal/ai/score-candidate`
    *   *Req:* `{ jobText: "...", candidateSkills: [...] }`
    *   *Res:* `{ matchScore: 85 }`
