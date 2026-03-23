# SRRSS User Guide (MVP)

## Candidate
1. Register with email/password or LinkedIn flow.
2. Login and open Candidate Portal.
3. Select job and upload resume (PDF/DOCX).
4. Submit application and track status timeline:
   - Applied → Shortlisted → Interview → Hired/Rejected.

## Recruiter
1. Login as Recruiter.
2. Create job with title, department, and description.
3. Open ranked candidates for a job.
4. Filter by required skills and minimum experience.
5. Schedule interview from the candidate row.

## Admin
1. Login as Admin.
2. Review analytics totals and time-to-hire metrics.
3. View users and update role assignments.
4. Access system audit logs (via application audit endpoint).

## Notifications
- Status updates and interview scheduling are designed for email/SMS integration.
- In this MVP scaffold, integration hooks are prepared but external providers are not yet configured.

## Accessibility & Responsiveness
- Candidate-facing pages follow responsive Tailwind layouts.
- Keyboard-friendly form controls are implemented in auth and portal forms.
