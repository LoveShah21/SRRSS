import { useEffect, useState } from 'react'
import api from '../api/client'

export default function RecruiterDashboardPage() {
  const [jobs, setJobs] = useState([])
  const [selectedJobId, setSelectedJobId] = useState('')
  const [candidates, setCandidates] = useState([])
  const [filters, setFilters] = useState({ skills: '', minYears: '0' })
  const [newJob, setNewJob] = useState({ title: '', department: '', description: '' })

  const loadJobs = async () => {
    const response = await api.get('/jobs')
    setJobs(response.data)
  }

  useEffect(() => {
    loadJobs().catch(() => undefined)
  }, [])

  const loadCandidates = async () => {
    if (!selectedJobId) return
    const response = await api.get(`/jobs/${selectedJobId}/candidates`, {
      params: { skills: filters.skills, minYears: filters.minYears },
    })
    setCandidates(response.data)
  }

  const createJob = async (event) => {
    event.preventDefault()
    await api.post('/jobs', newJob)
    setNewJob({ title: '', department: '', description: '' })
    await loadJobs()
  }

  const scheduleInterview = async (applicationId) => {
    const scheduledAt = new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString()
    await api.patch(`/applications/${applicationId}/schedule-interview`, {
      scheduledAt,
      mode: 'Online',
      notes: 'Initial technical round',
    })
    await loadCandidates()
  }

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold">Recruiter Dashboard</h2>
        <p className="mt-1 text-sm text-gray-600">Create jobs, rank candidates, and schedule interviews.</p>
        <form onSubmit={createJob} className="mt-4 grid gap-3 sm:grid-cols-3">
          <input className="rounded-md border border-gray-300 px-3 py-2" placeholder="Job title" value={newJob.title} onChange={(event) => setNewJob((prev) => ({ ...prev, title: event.target.value }))} required />
          <input className="rounded-md border border-gray-300 px-3 py-2" placeholder="Department" value={newJob.department} onChange={(event) => setNewJob((prev) => ({ ...prev, department: event.target.value }))} required />
          <button className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">Create Job</button>
          <textarea className="sm:col-span-3 rounded-md border border-gray-300 px-3 py-2" rows={3} placeholder="Job description" value={newJob.description} onChange={(event) => setNewJob((prev) => ({ ...prev, description: event.target.value }))} required />
        </form>
      </section>

      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-medium">Ranked Candidates</h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-4">
          <select className="rounded-md border border-gray-300 px-3 py-2" value={selectedJobId} onChange={(event) => setSelectedJobId(event.target.value)}>
            <option value="">Select job</option>
            {jobs.map((job) => (
              <option key={job._id} value={job._id}>{job.title}</option>
            ))}
          </select>
          <input className="rounded-md border border-gray-300 px-3 py-2" placeholder="skills: react,node.js" value={filters.skills} onChange={(event) => setFilters((prev) => ({ ...prev, skills: event.target.value }))} />
          <input className="rounded-md border border-gray-300 px-3 py-2" type="number" min="0" placeholder="min years" value={filters.minYears} onChange={(event) => setFilters((prev) => ({ ...prev, minYears: event.target.value }))} />
          <button className="rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700" onClick={loadCandidates}>Load Ranked List</button>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-gray-600">
                <th className="px-3 py-2">Candidate</th>
                <th className="px-3 py-2">Email</th>
                <th className="px-3 py-2">Match Score</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((row) => (
                <tr key={row._id} className="border-b border-gray-100">
                  <td className="px-3 py-2">{row.candidateId?.name}</td>
                  <td className="px-3 py-2">{row.candidateId?.email}</td>
                  <td className="px-3 py-2">{row.aiMatchScore ?? 0}%</td>
                  <td className="px-3 py-2">{row.status}</td>
                  <td className="px-3 py-2">
                    <button onClick={() => scheduleInterview(row._id)} className="rounded bg-green-600 px-3 py-1 text-white hover:bg-green-700">Schedule</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
