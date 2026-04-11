import { useMemo, useState, useCallback, useEffect } from "react";
import { motion } from "framer-motion";
import Select from "react-select";
import locationOptions from "./data/locations";
import { AnimatePresence } from "framer-motion";

const API_BASE = "https://aijobagent.duckdns.org";

const fadeInUp = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0 },
};

export default function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeData, setResumeData] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [ats, setATS] = useState(null);
  const [application, setApplication] = useState(null);
  const [activeJob, setActiveJob] = useState(null);
  const [jobQuery, setJobQuery] = useState("");

  const [uploadStatus, setUploadStatus] = useState("");
  const [matchStatus, setMatchStatus] = useState("");
  const [applyStatus, setApplyStatus] = useState("");

  const [uploading, setUploading] = useState(false);
  const [matching, setMatching] = useState(false);
  const [applying, setApplying] = useState(false);

  const [location, setLocation] = useState(null);
  const [jobtype, setJobtype] = useState("");
  const [remote, setRemote] = useState(false);

  const [analysisData, setAnalysisData] = useState({});
  const [analyzingId, setAnalyzingId] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  const canMatch = Boolean(resumeData) && !matching;


  const sortedJobs = useMemo(
  () =>
    [...jobs].sort((a, b) => {
      const scoreA = Number(a.score) || 0;
      const scoreB = Number(b.score) || 0;
      return scoreB - scoreA; // Descending order (highest first)
    }),
  [jobs]
);

  const handleUpload = useCallback(async () => {
    if (!resumeFile) {
      setUploadStatus("Please select a resume PDF first.");
      return;
    }

    setUploading(true);
    setUploadStatus("Analyzing your resume...");
    setJobs([]);
    setApplication(null);
    setApplyStatus("");
    setMatchStatus("");
    setResumeData(null);
    setATS(null);

    try {
      const formData = new FormData();
      formData.append("file", resumeFile);

      const response = await fetch(`${API_BASE}/resume/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.error || errorData.message || `Upload failed (${response.status})`;
        throw new Error(errorMessage);
      }

      const data = await response.json();

      if (!data.is_resume) {
        setUploadStatus(data.message || "Uploaded file is not a valid resume.");
        setResumeData(null);
        return;
      }
      
      setATS(data.ats);
      setResumeData(data);
      setUploadStatus("Resume parsed successfully.");

    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus(error.message || "Could not parse resume.");
      setResumeData(null);
    } finally {
      setUploading(false);
    }
  }, [resumeFile]);

  const handleMatch = useCallback(async () => {
    if (!resumeData) return;

    setMatching(true);
    setJobs([]);
    setMatchStatus("Finding top matching roles...");

    try {
      const response = await fetch(`${API_BASE}/jobs/find`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          data: resumeData?.data ?? {},
          query: jobQuery?.trim() ?? "",
          location: location || "India",
          jobtype: jobtype || undefined,
          remote: remote || false
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.error || errorData.message || `Job matching failed (${response.status})`;
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      const matches = data.matches || [];
      setJobs([...matches]);
      setMatchStatus(matches.length ? "Matches updated." : "No matches found.");
    } catch (error) {
      console.error('Match error:', error);
      setMatchStatus("Error: " + error.message);
    } finally {
      setMatching(false);
    }
  }, [resumeData, jobQuery, location, jobtype, remote]);

  const handleAnalyze = useCallback(async (job, idx) => {
  const id = idx; // IMPORTANT FIX

  setAnalyzingId(id);

  try {
    const res = await fetch(`${API_BASE}/jobs/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        resume: resumeData,
        job: job
      })
    });

    const data = await res.json();

    setAnalysisData(prev => ({
      ...prev,
      [id]: data
    }));

  } catch (err) {
    setAnalysisData(prev => ({
      ...prev,
      [id]: { error: err.message }
    }));
  } finally {
    setAnalyzingId(null);
  }
}, [resumeData]);
  
  const handleApply = useCallback(async (job) => {
    if (!resumeData) return;

    setApplying(true);
    setActiveJob(job);
    setApplyStatus(`Generating application for ${job.title || "this role"}...`);

    try {
      const response = await fetch(`${API_BASE}/apply/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume: resumeData.data || {},
          job,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.error || errorData.message || `Application generation failed (${response.status})`;
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setApplication(data);
      setApplyStatus("Application generated successfully.");
    } catch (error) {
      console.error('Apply error:', error);
      setApplyStatus(error.message || "Could not generate application.");
      setApplication(null);
    } finally {
      setApplying(false);
    }
  }, [resumeData]);

  return (
    <div className="relative min-h-screen overflow-x-hidden">
      <div className="pointer-events-none fixed -left-24 -top-24 h-80 w-80 rounded-full bg-violet-600/40 blur-3xl animate-floaty" />
      <div className="pointer-events-none fixed -bottom-24 -right-24 h-80 w-80 rounded-full bg-cyan-500/40 blur-3xl animate-floaty [animation-delay:-4s]" />
      <div className="pointer-events-none fixed inset-0 bg-[linear-gradient(rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[size:42px_42px] [mask-image:radial-gradient(circle_at_center,black_36%,transparent_90%)]" />

      <main className="relative z-20 mx-auto w-[min(1080px,92vw)] py-10">
        <motion.header
          variants={fadeInUp}
          initial="hidden"
          animate="show"
          transition={{ duration: 0.55 }}
          className="mb-8 text-center px-4"
        >
          <span className="inline-flex rounded-full border border-white/20 bg-violet-500/20 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-violet-200">
            AI Powered
          </span>
          <h1 className="mt-4 text-3xl font-extrabold sm:text-4xl md:text-5xl">Job Hunt Copilot</h1>
          <p className="mx-auto mt-3 max-w-2xl text-sm text-slate-300 md:text-base">
            Understand your resume, match real roles, and generate personalized applications with one smooth flow.
          </p>
        </motion.header>

        <section className="grid gap-4">
          <Card title="1) Upload Resume">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                className="w-full sm:max-w-xs rounded-lg border border-white/15 bg-slate-950/70 px-3 py-2 text-sm text-slate-300 file:mr-3 file:rounded-md file:border-0 file:bg-violet-500 file:px-3 file:py-1.5 file:text-white file:cursor-pointer"
              />
              <ActionButton 
                onClick={handleUpload} 
                disabled={uploading}
                className="w-full sm:w-auto"
              >
                {uploading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Analyzing...
                  </span>
                ) : "Analyze Resume"}
              </ActionButton>
            </div>
            <Status>{uploadStatus}</Status>
          </Card>

          {ats && (
            <Card title="1.1) ATS Analysis">
              <div className="flex flex-col items-center mb-6">
                <div className="relative w-32 h-32">
                  <svg className="w-full h-full rotate-[-90deg]">
                    <circle cx="64" cy="64" r="56" stroke="#1e293b" strokeWidth="10" fill="none" />
                    <circle
                      cx="64" cy="64" r="56" stroke="url(#gradient)" strokeWidth="10" fill="none"
                      strokeDasharray={2 * Math.PI * 56}
                      strokeDashoffset={2 * Math.PI * 56 * (1 - ats.ats_score / 100)}
                      strokeLinecap="round"
                      style={{ transition: "stroke-dashoffset 1s ease-in-out" }}
                    />
                    <defs>
                      <linearGradient id="gradient">
                        <stop offset="0%" stopColor="#8b5cf6" /><stop offset="100%" stopColor="#06b6d4" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center text-2xl font-bold">
                    {ats.ats_score}%
                  </div>
                </div>
                <p className="text-sm text-slate-400 text-center mt-4 max-w-md">{ats.summary}</p>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <ATSList title="Strengths" items={ats.strengths} color="text-green-400" />
                <ATSList title="Weaknesses" items={ats.weaknesses} color="text-red-400" />
                <ATSList title="Suggestions" items={ats.improvement_suggestions} color="text-yellow-400" />
                <ATSList title="Missing Keywords" items={ats.keywords_missing} color="text-blue-400" />
              </div>
            </Card>
          )}

          <Card title="2) Match Jobs">
            <div className="space-y-4">
               <div>
              <p className="text-xs text-slate-500 mt-1">
                  All filters are optional — leave blank for broader results
              </p>
            </div>
            <div className="space-y-3">
              <div>
                <input
                  value={jobQuery}
                  onChange={(e) => setJobQuery(e.target.value)}
                  placeholder="Job title / keyword (optional). Leave blank to auto-detect from resume."
                  className="w-full rounded-lg border border-white/15 bg-slate-950/70 px-3 py-2 text-sm text-slate-200 placeholder:text-slate-500"
                />
              </div>
              
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="w-full sm:w-48">
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <Select
                      options={locationOptions}
                      value={locationOptions.find(opt => opt.value === location) || null}
                      onChange={(option) => setLocation(option ? option.value : null)}
                      menuPortalTarget={document.body}
                      placeholder="Select Location..."
                      isSearchable
                      isClearable
                      styles={{
                        control: (base) => ({
                          ...base,
                          backgroundColor: "#020617",
                          borderColor: "rgba(255,255,255,0.15)",
                          borderRadius: "10px",
                          padding: "2px",
                          boxShadow: "none",
                          color: "#e2e8f0",
                          minHeight: "40px",
                        }),
                        menu: (base) => ({
                          ...base,
                          backgroundColor: "#020617",
                          border: "1px solid rgba(255,255,255,0.1)",
                          zIndex: 9999,
                        }),
                        menuPortal: (base) => ({
                          ...base,
                          zIndex: 9999,
                        }),
                        option: (base, state) => ({
                          ...base,
                          backgroundColor: state.isFocused
                            ? "rgba(139,92,246,0.3)"
                            : "transparent",
                          color: "#e2e8f0",
                          cursor: "pointer",
                        }),
                        singleValue: (base) => ({
                          ...base,
                          color: "#e2e8f0",
                        }),
                        input: (base) => ({
                          ...base,
                          color: "#e2e8f0",
                        }),
                        placeholder: (base) => ({
                          ...base,
                          color: "#64748b",
                        }),
                      }}
                    />
                  </motion.div>
                </div>

                <select
                  value={jobtype}
                  onChange={(e) => setJobtype(e.target.value)}
                  className="w-full sm:w-auto rounded-lg border border-white/15 bg-slate-950/70 px-3 py-2 text-sm text-slate-200"
                >
                  <option value="">Job Type</option>
                  <option value="Internship">Internship</option>
                  <option value="Fresher">Fresher</option>
                  <option value="Senior">Senior</option>
                </select>

                <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    className="accent-violet-500"
                    checked={remote}
                    onChange={(e) => setRemote(e.target.checked)}
                  />
                  Remote only
                </label>
              </div>
            </div>
          <motion.div whileTap={{ scale: 0.95 }} className="w-full sm:w-auto">
            <ActionButton 
              onClick={handleMatch} 
              disabled={!canMatch}
              className="w-full sm:w-auto"
            >
              {matching ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Finding...
                </span>
              ) : "Find Top Matches"}
            </ActionButton>
          </motion.div>  
            <Status>{matchStatus}</Status>
            {matching && (
              <div className="flex items-center justify-center py-8">
                <div className="flex items-center gap-3 text-cyan-400">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  <span className="text-sm">Searching across multiple job platforms...</span>
                </div>
              </div>
            )}
            

<div className="mt-3 grid gap-3">
  {sortedJobs.map((job, idx) => {
    const id = idx;
    const isExpanded = expandedId === id;
    const analysis = analysisData[id];
    const isAnalyzing = analyzingId === id;

    return (
      <motion.article
        key={id}
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.22, delay: idx * 0.05 }}
        className="relative z-10 overflow-hidden rounded-2xl border border-white/15 bg-slate-950/60 p-4"
      >
        {/* HEADER */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <h3 className="text-lg font-semibold">
            {job.title || "Untitled Role"}
          </h3>

          {job.score && (
            <span
              className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-bold ${
                job.score >= 80
                  ? "bg-green-500/20 text-green-400"
                  : job.score >= 60
                  ? "bg-yellow-500/20 text-yellow-400"
                  : "bg-red-500/20 text-red-400"
              }`}
            >
              {job.score}% Match
            </span>
          )}
        </div>

        <p className="mt-1 text-sm text-slate-300">
          {job.company || "Unknown Company"} • {job.location || "N/A"}
        </p>

         <div className="flex items-center gap-2 mt-1">
                    {job.source && (
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                        job.source === "internshala" ? "bg-blue-500/20 text-blue-300" :
                        job.source === "adzuna" ? "bg-purple-500/20 text-purple-300" :
                        job.source === "jsearch" ? "bg-green-500/20 text-green-300" :
                        "bg-gray-500/20 text-gray-300"
                      }`}>
                        {job.source}
                      </span>
                    )}
                  </div>

        {/* BUTTONS */}
        <div className="mt-3 flex flex-col sm:flex-row gap-2">
          {/* APPLY */}
          <ActionButton
            onClick={() => handleApply(job)}
            disabled={applying}
          >
            {applying && activeJob?.title === job.title
              ? "Generating..."
              : "Generate Application"}
          </ActionButton>

          {/* ANALYZE BUTTON */}
          <button
            className="rounded-xl border border-white/20 px-4 py-2 text-sm hover:bg-white/5"
            onClick={() => {
              setExpandedId(isExpanded ? null : id);

              if (!isExpanded && !analysisData[id]) {
                handleAnalyze(job, id);
              }
            }}
          >
            {isExpanded ? "Hide Analysis" : "Analyze"}
          </button>

          {/* OPEN JOB */}
          <a
            href={job.url || "#"}
            target="_blank"
            rel="noreferrer"
            className="rounded-xl border border-white/20 px-4 py-2 text-sm text-center hover:bg-white/5"
          >
            Open Job
          </a>
        </div>

        {/* LOADING */}
        {isAnalyzing && (
          <div className="mt-2 text-yellow-400 text-sm animate-pulse">
            🔍 Analyzing...
          </div>
        )}

        {/* EXPANDABLE SECTION */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="mt-4 border-t border-white/10 pt-3 space-y-3">
                {!analysis ? (
                  <p className="text-yellow-400 text-sm animate-pulse">
                    Analyzing job...
                  </p>
                ) : analysis.error ? (
                  <div className="text-red-400 text-sm">
                    <p className="font-semibold">Analysis Failed</p>
                    <p>{analysis.error}</p>
                  </div>
                ) : (
                  <>
                    {/* SCORE */}
                    <div className="flex gap-4 flex-wrap">
                      <p className="text-sm font-semibold">
                        Match Score:
                        <span className="ml-2 text-green-400 font-bold">
                          {analysis.score}%
                        </span>
                      </p>
                    </div>

                    {/* SUMMARY */}
                    {analysis.reason && (
                      <p className="text-sm text-slate-300">
                        <strong>Reason:</strong> {analysis.reason}
                      </p>
                    )}

                    {/* MISSING SKILLS */}
                    {analysis.missing_skills?.length > 0 && (
                      <div>
                        <p className="text-sm font-semibold">
                          Missing Skills:
                        </p>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {analysis.missing_skills.map((skill, i) => (
                            <span
                              key={i}
                              className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* SUGGESTION */}
                    {analysis.suggestion && (
                      <div className="text-sm text-green-300">
                        <strong>Suggestion:</strong>{" "}
                        {analysis.suggestion}
                      </div>
                    )}
                  </>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.article>
    );
  })}
</div>
            </div>
          </Card>

          <Card title="3) Application Output">
            <Status>{applyStatus}</Status>
            {application ? (
              <motion.article
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                className="mt-2 rounded-2xl border border-white/15 bg-slate-950/60 p-4"
              >
                <h3 className="text-lg font-semibold">
                  {application.title || "Role"} @ {application.company || "Unknown Company"}
                </h3>
                <p className="mt-3 text-sm">
                  <strong>Why fit:</strong> {application.application?.why_fit || "N/A"}
                </p>
                <p className="mt-2 text-sm">
                  <strong>Strengths:</strong>{" "}
                  {Array.isArray(application.application?.strengths)
                    ? application.application.strengths.join(", ")
                    : "N/A"}
                </p>
                <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-slate-200">
                  <strong>Cover letter:</strong>{" "}
                  {application.application?.cover_letter || "N/A"}
                </p>
              </motion.article>
            ) : null}
          </Card>
        </section>
      </main>
    </div>
  );
}

function Card({ title, children }) {
  return (
    <motion.section
      variants={fadeInUp}
      initial="hidden"
      animate="show"
      transition={{ duration: 0.45 }}
      className="rounded-2xl border border-white/20 bg-slate-900/60 p-5 shadow-glow backdrop-blur-md"
    >
      <h2 className="mb-3 text-lg font-semibold">{title}</h2>
      {children}
    </motion.section>
  );
}

function ATSList({ title, items, color }) {
  if (!items?.length) return null;
  return (
    <div>
      <h3 className={`${color} font-semibold mb-2`}>{title}</h3>
      <ul className="text-sm text-slate-300 space-y-1">
        {items.map((item, i) => <li key={i}>• {item}</li>)}
      </ul>
    </div>
  );
}

function JobCard({ job, idx, onApply, applying, activeJob }) {
  return (
    <motion.article initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }} className="rounded-xl border border-white/10 bg-slate-950/40 p-4">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-bold text-lg">{job.title}</h3>
          <p className="text-sm text-slate-400">{job.company} • {job.location}</p>
        </div>
        <span className="bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded text-xs font-bold">{job.score}% Match</span>
      </div>
      <p className="mt-3 text-sm text-slate-300">{job.reason}</p>
      <div className="mt-4 flex gap-3">
        <ActionButton onClick={() => onApply(job)} disabled={applying}>
          {applying && activeJob?.title === job.title ? "Generating..." : "Apply with AI"}
        </ActionButton>
        {job.url && <a href={job.url} target="_blank" rel="noreferrer" className="px-4 py-2 text-sm border border-white/20 rounded-xl hover:bg-white/5">View Posting</a>}
      </div>
    </motion.article>
  );
}

function ActionButton({ children, className = "", ...props }) {
  return (
    <button
      {...props}
      className={`rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 px-4 py-2 text-sm font-bold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
    >
      {children}
    </button>
  );
}

function Status({ children }) {
  return <p className="mt-2 min-h-5 text-sm text-slate-400">{children}</p>;
}
