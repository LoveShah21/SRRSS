import { useEffect, useState } from 'react'
import api from '../api/client'

export default function CandidatePortalPage() {
  const [jobs, setJobs] = useState([])
  const [myApplications, setMyApplications] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [selectedJobId, setSelectedJobId] = useState('')
  const [message, setMessage] = useState('')

  const loadData = async () => {
    const jobsResponse = await api.get('/jobs')
    const applicationsResponse = await api.get('/applications/my-applications')
    setJobs(jobsResponse.data)
    setMyApplications(applicationsResponse.data)
  }

  useEffect(() => {
    loadData().catch(() => setMessage('Failed to load candidate data'))
  }, [])

  const submitApplication = async (event) => {
    event.preventDefault()
    if (!selectedJobId || !selectedFile) {
      setMessage('Select job and resume file first')
      return
    }

    const formData = new FormData()
    formData.append('resume', selectedFile)
    await api.post(`/applications/apply/${selectedJobId}`, formData)
    setMessage('Application submitted')
    await loadData()
  }

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold">Candidate Portal</h2>
        <p className="mt-1 text-sm text-gray-600">Upload resume, apply, and track status timeline.</p>
        <form className="mt-4 grid gap-3 sm:grid-cols-3" onSubmit={submitApplication}>
          <select
            className="rounded-md border border-gray-300 px-3 py-2"
            value={selectedJobId}
            onChange={(event) => setSelectedJobId(event.target.value)}
          >
            <option value="">Select job</option>
            {jobs.map((job) => (
              <option value={job._id} key={job._id}>{job.title}</option>
            ))}
          </select>
          <div className="flex w-full items-center overflow-hidden rounded-md border border-gray-300 bg-white">
            <label className="cursor-pointer border-r border-gray-300 bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 shrink-0">
              Choose File
              <input
                type="file"
                accept=".pdf,.docx"
                className="hidden"
                id="file-upload-input"
                onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
              />
            </label>
            <span className="flex-1 truncate px-3 text-sm text-gray-500">
              {selectedFile ? selectedFile.name : 'No file chosen'}
            </span>
            <button 
              type="button"
              className="border-l border-gray-300 bg-gray-50 px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 shrink-0"
              onClick={() => document.getElementById('file-upload-input').click()}
            >
              Upload
            </button>
          </div>
          <button type="submit" className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">Apply</button>
        </form>
        {message && <p className="mt-3 text-sm text-blue-700">{message}</p>}
      </section>

      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-medium">Application Status</h3>
        <div className="mt-3 overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-gray-600">
                <th className="px-3 py-2">Job</th>
                <th className="px-3 py-2">Department</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">AI Match</th>
              </tr>
            </thead>
            <tbody>
              {myApplications.map((application) => (
                <tr key={application._id} className="border-b border-gray-100">
                  <td className="px-3 py-2">{application.jobId?.title}</td>
                  <td className="px-3 py-2">{application.jobId?.department}</td>
                  <td className="px-3 py-2">{application.status}</td>
                  <td className="px-3 py-2">{application.aiMatchScore ?? 0}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
