# SRRSS API Documentation

Base URL: `/api/v1`

## Authentication

### POST `/auth/register`
Register user by email/password.
- Body: `{ "name": "...", "email": "...", "password": "...", "role": "Candidate|Recruiter" }`

### POST `/auth/register-linkedin`
Candidate registration via LinkedIn identity payload.
- Body: `{ "name": "...", "email": "...", "linkedinUrl": "..." }`

### POST `/auth/login`
- Body: `{ "email": "...", "password": "..." }`
- Response: `{ token, user }`

### GET `/auth/me`
Get current user profile (Bearer token required).

### POST `/auth/refresh`
Issue new JWT for authenticated user.

### POST `/auth/logout`
Revoke active JWT in in-memory blacklist.

## Jobs

### GET `/jobs`
List open jobs (`?status=Open|Closed&q=search`).

### GET `/jobs/mine`
Recruiter/Admin: list own jobs (Admin gets all).

### POST `/jobs`
Recruiter/Admin create job; triggers bias detection.
- Body: `{ "title", "department", "description", "requiredSkills": [] }`

### GET `/jobs/:id/candidates`
Recruiter/Admin ranked applications for a job.
- Query: `skills=react,node.js&minYears=2`

### GET `/jobs/analytics/summary`
Recruiter/Admin dashboard metrics summary.

## Applications

### POST `/applications/apply/:jobId`
Candidate applies to a job with multipart resume upload.
- FormData: `resume=<pdf|docx>`

### GET `/applications/my-applications`
Candidate’s applications with status timeline.

### PATCH `/applications/:id/status`
Recruiter/Admin updates status to one of:
`Applied|Shortlisted|Interview|Hired|Rejected`.

### PATCH `/applications/:id/schedule-interview`
Recruiter/Admin schedules interview.
- Body: `{ "scheduledAt": ISODate, "mode": "Online|Onsite", "notes": "..." }`

### GET `/applications/job/:jobId`
Recruiter/Admin: list applications for job.

### GET `/applications/audit/logs`
Admin-only audit log listing.

## Admin

### GET `/admin/users`
Admin-only user listing.

### PATCH `/admin/users/:id/role`
Admin-only role update.
- Body: `{ "role": "Admin|Recruiter|Candidate" }`

### GET `/admin/analytics`
Admin-only aggregated metrics:
- totals: users/jobs/applications
- metrics: time-to-hire, source quality placeholder

## AI Service Internal Endpoints

AI Base URL: `http://localhost:8000/api/v1`

### POST `/parse-resume`
Input: PDF or DOCX file.
Output: extracted name/email/skills/education/experience and raw text.

### POST `/score-candidate`
Input: `{ jobText, jobSkills, candidate: { candidateSkills, candidateText } }`
Output: `{ match_score, matched_skills }`.

### POST `/detect-bias`
Input: `{ jobDescription }`
Output: `{ biased_words_found, recommendation }`.
