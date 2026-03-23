# SRRSS Design System (DESIGN.md)

## 1. Overview
The Smart Recruitment & Resume Screening System (SRRSS) design system defines the visual language, component primitives, and layouts for candidate, recruiter, and administrative user interfaces. 

It is mapped from the Stitch UI project `7674230861987470503`.

## 2. Core Flows & Mapped Screens
Based on the current Stitch output, here is the mapping of screens handling core requirements:

### Candidate Flows
*   **Landing & Auth:** SRRSS Immersive Landing Page, SRRSS Unified Auth Gateway
*   **Discovery & Application:** SRRSS Job Board, SRRSS Job Application Form
*   **Portal & Progress:** SRRSS Candidate Portal Dashboard, SRRSS Resume Upload & Status
*   **Operations:** Candidate Profile Settings, SRRSS Application Withdrawal

### Recruiter Flows
*   **Management:** SRRSS Recruiter Dashboard, SRRSS Job Creation Wizard, SRRSS Hiring Pipeline Kanban
*   **Evaluation:** Candidate Evaluation Scorecard, SRRSS Finalist Comparison Matrix, SRRSS AI Score Explainability Panel
*   **Interviews & Comms:** SRRSS Interview Management Hub, SRRSS Unified Communication Center, SRRSS External Interview Scheduler

### Admin Flows
*   **Control & Users:** SRRSS Admin Control Panel, SRRSS Admin User Moderation
*   **Configuration & Compliance:** SRRSS Admin Security Settings, SRRSS Admin Scoring Weights Config
*   **Logs & Analytics:** SRRSS System Audit Log Viewer, SRRSS Report Export Configurator

## 3. Visual Language

### Colors (Tailwind Reference)
*   **Primary (Brand):** `blue-600` (e.g., `#2563eb`) - Used for primary actions, buttons, and active states.
*   **Secondary/Accent:** `indigo-500` (e.g., `#6366f1`) - Used for illustrative elements, gradients on landing pages.
*   **Neutral (Backgrounds):** 
    *   `gray-50` (`#f9fafb`) for app backgrounds.
    *   `white` (`#ffffff`) for cards, panels, and surfaces.
*   **Text (Typography):**
    *   `gray-900` (`#111827`) for high-contrast headers.
    *   `gray-600` (`#4b5563`) for body copy and subdued metadata.
*   **Utility (Status/Feedback):**
    *   **Success (Hired/Shortlisted):** `green-500` (`#22c55e`), `green-50` backgrounds.
    *   **Warning (Pending Review):** `yellow-500` (`#eab308`), `yellow-50` backgrounds.
    *   **Danger (Rejected/Destructive):** `red-500` (`#ef4444`), `red-50` backgrounds.
    *   **Info (AI Generated/Parsed):** `blue-400` (`#3b82f6`).

### Typography 
*   **Font Family:** Inter (sans-serif) or system UI default.
*   **Headings:**
    *   H1: `text-3xl font-bold tracking-tight text-gray-900`
    *   H2: `text-2xl font-semibold text-gray-900`
    *   H3: `text-lg font-medium text-gray-900`
*   **Body:**
    *   Primary: `text-sm text-gray-600`
    *   Secondary/Captions: `text-xs text-gray-500`

### Sizing and Spacing
*   **Padding/Margins:** Based on a standard 4px baseline (`p-4`, `m-4` being 16px). Cards typical use `p-6` (24px).
*   **Corner Radii:** Soft modern corners (`rounded-lg` or `rounded-xl`).
*   **Shadows:** 
    *   Subtle elevation (`shadow-sm`) for interactive elements.
    *   Medium elevation (`shadow-md`) for dropdowns/modals.

## 4. Component Layouts & Primitives

### Standard Layout Structure
1.  **Sidebar/Navigation:** Fixed navigation rail on the left (Recruiter/Admin) or Top horizontal navbar (Candidate portal).
2.  **Breadcrumbs:** Essential for admin and recruiter nested views (e.g., `Dashboard / Candidates / John Doe`).
3.  **Content Surface:** Centered main container max-wdith (`max-w-7xl px-4 sm:px-6 lg:px-8`).

### UI Primitives
*   **Buttons:**
    *   *Primary:* Solid blue background, white text (`bg-blue-600 hover:bg-blue-700 text-white rounded-md px-4 py-2`).
    *   *Secondary:* White background, border, gray text (`bg-white border border-gray-300 text-gray-700 hover:bg-gray-50`).
*   **Data Tables:** Clean tables with sticky headers. Used in Log Viewers, Candidates list, and Admin panels.
*   **Kanban Boards:** Horizontal swimlanes for Hiring Pipeline.
*   **Forms & Inputs:** Standard block inputs (`w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500`).
*   **Score Badges:** Circular or pill-shaped badges highlighting the AI match score in percentages.
*   **Drag & Drop Zones:** Dashed border areas for file uploads (`border-2 border-dashed border-gray-300 bg-gray-50`).

## 5. UI Gap Analysis (`stitch-loop`)
Based on the mapping, we have exceptional coverage for the core MVP across all user roles. No major UI design components are missing for starting the frontend architecture phase.
