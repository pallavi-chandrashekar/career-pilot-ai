"use client";
import { useState } from "react";
const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
export function EvidenceOnboarding({ token, done }: { token: string; done: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState(
    "Upload a PDF or DOCX to build your verified evidence profile.",
  );
  async function upload() {
    if (!file) return;
    const data = new FormData();
    data.append("file", file);
    const headers = { Authorization: `Bearer ${token}` };
    const created = await fetch(`${base}/api/v1/documents`, {
      method: "POST",
      headers,
      body: data,
    });
    if (!created.ok) {
      setMessage("Upload failed. Use a PDF or DOCX under 10 MiB.");
      return;
    }
    const document = (await created.json()) as { id: string };
    setMessage("Parsing your document…");
    const parsed = await fetch(`${base}/api/v1/documents/${document.id}/parse`, {
      method: "POST",
      headers,
    });
    if (!parsed.ok) {
      setMessage("Parsing failed. You can try another document.");
      return;
    }
    setMessage("Extracting evidence-grounded draft claims…");
    const extracted = await fetch(`${base}/api/v1/documents/${document.id}/extract-claims`, {
      method: "POST",
      headers: { ...headers, "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    if (!extracted.ok) {
      setMessage("Claims could not be extracted. You can still upload another document.");
      return;
    }
    setMessage("Claims are ready for your review.");
    done();
  }
  return (
    <section aria-labelledby="evidence-onboarding">
      <p className="eyebrow">Step 1 of 3</p>
      <h1 id="evidence-onboarding">Build your verified profile</h1>
      <p>
        We only create draft claims backed by the exact lines in your document. You decide what
        becomes approved evidence.
      </p>
      <label className="auth-form">
        Resume or profile document
        <input
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />
      </label>
      <button disabled={!file} onClick={upload}>
        Upload and extract claims
      </button>
      <p role="status">{message}</p>
    </section>
  );
}
