"use client";

import { useCallback, useEffect, useState } from "react";

type Claim = {
  id: string;
  claim_type: string;
  canonical_statement: string;
  verification_status: string;
};

type ResumeVersion = {
  id: string;
  name: string;
  content_model: { sections: { heading: string; items: { claim_id: string }[] }[] };
};

const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function ResumeEditor({ token }: { token: string }) {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [versions, setVersions] = useState<ResumeVersion[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [name, setName] = useState("Master resume");
  const [message, setMessage] = useState(
    "Load approved claims to build your structured master resume.",
  );
  const load = useCallback(async () => {
    const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
    try {
      const [claimsResponse, resumesResponse] = await Promise.all([
        fetch(`${base}/api/v1/candidate-claims`, { headers }),
        fetch(`${base}/api/v1/resume-versions`, { headers }),
      ]);
      if (!claimsResponse.ok || !resumesResponse.ok) {
        setMessage("Resume data could not be loaded. Please try again.");
        return;
      }
      const loadedClaims = (await claimsResponse.json()) as Claim[];
      setClaims(loadedClaims.filter((claim) => claim.verification_status === "APPROVED"));
      setVersions((await resumesResponse.json()) as ResumeVersion[]);
      setMessage("Choose approved claims. Their order becomes the resume section order.");
    } catch {
      setMessage("Resume data could not be loaded. Please try again.");
    }
  }, [token]);

  useEffect(() => {
    void load();
  }, [load]);

  async function save() {
    if (!selected.length) {
      setMessage("Select at least one approved claim before saving a resume version.");
      return;
    }
    const response = await fetch(`${base}/api/v1/resume-versions`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        content_model: {
          sections: [
            { heading: "Selected evidence", items: selected.map((claim_id) => ({ claim_id })) },
          ],
        },
      }),
    });
    if (!response.ok) {
      setMessage("Resume version could not be saved. Only approved claims may be included.");
      return;
    }
    const saved = (await response.json()) as ResumeVersion;
    setVersions([saved, ...versions]);
    setMessage(
      "Immutable resume version saved. Future tailored resumes can only select from this evidence.",
    );
  }

  return (
    <section aria-labelledby="resume-editor">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Candidate profile</p>
          <h1 id="resume-editor">Master resume</h1>
        </div>
        <button className="secondary" onClick={() => void load()}>
          Refresh evidence
        </button>
      </div>
      <p>
        This resume is an ordered content model, not free-form text. Every item must be an approved
        claim.
      </p>
      <p role="status">{message}</p>
      <label>
        Resume version name
        <input value={name} onChange={(event) => setName(event.target.value)} />
      </label>
      <section aria-labelledby="approved-resume-claims">
        <h2 id="approved-resume-claims">Approved claims ({claims.length})</h2>
        {!claims.length ? (
          <p>Approve claims from Claim Review before adding them to your master resume.</p>
        ) : (
          <ul className="claim-list">
            {claims.map((claim) => (
              <li key={claim.id}>
                <label>
                  <input
                    type="checkbox"
                    checked={selected.includes(claim.id)}
                    onChange={() =>
                      setSelected(
                        selected.includes(claim.id)
                          ? selected.filter((id) => id !== claim.id)
                          : [...selected, claim.id],
                      )
                    }
                  />{" "}
                  <strong>{claim.claim_type}</strong> — {claim.canonical_statement}
                </label>
              </li>
            ))}
          </ul>
        )}
      </section>
      <button disabled={!selected.length} onClick={() => void save()}>
        Save immutable resume version
      </button>
      <section aria-labelledby="saved-resume-versions">
        <h2 id="saved-resume-versions">Saved versions ({versions.length})</h2>
        <ul className="claim-list">
          {versions.map((version) => (
            <li key={version.id}>
              {version.name} ·{" "}
              {version.content_model.sections.flatMap((section) => section.items).length} approved
              claims
            </li>
          ))}
        </ul>
      </section>
    </section>
  );
}
