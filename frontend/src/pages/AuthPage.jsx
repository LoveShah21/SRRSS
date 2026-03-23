import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const onSubmit = async (event) => {
    event.preventDefault()
    setError('')
    try {
      const route = isLogin ? '/auth/login' : '/auth/register'
      const payload = isLogin ? { email: form.email, password: form.password } : form
      const response = await api.post(route, payload)
      localStorage.setItem('srrss_token', response.data.token)
      localStorage.setItem('srrss_role', response.data.user.role)
      const role = response.data.user.role
      if (role === 'Admin') navigate('/admin')
      else if (role === 'Recruiter') navigate('/recruiter')
      else navigate('/candidate')
    } catch (requestError) {
      setError(requestError?.response?.data?.error || 'Authentication failed')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="mb-2 text-2xl font-semibold text-gray-900">SRRSS Auth Gateway</h2>
        <p className="mb-6 text-sm text-gray-600">
          {isLogin ? 'Sign in to continue' : 'Create a candidate account'}
        </p>
        <form onSubmit={onSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Name</label>
              <input
                className="w-full rounded-md border border-gray-300 px-3 py-2"
                value={form.name}
                onChange={(event) => setForm((previous) => ({ ...previous, name: event.target.value }))}
                required
              />
            </div>
          )}
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              className="w-full rounded-md border border-gray-300 px-3 py-2"
              value={form.email}
              onChange={(event) => setForm((previous) => ({ ...previous, email: event.target.value }))}
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Password</label>
            <input
              type="password"
              className="w-full rounded-md border border-gray-300 px-3 py-2"
              value={form.password}
              onChange={(event) => setForm((previous) => ({ ...previous, password: event.target.value }))}
              required
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button className="w-full rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700">
            {isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>
        <button
          className="mt-4 text-sm text-blue-600"
          onClick={() => setIsLogin((previous) => !previous)}
          type="button"
        >
          {isLogin ? 'Need an account? Register' : 'Already have an account? Sign in'}
        </button>
      </div>
    </div>
  )
}
