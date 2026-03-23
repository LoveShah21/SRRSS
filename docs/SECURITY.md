# Application Security Checklist

## 1. Authentication & Authorization
- [x] JWT-based authentication implemented.
- [x] Tokens are self-contained and signed with a strong secret.
- [x] Passwords hashed before storage using strict algorithms (e.g., bcrypt with 10+ rounds).
- [x] RBAC middleware designed (Admin, Recruiter, Candidate roles).
- [ ] Token invalidation strategy (e.g., blocklist for logout) planned.

## 2. PII & Data Privacy
- [ ] Masking logic to be implemented for candidate PII (names, contact info) to prevent bias for Recruiters in initial stages.
- [ ] Ensure Resumes uploaded to S3 use presigned URLs with short expiry times (e.g., 5-15 mins).
- [ ] Avoid returning `passwordHash` or sensitive user info in any API responses.

## 3. Communication Security
- [ ] CORS domains restricted only to trusted frontend origins (e.g., `https://frontend-domain.com`).
- [ ] All public-facing endpoints behind HTTPS / TLS.

## 4. Input Validation & API Hardening
- [ ] Implement Express validation (e.g., `express-validator` or `zod`).
- [ ] Safe-guard against NoSQL injections by preventing raw object merges from `req.body`.
- [ ] Implement rate limiting (e.g., `express-rate-limit`) to prevent brute force login/resume upload abuse.

## 5. Security Audit Log
- [ ] Retain timestamps and user identifiers for sensitive actions (e.g., Role Changes, Job Deletion).
