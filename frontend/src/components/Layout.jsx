import { Link, Outlet, useLocation } from 'react-router-dom'

function NavItem({ to, label, activePath }) {
  const isActive = activePath.startsWith(to)
  return (
    <Link
      to={to}
      className={`rounded-md px-3 py-2 text-sm font-medium ${
        isActive ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'
      }`}
    >
      {label}
    </Link>
  )
}

export default function Layout() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <h1 className="text-xl font-semibold">SRRSS</h1>
          <nav className="flex items-center gap-2">
            <NavItem to="/candidate" label="Candidate" activePath={location.pathname} />
            <NavItem to="/recruiter" label="Recruiter" activePath={location.pathname} />
            <NavItem to="/admin" label="Admin" activePath={location.pathname} />
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  )
}
