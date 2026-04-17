import { useEffect, useState } from 'react';

const StatItem = ({ label, value, suffix = "", delay = 0 }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = parseInt(value);
    if (start === end) return;

    let totalMilisecondDurration = 2000;
    let incrementTime = (totalMilisecondDurration / end);

    let timer = setInterval(() => {
      start += 1;
      setCount(start);
      if (start === end) clearInterval(timer);
    }, incrementTime);

    return () => clearInterval(timer);
  }, [value, delay]);

  return (
    <div className="flex flex-col items-center justify-center p-6 text-center">
      <div className="text-4xl font-black text-indigo-600 dark:text-indigo-400 sm:text-5xl">
        {count}{suffix}
      </div>
      <div className="mt-2 text-sm font-semibold uppercase tracking-widest text-slate-500 dark:text-slate-400">
        {label}
      </div>
    </div>
  );
};

export default function StatsSection() {
  const stats = [
    { label: "AI Matches", value: "850", suffix: "+" },
    { label: "Active Jobs", value: "120", suffix: "" },
    { label: "Hiring Rate", value: "94", suffix: "%" },
    { label: "Hours Saved", value: "2400", suffix: "+" },
  ];

  return (
    <section className="relative overflow-hidden rounded-3xl bg-slate-50 py-12 dark:bg-slate-900/50">
      <div className="absolute inset-0 opacity-10 dark:opacity-20">
        <div className="absolute left-0 top-0 h-full w-full bg-[radial-gradient(#6366f1_1px,transparent_1px)] [background-size:20px_20px]"></div>
      </div>
      
      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {stats.map((stat, idx) => (
            <StatItem key={stat.label} {...stat} delay={idx * 200} />
          ))}
        </div>
      </div>
    </section>
  );
}
