import { Link } from 'react-router-dom';

const JobCard = ({ job }) => {
  return (
    <div className="card group">
      <div className="card-gradient opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
      
      <div className="flex flex-col h-full justify-between">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="badge">{job.department}</span>
            <span className="text-xs text-slate-400 font-medium">
              {new Date(job.createdAt).toLocaleDateString()}
            </span>
          </div>
          
          <h3 className="text-lg font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
            {job.title}
          </h3>
          
          <p className="mt-2 text-sm text-slate-600 line-clamp-3">
            {job.description}
          </p>
        </div>

        <div className="mt-6 flex items-center justify-between">
          <div className="flex flex-wrap gap-1">
            {job.biasFlags && job.biasFlags.length > 0 ? (
              <span className="inline-flex items-center gap-1 rounded bg-amber-50 px-2 py-0.5 text-[10px] font-medium text-amber-600">
                AI Inspected
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 rounded bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-600">
                Verified
              </span>
            )}
          </div>
          
          <Link 
            to="/login" 
            className="text-sm font-semibold text-indigo-600 hover:text-indigo-700 underline-offset-4 hover:underline"
          >
            Apply Now
          </Link>
        </div>
      </div>
    </div>
  );
};

export default JobCard;
