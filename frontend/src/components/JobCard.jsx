import { Link } from 'react-router-dom';

const JobCard = ({ job }) => {
  return (
    <div className="card group">
      <div className="card-gradient opacity-0 transition-opacity duration-500 group-hover:opacity-100"></div>
      
      <div className="flex flex-col h-full justify-between">
        <div>
          <div className="flex items-center justify-between mb-4">
            <span className="badge">{job.department}</span>
            <span className="text-xs text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider">
              {new Date(job.createdAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
            </span>
          </div>
          
          <h3 className="text-xl font-black text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
            {job.title}
          </h3>
          
          <p className="mt-3 text-sm text-slate-600 dark:text-slate-400 line-clamp-3 leading-relaxed">
            {job.description}
          </p>

          <div className="mt-4 flex flex-wrap gap-2">
            <span className="inline-flex items-center rounded-lg bg-slate-50 px-2 py-1 text-[10px] font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-400">
               Full-time
            </span>
            <span className="inline-flex items-center rounded-lg bg-slate-50 px-2 py-1 text-[10px] font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-400">
               Remote
            </span>
          </div>
        </div>

        <div className="mt-8 flex items-center justify-between">
          <div className="flex flex-wrap gap-1">
            {job.biasFlags && job.biasFlags.length > 0 ? (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-3 py-1 text-[10px] font-bold text-amber-600 dark:bg-amber-500/10 dark:text-amber-400">
                <span className="h-1 w-1 rounded-full bg-amber-500 animate-pulse"></span>
                AI Inspected
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-[10px] font-bold text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400">
                <span className="h-1 w-1 rounded-full bg-emerald-500"></span>
                Fair Hiring
              </span>
            )}
          </div>
          
          <Link 
            to="/login" 
            className="group/btn flex items-center gap-1 text-sm font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-all"
          >
            Apply Now
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="h-4 w-4 transition-transform group-hover/btn:translate-x-1">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default JobCard;
