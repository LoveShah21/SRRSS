import { useEffect, useState } from 'react'
import api from '../api/client'

export default function AdminConsolePage() {
  const [users, setUsers] = useState([])
  const [analytics, setAnalytics] = useState(null)

  const loadAdminData = async () => {
    const [usersResponse, analyticsResponse] = await Promise.all([
      api.get('/admin/users'),
      api.get('/admin/analytics'),
    ])
    setUsers(usersResponse.data)
    setAnalytics(analyticsResponse.data)
  }

  useEffect(() => {
    loadAdminData().catch(() => undefined)
  }, [])

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold">Admin Console</h2>
        <p className="mt-1 text-sm text-gray-600">Manage users, configuration, and hiring analytics.</p>
      </section>

      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-medium">Usage Analytics</h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          <div className="rounded-md bg-gray-50 p-4">
            <p className="text-xs text-gray-500">Total Users</p>
            <p className="text-2xl font-semibold">{analytics?.totals?.users ?? 0}</p>
          </div>
          <div className="rounded-md bg-gray-50 p-4">
            <p className="text-xs text-gray-500">Total Jobs</p>
            <p className="text-2xl font-semibold">{analytics?.totals?.jobs ?? 0}</p>
          </div>
          <div className="rounded-md bg-gray-50 p-4">
            <p className="text-xs text-gray-500">Total Applications</p>
            <p className="text-2xl font-semibold">{analytics?.totals?.applications ?? 0}</p>
          </div>
        </div>
      </section>

      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-medium">User Management</h3>
        <div className="mt-3 overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-gray-600">
                <th className="px-3 py-2">Name</th>
                <th className="px-3 py-2">Email</th>
                <th className="px-3 py-2">Role</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user._id} className="border-b border-gray-100">
                  <td className="px-3 py-2">{user.name}</td>
                  <td className="px-3 py-2">{user.email}</td>
                  <td className="px-3 py-2">{user.role}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
