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

type SearchProfile = {
  id: string;
  name: string;
  is_active: boolean;
  configuration: {
    weights: Record<string, number>;
    thresholds: Record<string, number>;
  };
};

type ScorePreview = {
  total: number;
  confidence: number;
  recommendation: string;
};

type ResumeVersion = { id: string; name: string };
type ApplicationDraft = {
  id: string;
  tailored_resume: string[];
  cover_letter: string;
  recruiter_message: string;
  referral_message: string;
  evidence_map: Record<string, string[]>;
};

type FactualityReport = {
  valid: boolean;
  findings: { field: string; code: string; message: string }[];
};

const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const emptyDraft: JobDraft = {
  company: "",
  title: "",
  description: "",
  location: "",
  source_url: "",
};
const initialCategoryScores: Record<string, number> = {
  core_technical_skills: 50,
  distributed_systems: 50,
  ai_alignment: 50,
  domain_alignment: 50,
  seniority: 50,
  leadership: 50,
  location: 50,
  sponsorship: 50,
  compensation: 50,
  company_preference: 50,
};

function displayCategory(name: string) {
  return name.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function JobInbox({ token }: { token: string }) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [draft, setDraft] = useState<JobDraft>(emptyDraft);
  const [importUrl, setImportUrl] = useState("");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Job | null>(null);
  const [profiles, setProfiles] = useState<SearchProfile[]>([]);
  const [profileId, setProfileId] = useState("");
  const [categoryScores, setCategoryScores] = useState(initialCategoryScores);
  const [scorePreview, setScorePreview] = useState<ScorePreview | null>(null);
  const [resumeVersions, setResumeVersions] = useState<ResumeVersion[]>([]);
  const [resumeVersionId, setResumeVersionId] = useState("");
  const [applicationDraft, setApplicationDraft] = useState<ApplicationDraft | null>(null);
  const [factualityReport, setFactualityReport] = useState<FactualityReport | null>(null);
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

  async function loadProfiles() {
    const response = await fetch(`${base}/api/v1/search-profiles?active_only=true`, { headers });
    if (!response.ok) {
      setMessage("Active search profiles could not be loaded.");
      return;
    }
    const loaded = (await response.json()) as SearchProfile[];
    setProfiles(loaded);
    setProfileId(loaded[0]?.id ?? "");
    setMessage(
      loaded.length
        ? "Choose an active profile for a transparent score preview."
        : "Create and activate a search profile before scoring.",
    );
  }

  async function loadResumeVersions() {
    const response = await fetch(`${base}/api/v1/resume-versions`, { headers });
    if (!response.ok) {
      setMessage("Resume versions could not be loaded.");
      return;
    }
    const loaded = (await response.json()) as ResumeVersion[];
    setResumeVersions(loaded);
    setResumeVersionId(loaded[0]?.id ?? "");
    setMessage(
      loaded.length
        ? "Choose a master resume to assemble an evidence-backed draft."
        : "Create a master resume before drafting application content.",
    );
  }

  async function generateApplicationDraft() {
    if (!selected || !resumeVersionId) return;
    const response = await fetch(`${base}/api/v1/jobs/${selected.id}/application-draft`, {
      method: "POST",
      headers,
      body: JSON.stringify({ resume_version_id: resumeVersionId }),
    });
    if (!response.ok) {
      setMessage(
        "Application draft could not be generated. The resume must contain approved claims.",
      );
      return;
    }
    setApplicationDraft((await response.json()) as ApplicationDraft);
    setFactualityReport(null);
    setMessage(
      "Evidence-backed application draft generated. Review it before any export or approval.",
    );
  }

  async function validateApplicationDraft() {
    if (!applicationDraft) return;
    const response = await fetch(
      `${base}/api/v1/application-packages/${applicationDraft.id}/validate`,
      {
        method: "POST",
        headers,
      },
    );
    if (!response.ok) {
      setMessage("Factuality validation could not be completed.");
      return;
    }
    const report = (await response.json()) as FactualityReport;
    setFactualityReport(report);
    setMessage(report.valid ? "Factuality validation passed." : "Factuality findings need review.");
  }

  async function previewScore() {
    const profile = profiles.find((item) => item.id === profileId);
    if (!selected || !profile) return;
    const response = await fetch(`${base}/api/v1/jobs/${selected.id}/preview-score`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        category_scores: categoryScores,
        weights: profile.configuration.weights,
        thresholds: profile.configuration.thresholds,
      }),
    });
    if (!response.ok) {
      setMessage("Score preview could not be calculated. Check the selected profile.");
      return;
    }
    setScorePreview((await response.json()) as ScorePreview);
    setMessage("Score preview calculated from your selected profile. It does not take any action.");
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
              <section aria-labelledby="application-workspace">
                <div className="section-heading">
                  <h3 id="application-workspace">Application workspace</h3>
                  <button className="secondary" onClick={() => void loadResumeVersions()}>
                    Load master resumes
                  </button>
                </div>
                <p className="section-help">
                  Drafts use only approved claims from the selected master resume. No application is
                  sent.
                </p>
                {resumeVersions.length > 0 && (
                  <>
                    <label>
                      Master resume
                      <select
                        value={resumeVersionId}
                        onChange={(event) => setResumeVersionId(event.target.value)}
                      >
                        {resumeVersions.map((resume) => (
                          <option key={resume.id} value={resume.id}>
                            {resume.name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <button onClick={() => void generateApplicationDraft()}>
                      Generate evidence-backed draft
                    </button>
                  </>
                )}
                {applicationDraft && (
                  <>
                    <h4>Tailored resume content</h4>
                    <ul>
                      {applicationDraft.tailored_resume.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                    <h4>Cover letter</h4>
                    <pre className="evidence-text">{applicationDraft.cover_letter}</pre>
                    <h4>Evidence map</h4>
                    <pre className="evidence-text">
                      {JSON.stringify(applicationDraft.evidence_map, null, 2)}
                    </pre>
                    <button onClick={() => void validateApplicationDraft()}>
                      Validate factuality
                    </button>
                    {factualityReport && (
                      <p role="status">
                        {factualityReport.valid
                          ? "All mapped claims are approved and present."
                          : factualityReport.findings
                              .map((finding) => `${finding.field}: ${finding.message}`)
                              .join(" ")}
                      </p>
                    )}
                  </>
                )}
              </section>
              <section aria-labelledby="score-preview">
                <div className="section-heading">
                  <h3 id="score-preview">Profile-based score preview</h3>
                  <button className="secondary" onClick={() => void loadProfiles()}>
                    Load active profiles
                  </button>
                </div>
                <p className="section-help">
                  Set each visible category score from 0–100, then calculate using your profile’s
                  saved weights and thresholds. This is an advisory preview only.
                </p>
                {profiles.length > 0 && (
                  <>
                    <label>
                      Active search profile
                      <select
                        value={profileId}
                        onChange={(event) => setProfileId(event.target.value)}
                      >
                        {profiles.map((profile) => (
                          <option key={profile.id} value={profile.id}>
                            {profile.name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <div className="guided-profile-form score-inputs">
                      {Object.keys(initialCategoryScores).map((category) => (
                        <label key={category}>
                          {displayCategory(category)}
                          <input
                            type="number"
                            min="0"
                            max="100"
                            value={categoryScores[category]}
                            onChange={(event) =>
                              setCategoryScores({
                                ...categoryScores,
                                [category]: Math.max(0, Math.min(100, Number(event.target.value))),
                              })
                            }
                          />
                        </label>
                      ))}
                    </div>
                    <button onClick={() => void previewScore()}>Calculate preview</button>
                  </>
                )}
                {scorePreview && (
                  <p role="status">
                    Recommendation: {scorePreview.recommendation.replaceAll("_", " ")} · Score:{" "}
                    {scorePreview.total}/100 · Confidence:{" "}
                    {Math.round(scorePreview.confidence * 100)}%
                  </p>
                )}
              </section>
            </>
          ) : (
            <p>Select a job to extract requirements and view its deterministic filter summary.</p>
          )}
        </div>
      </div>
    </section>
  );
}
