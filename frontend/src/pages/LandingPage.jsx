function LandingPage() {
  return (
    <section className="space-y-6">
      <div className="card">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Smart Recruitment & Resume Screening System</h1>
        <p className="mt-2 text-slate-600">
          AI-driven recruitment platform for candidate applications, recruiter ranking workflows, and admin governance.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <article className="card">
          <h2 className="text-lg font-semibold">Candidate Portal</h2>
          <p className="mt-2 text-sm text-slate-600">Register, upload resume, and track application status timeline.</p>
        </article>
        <article className="card">
          <h2 className="text-lg font-semibold">Recruiter Dashboard</h2>
          <p className="mt-2 text-sm text-slate-600">Create jobs, rank candidates, filter by skills, and schedule interviews.</p>
        </article>
        <article className="card">
          <h2 className="text-lg font-semibold">Admin Console</h2>
          <p className="mt-2 text-sm text-slate-600">Manage roles, review analytics, and monitor audit logs.</p>
        </article>
      </div>
    </section>
  );
}

export default LandingPage;
