import { useMemo, useState } from "react";
import { motion } from "framer-motion";

const API_BASE = "http://127.0.0.1:8000";

const fadeInUp = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0 },
};

export default function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeData, setResumeData] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [application, setApplication] = useState(null);
  const [activeJob, setActiveJob] = useState(null);
  const [jobQuery, setJobQuery] = useState("");

  const [uploadStatus, setUploadStatus] = useState("");
  const [matchStatus, setMatchStatus] = useState("");
  const [applyStatus, setApplyStatus] = useState("");

  const [uploading, setUploading] = useState(false);
  const [matching, setMatching] = useState(false);
  const [applying, setApplying] = useState(false);

  const canMatch = Boolean(resumeData) && !matching;

  const sortedJobs = useMemo(
    () => [...jobs].sort((a, b) => Number(b.score || 0) - Number(a.score || 0)),
    [jobs]
  );

  async function handleUpload() {
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

    try {
      const formData = new FormData();
      formData.append("file", resumeFile);

      const response = await fetch(`${API_BASE}/resume/upload`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error(`Resume upload failed (${response.status})`);

      const data = await response.json();
      setResumeData(data);
      setUploadStatus("Resume parsed successfully.");
    } catch (error) {
      setUploadStatus(error.message || "Could not parse resume.");
      setResumeData(null);
    } finally {
      setUploading(false);
    }
  }

  async function handleMatch() {
    if (!resumeData) return;

    setMatching(true);
    setMatchStatus("Finding top matching roles...");
    setApplication(null);
    setApplyStatus("");

    try {
      const response = await fetch(`${API_BASE}/jobs/match`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...resumeData,
          query: jobQuery?.trim() || undefined,
        }),
      });
      if (!response.ok) throw new Error(`Job matching failed (${response.status})`);

      const data = await response.json();
      const matches = data.matches || [];
      setJobs(matches);
      setMatchStatus(matches.length ? "Top matches are ready." : "No matches returned.");
    } catch (error) {
      setMatchStatus(error.message || "Could not fetch job matches.");
      setJobs([]);
    } finally {
      setMatching(false);
    }
  }

  async function handleApply(job) {
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
      if (!response.ok) throw new Error(`Application generation failed (${response.status})`);

      const data = await response.json();
      setApplication(data);
      setApplyStatus("Application generated successfully.");
    } catch (error) {
      setApplyStatus(error.message || "Could not generate application.");
      setApplication(null);
    } finally {
      setApplying(false);
    }
  }

  return (
    <div className="relative min-h-screen overflow-x-hidden">
      <div className="pointer-events-none fixed -left-24 -top-24 h-80 w-80 rounded-full bg-violet-600/40 blur-3xl animate-floaty" />
      <div className="pointer-events-none fixed -bottom-24 -right-24 h-80 w-80 rounded-full bg-cyan-500/40 blur-3xl animate-floaty [animation-delay:-4s]" />
      <div className="pointer-events-none fixed inset-0 bg-[linear-gradient(rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[size:42px_42px] [mask-image:radial-gradient(circle_at_center,black_36%,transparent_90%)]" />

      <main className="relative z-10 mx-auto w-[min(1080px,92vw)] py-10">
        <motion.header
          variants={fadeInUp}
          initial="hidden"
          animate="show"
          transition={{ duration: 0.55 }}
          className="mb-8 text-center"
        >
          <span className="inline-flex rounded-full border border-white/20 bg-violet-500/20 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-violet-200">
            AI Powered
          </span>
          <h1 className="mt-4 text-4xl font-extrabold md:text-5xl">Job Hunt Copilot</h1>
          <p className="mx-auto mt-3 max-w-2xl text-sm text-slate-300 md:text-base">
            Understand your resume, match real roles, and generate personalized applications with one smooth flow.
          </p>
        </motion.header>

        <section className="grid gap-4">
          <Card title="1) Upload Resume">
            <div className="flex flex-wrap items-center gap-3">
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                className="max-w-full rounded-lg border border-white/15 bg-slate-950/70 px-3 py-2 text-sm text-slate-300 file:mr-3 file:rounded-md file:border-0 file:bg-violet-500 file:px-3 file:py-1.5 file:text-white"
              />
              <ActionButton onClick={handleUpload} disabled={uploading}>
                {uploading ? "Analyzing..." : "Analyze Resume"}
              </ActionButton>
            </div>
            <Status>{uploadStatus}</Status>
          </Card>

          <Card title="2) Match Jobs">
            <div className="flex flex-wrap items-center gap-3">
              <input
                value={jobQuery}
                onChange={(e) => setJobQuery(e.target.value)}
                placeholder="Job title / keyword (optional). Leave blank to auto-detect from resume."
                className="min-w-[260px] flex-1 rounded-lg border border-white/15 bg-slate-950/70 px-3 py-2 text-sm text-slate-200 placeholder:text-slate-500"
              />
            </div>
            <ActionButton onClick={handleMatch} disabled={!canMatch}>
              {matching ? "Finding..." : "Find Top Matches"}
            </ActionButton>
            <Status>{matchStatus}</Status>
            <div className="mt-3 grid gap-3">
              {sortedJobs.map((job, idx) => (
                <motion.article
                  key={`${job.title}-${idx}`}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.22, delay: idx * 0.05 }}
                  className="rounded-2xl border border-white/15 bg-slate-950/60 p-4"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h3 className="text-lg font-semibold">{job.title || "Untitled Role"}</h3>
                    <span className="rounded-full border border-emerald-400/35 bg-emerald-500/10 px-2 py-1 text-xs font-bold text-emerald-300">
                      {Number(job.score || 0)}% Match
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-slate-300">
                    {job.company || "Unknown Company"} - {job.location || "N/A"}
                  </p>
                  <p className="mt-2 text-sm text-slate-200">{job.reason || "No reason provided."}</p>
                  <p className="mt-2 text-sm text-slate-400">
                    <span className="font-semibold text-slate-300">Missing skills:</span>{" "}
                    {Array.isArray(job.missing_skills) && job.missing_skills.length
                      ? job.missing_skills.join(", ")
                      : "None"}
                  </p>
                  <p className="mt-2 text-sm text-slate-400">
                    <span className="font-semibold text-slate-300">Suggestion:</span>{" "}
                    {job.suggestion || "No suggestion available."}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <ActionButton onClick={() => handleApply(job)} disabled={applying}>
                      {applying && activeJob?.title === job.title ? "Generating..." : "Generate Application"}
                    </ActionButton>
                    <a
                      href={job.url || "#"}
                      target="_blank"
                      rel="noreferrer"
                      className="rounded-xl border border-white/20 bg-transparent px-4 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/5"
                    >
                      Open Job
                    </a>
                  </div>
                </motion.article>
              ))}
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

function ActionButton({ children, ...props }) {
  return (
    <button
      {...props}
      className="rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 px-4 py-2 text-sm font-bold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {children}
    </button>
  );
}

function Status({ children }) {
  return <p className="mt-2 min-h-5 text-sm text-slate-400">{children}</p>;
}
