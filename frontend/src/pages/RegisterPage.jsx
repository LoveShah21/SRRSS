import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'Candidate' });
  const [error, setError] = useState('');

  const onSubmit = async (event) => {
    event.preventDefault();
    setError('');
    try {
      const user = await register(form);
      if (user.role === 'Candidate') navigate('/candidate');
      else navigate('/recruiter');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
    }
  };

  return (
    <section className="mx-auto max-w-md card">
      <h1 className="text-2xl font-semibold">Register</h1>
      <form onSubmit={onSubmit} className="mt-4 space-y-3">
        <input className="w-full rounded-md border border-slate-300 px-3 py-2" placeholder="Full Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input className="w-full rounded-md border border-slate-300 px-3 py-2" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input type="password" className="w-full rounded-md border border-slate-300 px-3 py-2" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <select className="w-full rounded-md border border-slate-300 px-3 py-2" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
          <option value="Candidate">Candidate</option>
          <option value="Recruiter">Recruiter</option>
        </select>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button className="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">Create Account</button>
      </form>
    </section>
  );
}

export default RegisterPage;
