import { useEffect, useState } from 'react';
import api from '../api/client';
import JobCard from '../components/JobCard';

function LandingPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchJobs = async () => {
      setLoading(true);
      try {
        const response = await api.get('/jobs', {
          params: { q: searchQuery }
        });
        setJobs(response.data);
      } catch (error) {
        console.error('Error fetching jobs:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, [searchQuery]);

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchQuery(searchTerm);
  };

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-indigo-600 px-6 py-16 text-center text-white shadow-2xl">
        <div className="relative z-10 mx-auto max-w-2xl">
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
            Find Your Dream Career <span className="text-indigo-200">Today</span>
          </h1>
          <p className="mt-4 text-lg text-indigo-100">
            AI-powered recruitment system that matches your skills with the best opportunities.
          </p>
          
          <form onSubmit={handleSearch} className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
            <div className="relative w-full max-w-sm">
              <input
                type="text"
                placeholder="Search jobs, skills, or departments..."
                className="w-full rounded-2xl border-none bg-white/10 px-6 py-4 text-white placeholder-indigo-200 backdrop-blur-md transition-all focus:bg-white focus:text-slate-900 focus:outline-none focus:ring-4 focus:ring-indigo-400/50"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button type="submit" className="w-full rounded-2xl bg-white px-8 py-4 font-bold text-indigo-600 shadow-lg transition-all hover:bg-indigo-50 active:scale-95 sm:w-auto">
              Search Jobs
            </button>
          </form>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-indigo-500/20 blur-3xl"></div>
        <div className="absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-indigo-400/20 blur-3xl"></div>
      </section>

      {/* Stats/Portal Section */}
      <section className="grid gap-6 md:grid-cols-3">
        <div className="card">
          <div className="card-gradient"></div>
          <h3 className="text-xl font-bold">Candidate Portal</h3>
          <p className="mt-2 text-sm text-slate-600">Smart resume screening with real-time feedback and application tracking.</p>
        </div>
        <div className="card">
          <div className="card-gradient"></div>
          <h3 className="text-xl font-bold">Recruiter Dashboard</h3>
          <p className="mt-2 text-sm text-slate-600">AI-ranked candidates and bias-free job descriptions for better hiring.</p>
        </div>
        <div className="card">
          <div className="card-gradient"></div>
          <h3 className="text-xl font-bold">Admin Console</h3>
          <p className="mt-2 text-sm text-slate-600">Full audit logging, role management, and system-wide analytics.</p>
        </div>
      </section>

      {/* Jobs Section */}
      <section id="jobs" className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-slate-900">Current Openings</h2>
          <span className="text-sm font-medium text-slate-500">{jobs.length} roles found</span>
        </div>

        {loading ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="card h-48 animate-pulse bg-slate-100"></div>
            ))}
          </div>
        ) : jobs.length > 0 ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {jobs.map((job) => (
              <JobCard key={job._id} job={job} />
            ))}
          </div>
        ) : (
          <div className="rounded-3xl border-2 border-dashed border-slate-200 py-20 text-center">
            <h3 className="text-lg font-medium text-slate-900">No jobs found</h3>
            <p className="mt-1 text-slate-500">Try adjusting your search criteria or come back later.</p>
          </div>
        )}
      </section>
    </div>
  );
}

export default LandingPage;
