"use client";

import { FormEvent, useState } from "react";
import { SearchProfileEditor } from "./search-profile-editor";
import { JobInbox } from "./job-inbox";

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
  const [workspace, setWorkspace] = useState<"claims" | "profiles" | "jobs">("claims");
  const [claims, setClaims] = useState<Claim[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [edits, setEdits] = useState<Record<string, string>>({});
  const [evidence, setEvidence] = useState<Record<string, ClaimEvidence>>({});
  const [message, setMessage] = useState("Enter a bearer token to review draft claims.");

  async function loadClaims(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const response = await fetch(`${apiBaseUrl}/api/v1/candidate-claims`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      setMessage("Claims could not be loaded. Check the bearer token and try again.");
      return;
    }
    setClaims(await response.json());
    setSelected([]);
    setMessage("Claims loaded. Draft claims require your explicit review.");
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
  return (
    <main>
      <nav aria-label="Workspace" className="workspace-nav">
        <button
          className={workspace === "claims" ? "selected" : "secondary"}
          onClick={() => setWorkspace("claims")}
        >
          Claim review
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
      <form onSubmit={loadClaims} className="token-form">
        <label htmlFor="token">Bearer token</label>
        <input
          id="token"
          type="password"
          value={token}
          onChange={(event) => setToken(event.target.value)}
          required
        />
        <button type="submit">Load claims</button>
      </form>
      {workspace === "profiles" ? (
        <SearchProfileEditor token={token} />
      ) : workspace === "jobs" ? (
        <JobInbox token={token} />
      ) : (
        <>
          <p className="eyebrow">Candidate profile</p>
          <h1>Claim review</h1>
          <p>
            Review evidence-grounded draft claims before they can be used in application content.
          </p>
          <p role="status">{message}</p>
          <section aria-labelledby="draft-claims">
            <div className="section-heading">
              <h2 id="draft-claims">Draft claims ({drafts.length})</h2>
              <button disabled={!selected.length} onClick={() => approve(selected)}>
                Approve selected
              </button>
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
