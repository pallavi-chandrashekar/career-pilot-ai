"use client";

import { FormEvent, useMemo, useState } from "react";

type Job = {
  id: string;
  company: string;
  title: string;
  description: string;
  location: string | null;
  canonical_url: string | null;
  sponsorship: string | null;
  clearance: string | null;
  normalized_requirements: Record<string, unknown> | null;
  hard_filter_results: Record<string, unknown> | null;
};

type JobDraft = {
  company: string;
  title: string;
  description: string;
  location: string;
  source_url: string;
};

const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const emptyDraft: JobDraft = {
  company: "",
  title: "",
  description: "",
  location: "",
  source_url: "",
};

export function JobInbox({ token }: { token: string }) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [draft, setDraft] = useState<JobDraft>(emptyDraft);
  const [importUrl, setImportUrl] = useState("");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Job | null>(null);
  const [message, setMessage] = useState("Add a job or load your existing inbox.");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
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

  function updateDraft(field: keyof JobDraft, value: string) {
    setDraft({ ...draft, [field]: value });
  }

  async function load() {
    const response = await fetch(`${base}/api/v1/jobs`, { headers });
    if (!response.ok) {
      setMessage("Jobs could not be loaded. Please try again.");
      return;
    }
    const loaded = (await response.json()) as Job[];
    setJobs(loaded);
    setMessage(loaded.length ? "Jobs loaded." : "Your inbox is ready for its first job.");
  }

  async function createJob(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const response = await fetch(`${base}/api/v1/jobs`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        company: draft.company,
        title: draft.title,
        description: draft.description,
        location: draft.location || null,
        source_url: draft.source_url || null,
      }),
    });
    if (!response.ok) {
      setMessage("The job could not be saved. Check the required fields and try again.");
      return;
    }
    const saved = (await response.json()) as Job;
    setJobs([saved, ...jobs.filter((job) => job.id !== saved.id)]);
    setSelected(saved);
    setDraft(emptyDraft);
    setMessage("Job saved. Normalize it to extract requirements, then evaluate hard filters.");
  }

  async function importFromUrl(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const response = await fetch(`${base}/api/v1/jobs/import-url`, {
      method: "POST",
      headers,
      body: JSON.stringify({ url: importUrl }),
    });
    if (!response.ok) {
      setMessage("That URL could not be imported. Paste the job description instead.");
      return;
    }
    const imported = (await response.json()) as {
      status: string;
      extracted_text?: string;
      page_title?: string;
      paste_fallback_message?: string;
    };
    if (imported.status !== "EXTRACTED" || !imported.extracted_text) {
      setMessage(imported.paste_fallback_message ?? "Paste the job description to continue.");
      return;
    }
    setDraft({
      ...draft,
      description: imported.extracted_text,
      source_url: importUrl,
      title: draft.title || imported.page_title || "",
    });
    setMessage("Description imported. Confirm the company and job title, then save the job.");
  }

  async function updateJob(action: "normalize" | "evaluate") {
    if (!selected) return;
    const response = await fetch(`${base}/api/v1/jobs/${selected.id}/${action}`, {
      method: "POST",
      headers,
    });
    if (!response.ok) {
      setMessage(`${action === "normalize" ? "Normalization" : "Hard-filter evaluation"} failed.`);
      return;
    }
    const updated = (await response.json()) as Job;
    setSelected(updated);
    setJobs(jobs.map((job) => (job.id === updated.id ? updated : job)));
    setMessage(
      action === "normalize"
        ? "Requirements extracted. You can now run deterministic hard filters."
        : "Hard filters evaluated. Review the result below.",
    );
  }

  return (
    <section aria-labelledby="job-inbox">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Job discovery</p>
          <h1 id="job-inbox">Job inbox</h1>
        </div>
        <button onClick={() => void load()}>Load jobs</button>
      </div>
      <p>Save a job manually or import its public URL. Nothing is submitted to an employer.</p>
      <p role="status">{message}</p>
      <div className="profile-layout job-entry-layout">
        <form className="auth-form" onSubmit={createJob}>
          <h2>Add a job</h2>
          <label>
            Company
            <input
              value={draft.company}
              onChange={(event) => updateDraft("company", event.target.value)}
              required
            />
          </label>
          <label>
            Job title
            <input
              value={draft.title}
              onChange={(event) => updateDraft("title", event.target.value)}
              required
            />
          </label>
          <label>
            Location{" "}
            <input
              value={draft.location}
              onChange={(event) => updateDraft("location", event.target.value)}
            />
          </label>
          <label>
            Job description
            <textarea
              value={draft.description}
              onChange={(event) => updateDraft("description", event.target.value)}
              required
            />
          </label>
          <label>
            Source URL (optional)
            <input
              type="url"
              value={draft.source_url}
              onChange={(event) => updateDraft("source_url", event.target.value)}
            />
          </label>
          <button type="submit">Save job</button>
        </form>
        <form className="auth-form" onSubmit={importFromUrl}>
          <h2>Import from URL</h2>
          <p className="section-help">
            We only retrieve public pages. If a site blocks access, paste the description instead.
          </p>
          <label>
            Public job URL
            <input
              type="url"
              value={importUrl}
              onChange={(event) => setImportUrl(event.target.value)}
              required
            />
          </label>
          <button className="secondary" type="submit">
            Import description
          </button>
        </form>
      </div>
      <label>
        Filter jobs{" "}
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Company, title, or location"
        />
      </label>
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
              <div className="claim-actions">
                <button onClick={() => void updateJob("normalize")}>Extract requirements</button>
                <button className="secondary" onClick={() => void updateJob("evaluate")}>
                  Evaluate hard filters
                </button>
              </div>
              <h3>Extracted requirements</h3>
              <pre className="evidence-text">
                {JSON.stringify(selected.normalized_requirements ?? "Not extracted", null, 2)}
              </pre>
              <h3>Hard-filter analysis</h3>
              <pre className="evidence-text">
                {JSON.stringify(selected.hard_filter_results ?? "Not evaluated", null, 2)}
              </pre>
            </>
          ) : (
            <p>Select a job to extract requirements and view its deterministic filter summary.</p>
          )}
        </div>
      </div>
    </section>
  );
}
