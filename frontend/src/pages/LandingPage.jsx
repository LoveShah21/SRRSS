import { useEffect, useState } from 'react';
import api from '../api/client';
import JobCard from '../components/JobCard';
import StatsSection from '../components/StatsSection';

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
    <div className="space-y-24 pb-20">
      {/* Hero Section */}
      <section className="relative -mt-6 flex min-h-[80vh] flex-col items-center justify-center overflow-hidden rounded-[3rem] bg-indigo-600 px-6 py-24 text-center text-white shadow-[0_32px_64px_-16px_rgba(79,70,229,0.3)] dark:shadow-[0_32px_64px_-16px_rgba(0,0,0,0.5)]">
        {/* Animated Mesh Gradients */}
        <div className="absolute inset-0 z-0">
          <div className="absolute -left-1/4 -top-1/4 h-[80%] w-[80%] animate-pulse rounded-full bg-indigo-400/30 blur-[120px]"></div>
          <div className="absolute -right-1/4 -bottom-1/4 h-[80%] w-[80%] animate-pulse rounded-full bg-pink-500/20 blur-[120px]" style={{ animationDelay: '2s' }}></div>
          <div className="absolute left-1/4 bottom-1/4 h-[40%] w-[40%] animate-bounce rounded-full bg-blue-400/20 blur-[100px]" style={{ animationDuration: '8s' }}></div>
        </div>

        <div className="relative z-10 mx-auto max-w-4xl">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-1.5 text-sm font-semibold backdrop-blur-md">
            <span className="flex h-2 w-2 animate-pulse rounded-full bg-indigo-300"></span>
            Now Powered by Gemini 1.5
          </div>
          
          <h1 className="text-5xl font-black tracking-tight sm:text-7xl">
            Hire Faster. <br />
            <span className="bg-gradient-to-r from-indigo-200 to-pink-200 bg-clip-text text-transparent">Match Smarter.</span>
          </h1>
          
          <p className="mx-auto mt-8 max-w-2xl text-xl text-indigo-100/90 leading-relaxed md:text-2xl">
            SRRSS uses state-of-the-art AI to screen resumes, detect bias, and match candidates with precision.
          </p>
          
          <form onSubmit={handleSearch} className="mt-12 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <div className="group relative w-full max-w-md">
              <input
                type="text"
                placeholder="Job title, skills, or department..."
                className="w-full rounded-2xl border-none bg-white/10 px-8 py-5 text-lg text-white placeholder-indigo-200 backdrop-blur-xl transition-all focus:bg-white focus:text-slate-900 focus:outline-none focus:ring-8 focus:ring-white/20"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <div className="absolute inset-0 -z-10 rounded-2xl bg-indigo-400/20 blur-xl transition-opacity opacity-0 group-focus-within:opacity-100"></div>
            </div>
            <button type="submit" className="w-full rounded-2xl bg-white px-10 py-5 text-lg font-bold text-indigo-600 shadow-2xl transition-all hover:scale-105 hover:bg-indigo-50 active:scale-95 sm:w-auto">
              Find Jobs
            </button>
          </form>
        </div>
      </section>

      {/* Stats Section */}
      <StatsSection />

      {/* Bento Box Features */}
      <section className="space-y-12">
        <div className="text-center">
          <h2 className="text-3xl font-black text-slate-900 dark:text-white sm:text-4xl">The Future of Recruiting</h2>
          <p className="mt-4 text-slate-600 dark:text-slate-400 font-medium">Built for speed, transparency, and fairness.</p>
        </div>

        <div className="grid gap-6 md:grid-cols-6 md:grid-rows-2">
          {/* Main Feature - Recruiters */}
          <div className="card group md:col-span-3 md:row-span-2">
            <div className="card-gradient"></div>
            <div className="relative z-10 flex h-full flex-col">
              <div className="mb-8 flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-lg shadow-indigo-200 dark:bg-indigo-500">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-8 w-8">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
                </svg>
              </div>
              <h3 className="text-2xl font-black dark:text-white">Advanced Recruiter Insights</h3>
              <p className="mt-4 text-slate-600 dark:text-slate-400">
                AI-ranked candidate pools with detailed match summaries. Screen thousands of resumes in seconds with zero manual effort.
              </p>
              <div className="mt-auto pt-12">
                <div className="flex -space-x-3">
                   {[1,2,3,4].map(i => (
                     <div key={i} className={`h-10 w-10 rounded-full border-2 border-white bg-slate-200 dark:border-slate-800 dark:bg-slate-700`}></div>
                   ))}
                </div>
                <p className="mt-2 text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-widest">Join 500+ Hiring Teams</p>
              </div>
            </div>
          </div>

          {/* Feature - Candidate */}
          <div className="card md:col-span-3">
            <div className="card-gradient"></div>
            <div className="flex items-start gap-6">
              <div className="shrink-0 h-12 w-12 rounded-xl bg-pink-100 flex items-center justify-center text-pink-600 dark:bg-pink-500/10 dark:text-pink-400">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-6 w-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-black dark:text-white">Smart Candidate Portal</h3>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">Get real-time feedback on your applications and track status with ease.</p>
              </div>
            </div>
          </div>

          {/* Feature - Bias Detection */}
          <div className="card md:col-span-3">
            <div className="card-gradient"></div>
            <div className="flex items-start gap-6">
              <div className="shrink-0 h-12 w-12 rounded-xl bg-amber-100 flex items-center justify-center text-amber-600 dark:bg-amber-500/10 dark:text-amber-400">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-6 w-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-black dark:text-white">Fairness Built-in</h3>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">Automated bias detection ensures Every candidate gets a fair shake.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Jobs Section */}
      <section id="jobs" className="space-y-12">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-3xl font-black text-slate-900 dark:text-white">Open Opportunities</h2>
            <p className="mt-1 text-slate-500 dark:text-slate-400">Find the perfect match for your skill set.</p>
          </div>
          <span className="inline-flex items-center rounded-2xl bg-indigo-50 px-4 py-2 text-sm font-bold text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400">
            {jobs.length} roles available
          </span>
        </div>

        {loading ? (
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-64 animate-pulse rounded-3xl bg-slate-100 dark:bg-slate-800"></div>
            ))}
          </div>
        ) : jobs.length > 0 ? (
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {jobs.map((job) => (
              <JobCard key={job._id} job={job} />
            ))}
          </div>
        ) : (
          <div className="rounded-[2.5rem] border-2 border-dashed border-slate-200 dark:border-slate-800 py-32 text-center">
            <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl bg-slate-50 dark:bg-slate-900 mb-6">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-10 w-10 text-slate-400">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">No matches found</h3>
            <p className="mt-2 text-slate-500 dark:text-slate-400">Try adjusting your search criteria or explore trending categories.</p>
            <button 
              onClick={() => setSearchQuery('')}
              className="mt-8 btn-secondary"
            >
              Clear Search
            </button>
          </div>
        )}
      </section>
      
      {/* Newsletter / Activity Section */}
      <section className="card bg-indigo-600/5 dark:bg-indigo-500/5 p-12 text-center">
        <h2 className="text-2xl font-black dark:text-white">Stay in the Loop</h2>
        <p className="mt-4 text-slate-600 dark:text-slate-400">Get notified about new jobs and AI-powered tips for your career.</p>
        <div className="mt-8 mx-auto flex max-w-md gap-3">
          <input type="email" placeholder="email@company.com" className="input-field" />
          <button className="btn-primary whitespace-nowrap">Subscribe</button>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;
