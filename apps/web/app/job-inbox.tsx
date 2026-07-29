"use client";
import { useMemo, useState } from "react";
type Job = {
  id: string;
  company: string;
  title: string;
  location: string | null;
  sponsorship: string | null;
  hard_filter_results: Record<string, unknown> | null;
};
const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
export function JobInbox({ token }: { token: string }) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Job | null>(null);
  const [message, setMessage] = useState("Load jobs to review the inbox.");
  const filtered = useMemo(
    () =>
      jobs
        .filter((job) =>
          `${job.company} ${job.title} ${job.location ?? ""}`
            .toLowerCase()
            .includes(query.toLowerCase()),
        )
        .sort((a, b) => a.company.localeCompare(b.company)),
    [jobs, query],
  );
  async function load() {
    const response = await fetch(`${base}/api/v1/jobs`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      setMessage("Jobs could not be loaded. Check the bearer token.");
      return;
    }
    setJobs(await response.json());
    setMessage("Jobs loaded.");
  }
  return (
    <section aria-labelledby="job-inbox">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Job discovery</p>
          <h1 id="job-inbox">Job inbox</h1>
        </div>
        <button onClick={load}>Load jobs</button>
      </div>
      <label>
        Filter jobs{" "}
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Company, title, or location"
        />
      </label>
      <p role="status">{message}</p>
      <div className="profile-layout">
        <ul className="claim-list">
          {filtered.map((job) => (
            <li key={job.id}>
              <button className="profile-card" onClick={() => setSelected(job)}>
                {job.company} · {job.title}
                <br />
                {job.location ?? "Location unknown"} · Sponsorship: {job.sponsorship ?? "UNKNOWN"}
              </button>
            </li>
          ))}
        </ul>
        <div>
          {selected ? (
            <>
              <h2>{selected.title}</h2>
              <p>{selected.company}</p>
              <p>Location: {selected.location ?? "Unknown"}</p>
              <h3>Match analysis</h3>
              <pre className="evidence-text">
                {JSON.stringify(selected.hard_filter_results ?? "Not evaluated", null, 2)}
              </pre>
            </>
          ) : (
            <p>Select a job to view its details and hard-filter summary.</p>
          )}
        </div>
      </div>
    </section>
  );
}
