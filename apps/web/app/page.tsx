"use client";

import { FormEvent, useState } from "react";
import { SearchProfileEditor } from "./search-profile-editor";
import { JobInbox } from "./job-inbox";
import { EvidenceOnboarding } from "./evidence-onboarding";
import { ResumeEditor } from "./resume-editor";

type Claim = {
  id: string;
  claim_type: string;
  canonical_statement: string;
  source_locator: { start_line: number; end_line: number };
  verification_status: "DRAFT" | "APPROVED" | "REJECTED" | "ARCHIVED";
};

type ClaimEvidence = {
  start_line: number;
  end_line: number;
  text: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function HomePage() {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);
  const [workspace, setWorkspace] = useState<
    "evidence" | "claims" | "resume" | "profiles" | "jobs"
  >("evidence");
  const [claims, setClaims] = useState<Claim[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [edits, setEdits] = useState<Record<string, string>>({});
  const [evidence, setEvidence] = useState<Record<string, ClaimEvidence>>({});
  const [message, setMessage] = useState("Upload a resume to get started.");

  async function authenticate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const endpoint = isRegistering ? "register" : "login";
    const payload = isRegistering
      ? {
          email,
          password,
          display_name: displayName,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        }
      : { email, password };
    const response = await fetch(`${apiBaseUrl}/api/v1/auth/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      setMessage("Authentication failed. Check your details and try again.");
      return;
    }
    setToken(((await response.json()) as { access_token: string }).access_token);
    setMessage("Signed in. Your session stays in this browser tab only.");
  }

  async function loadClaims() {
    const response = await fetch(`${apiBaseUrl}/api/v1/candidate-claims`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      setMessage("Claims could not be loaded. Upload and extract evidence, then try again.");
      return;
    }
    const loaded = (await response.json()) as Claim[];
    setClaims(loaded);
    setSelected([]);
    setEvidence({});
    setMessage(
      loaded.length ? "Draft claims are ready for review." : "No draft claims were found yet.",
    );
  }

  async function approve(claimIds: string[]) {
    const response = await fetch(`${apiBaseUrl}/api/v1/candidate-claims/bulk-approve`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ claim_ids: claimIds }),
    });
    if (!response.ok) {
      setMessage("Approval could not be completed. Only draft claims can be approved.");
      return;
    }
    setClaims(
      claims.map((claim) =>
        claimIds.includes(claim.id) ? { ...claim, verification_status: "APPROVED" } : claim,
      ),
    );
    setSelected([]);
    setMessage("Selected claims were approved.");
  }

  async function reject(claimId: string) {
    const response = await fetch(`${apiBaseUrl}/api/v1/candidate-claims/${claimId}/reject`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      setMessage("Rejection could not be completed. Only draft claims can be rejected.");
      return;
    }
    setClaims(
      claims.map((claim) =>
        claim.id === claimId ? { ...claim, verification_status: "REJECTED" } : claim,
      ),
    );
    setSelected(selected.filter((id) => id !== claimId));
    setMessage("Claim rejected.");
  }

  async function saveEdit(claim: Claim) {
    const canonicalStatement = edits[claim.id] ?? claim.canonical_statement;
    const response = await fetch(`${apiBaseUrl}/api/v1/candidate-claims/${claim.id}`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ canonical_statement: canonicalStatement }),
    });
    if (!response.ok) {
      setMessage("Edit could not be saved. The statement must remain supported by its evidence.");
      return;
    }
    const saved = (await response.json()) as Claim;
    setClaims(claims.map((current) => (current.id === claim.id ? saved : current)));
    setEdits({ ...edits, [claim.id]: saved.canonical_statement });
    setMessage("Draft claim updated.");
  }

  async function viewEvidence(claimId: string) {
    const response = await fetch(`${apiBaseUrl}/api/v1/candidate-claims/${claimId}/evidence`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      setMessage("Evidence could not be loaded.");
      return;
    }
    const loaded = (await response.json()) as ClaimEvidence;
    setEvidence({ ...evidence, [claimId]: loaded });
  }

  const drafts = claims.filter((claim) => claim.verification_status === "DRAFT");
  if (!token)
    return (
      <main className="onboarding">
        <p className="eyebrow">CareerPilot AI</p>
        <h1>Set up your job search</h1>
        <p>
          Create an account to save your resume, job preferences, and opportunities in one place.
        </p>
        <form onSubmit={authenticate} className="auth-form">
          <h2>{isRegistering ? "Create account" : "Welcome back"}</h2>
          {isRegistering && (
            <label>
              Display name
              <input
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
                required
              />
            </label>
          )}
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              minLength={12}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          <button type="submit">{isRegistering ? "Create secure account" : "Sign in"}</button>
          <button
            type="button"
            className="secondary"
            onClick={() => setIsRegistering(!isRegistering)}
          >
            {isRegistering ? "I already have an account" : "Create an account"}
          </button>
        </form>
        <p role="status">{message}</p>
      </main>
    );
  return (
    <main>
      <nav aria-label="Workspace" className="workspace-nav">
        <button
          className={workspace === "evidence" ? "selected" : "secondary"}
          onClick={() => setWorkspace("evidence")}
        >
          My evidence
        </button>
        <button
          className={workspace === "claims" ? "selected" : "secondary"}
          onClick={() => setWorkspace("claims")}
        >
          Claim review
        </button>
        <button
          className={workspace === "resume" ? "selected" : "secondary"}
          onClick={() => setWorkspace("resume")}
        >
          Master resume
        </button>
        <button
          className={workspace === "profiles" ? "selected" : "secondary"}
          onClick={() => setWorkspace("profiles")}
        >
          Search profiles
        </button>
        <button
          className={workspace === "jobs" ? "selected" : "secondary"}
          onClick={() => setWorkspace("jobs")}
        >
          Job inbox
        </button>
      </nav>
      <div className="session-bar">
        <span>Signed in</span>
        <button className="secondary" onClick={() => setToken("")}>
          Sign out
        </button>
      </div>
      {workspace === "evidence" ? (
        <EvidenceOnboarding
          token={token}
          done={() => {
            setWorkspace("claims");
            void loadClaims();
          }}
        />
      ) : workspace === "profiles" ? (
        <SearchProfileEditor token={token} />
      ) : workspace === "resume" ? (
        <ResumeEditor token={token} />
      ) : workspace === "jobs" ? (
        <JobInbox token={token} />
      ) : (
        <>
          <p className="eyebrow">Candidate profile</p>
          <h1>Claim review</h1>
          <p>
            Review the statements we found in your document. Approve only the details that are
            accurate.
          </p>
          <p role="status">{message}</p>
          <section aria-labelledby="draft-claims">
            <div className="section-heading">
              <h2 id="draft-claims">Draft claims ({drafts.length})</h2>
              <div className="claim-actions">
                <button className="secondary" onClick={() => void loadClaims()}>
                  Refresh claims
                </button>
                <button disabled={!selected.length} onClick={() => approve(selected)}>
                  Approve selected
                </button>
              </div>
            </div>
            {!claims.length ? (
              <p>No claims loaded.</p>
            ) : (
              <ul className="claim-list">
                {claims.map((claim) => (
                  <li key={claim.id}>
                    <label>
                      <input
                        type="checkbox"
                        disabled={claim.verification_status !== "DRAFT"}
                        checked={selected.includes(claim.id)}
                        onChange={() =>
                          setSelected(
                            selected.includes(claim.id)
                              ? selected.filter((id) => id !== claim.id)
                              : [...selected, claim.id],
                          )
                        }
                      />{" "}
                      <strong>{claim.claim_type}</strong>
                    </label>
                    {claim.verification_status === "DRAFT" ? (
                      <label className="edit-field">
                        Claim statement
                        <input
                          aria-label={`Edit claim ${claim.id}`}
                          value={edits[claim.id] ?? claim.canonical_statement}
                          onChange={(event) =>
                            setEdits({ ...edits, [claim.id]: event.target.value })
                          }
                        />
                      </label>
                    ) : (
                      <p>{claim.canonical_statement}</p>
                    )}
                    <p className="evidence">
                      Evidence: document lines {claim.source_locator.start_line}–
                      {claim.source_locator.end_line}
                    </p>
                    <button className="secondary" onClick={() => viewEvidence(claim.id)}>
                      View evidence
                    </button>
                    {evidence[claim.id] && (
                      <pre className="evidence-text">{evidence[claim.id].text}</pre>
                    )}
                    <p>Status: {claim.verification_status}</p>
                    {claim.verification_status === "DRAFT" && (
                      <div className="claim-actions">
                        <button onClick={() => saveEdit(claim)}>Save edit</button>
                        <button onClick={() => approve([claim.id])}>Approve</button>
                        <button className="secondary" onClick={() => reject(claim.id)}>
                          Reject
                        </button>
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </section>
          <section aria-labelledby="conflicts">
            <h2 id="conflicts">Conflicts</h2>
            <p>No conflicts detected. Conflict analysis will appear here when available.</p>
          </section>
        </>
      )}
    </main>
  );
}
