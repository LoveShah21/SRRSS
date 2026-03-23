import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function MainNav() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const onLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <Link className="text-lg font-semibold text-blue-700" to="/">
          SRRSS
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          {!user && (
            <>
              <Link to="/login" className="text-slate-700 hover:text-slate-900">Login</Link>
              <Link to="/register" className="rounded-md bg-blue-600 px-3 py-1.5 text-white hover:bg-blue-700">Register</Link>
            </>
          )}
          {user?.role === 'Candidate' && <Link to="/candidate">Candidate Portal</Link>}
          {(user?.role === 'Recruiter' || user?.role === 'Admin') && <Link to="/recruiter">Recruiter</Link>}
          {user?.role === 'Admin' && <Link to="/admin">Admin</Link>}
          {user && (
            <button type="button" className="rounded-md border border-slate-300 px-3 py-1.5" onClick={onLogout}>
              Logout
            </button>
          )}
        </nav>
      </div>
    </header>
  );
}

export default MainNav;
