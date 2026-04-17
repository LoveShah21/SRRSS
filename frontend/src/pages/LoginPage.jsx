import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');

  const onSubmit = async (event) => {
    event.preventDefault();
    setError('');
    try {
      const user = await login(form.email, form.password);
      if (user.role === 'Candidate') navigate('/candidate');
      else if (user.role === 'Admin') navigate('/admin');
      else navigate('/recruiter');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    }
  };

  return (
    <section className="mx-auto max-w-md card mt-12">
      <h1 className="text-3xl font-black text-slate-900 dark:text-white">Welcome Back</h1>
      <p className="mt-2 text-slate-600 dark:text-slate-400">Sign in to manage your recruitment journey.</p>
      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <div>
          <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Email Address</label>
          <input className="input-field mt-1" placeholder="email@example.com" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </div>
        <div>
          <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Password</label>
          <input type="password" className="input-field mt-1" placeholder="••••••••" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </div>
        {error && <p className="text-sm font-medium text-red-500">{error}</p>}
        <button className="btn-primary w-full mt-4">Sign In</button>
      </form>
    </section>
  );
}

export default LoginPage;
