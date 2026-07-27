"use client";

import { ChangeEvent, useState } from "react";
import { parse, stringify } from "yaml";

type Profile = {
  id: string;
  name: string;
  description: string;
  is_default: boolean;
  is_active: boolean;
  configuration_version: number;
  configuration: Record<string, unknown>;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const initialConfiguration = {
  name: "New search profile",
  description: "",
  active: false,
  target_roles: [],
  excluded_titles: [],
  locations: { preferred: [], acceptable: [], excluded: [] },
  work_authorization: {},
  compensation: {},
  employment_types: {},
  skills: { required: [], preferred: [], learning_interests: [], excluded: [] },
  companies: {},
  weights: {
    core_technical_skills: 20,
    distributed_systems: 15,
    ai_alignment: 15,
    domain_alignment: 10,
    seniority: 10,
    leadership: 10,
    location: 8,
    sponsorship: 7,
    compensation: 3,
    company_preference: 2,
  },
  thresholds: { apply_now: 80, apply_selectively: 68, manual_review: 55, skip_below: 55 },
  notifications: { minimum_score: 75, immediate_for_apply_now: false, daily_digest: true },
};

export function SearchProfileEditor({ token }: { token: string }) {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [selected, setSelected] = useState<Profile | null>(null);
  const [yaml, setYaml] = useState(stringify(initialConfiguration));
  const [message, setMessage] = useState("Load profiles or configure a new profile.");

  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  function setProfile(profile: Profile) {
    setSelected(profile);
    setYaml(stringify(profile.configuration));
  }

  async function loadProfiles() {
    const response = await fetch(`${apiBaseUrl}/api/v1/search-profiles`, { headers });
    if (!response.ok) {
      setMessage("Profiles could not be loaded. Check the bearer token and try again.");
      return;
    }
    const loaded = (await response.json()) as Profile[];
    setProfiles(loaded);
    setMessage("Profiles loaded. Configuration history is preserved on every save.");
  }

  function configuration(): Record<string, unknown> | null {
    try {
      const parsed = parse(yaml);
      if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") throw new Error();
      return parsed as Record<string, unknown>;
    } catch {
      setMessage("YAML could not be read. Correct the configuration and try again.");
      return null;
    }
  }

  async function validate() {
    const value = configuration();
    if (!value) return;
    if (!selected) {
      setMessage("Save the new profile before using server-side validation.");
      return;
    }
    const response = await fetch(`${apiBaseUrl}/api/v1/search-profiles/${selected.id}/validate`, {
      method: "POST",
      headers,
      body: JSON.stringify({ configuration: value }),
    });
    if (!response.ok) {
      setMessage("Validation could not be completed.");
      return;
    }
    const result = (await response.json()) as { valid: boolean; errors: string[] };
    setMessage(result.valid ? "Configuration is valid." : result.errors.join(" "));
  }

  async function save() {
    const value = configuration();
    if (!value) return;
    const endpoint = selected
      ? `${apiBaseUrl}/api/v1/search-profiles/${selected.id}`
      : `${apiBaseUrl}/api/v1/search-profiles`;
    const response = await fetch(endpoint, {
      method: selected ? "PUT" : "POST",
      headers,
      body: JSON.stringify(value),
    });
    if (!response.ok) {
      setMessage("Profile could not be saved. Review the configuration validation rules.");
      return;
    }
    const saved = (await response.json()) as Profile;
    setProfile(saved);
    setMessage(`Profile saved as version ${saved.configuration_version}.`);
    await loadProfiles();
  }

  async function duplicate() {
    if (!selected) return;
    const response = await fetch(`${apiBaseUrl}/api/v1/search-profiles/${selected.id}/duplicate`, {
      method: "POST",
      headers,
      body: JSON.stringify({}),
    });
    if (!response.ok) {
      setMessage("Profile could not be duplicated.");
      return;
    }
    const copied = (await response.json()) as Profile;
    setProfile(copied);
    setMessage("Inactive profile copy created.");
    await loadProfiles();
  }

  async function setState(isActive: boolean, isDefault: boolean) {
    if (!selected) return;
    const response = await fetch(`${apiBaseUrl}/api/v1/search-profiles/${selected.id}/state`, {
      method: "POST",
      headers,
      body: JSON.stringify({ is_active: isActive, is_default: isDefault }),
    });
    if (!response.ok) {
      setMessage("Profile state could not be updated.");
      return;
    }
    setProfile((await response.json()) as Profile);
    setMessage(isDefault ? "Profile activated as the default." : "Profile state updated.");
    await loadProfiles();
  }

  async function importYaml(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setYaml(await file.text());
    setSelected(null);
    setMessage("YAML imported as a new, unsaved profile.");
  }

  function exportYaml() {
    const blob = new Blob([yaml], { type: "application/yaml" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "careerpilot-search-profile.yaml";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section aria-labelledby="search-profiles">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Job discovery</p>
          <h1 id="search-profiles">Search profiles</h1>
        </div>
        <button onClick={loadProfiles}>Load profiles</button>
      </div>
      <p>Save versions, validate constraints, and explicitly control active/default state.</p>
      <p role="status">{message}</p>
      <div className="profile-layout">
        <aside aria-label="Saved search profiles">
          <button
            onClick={() => {
              setSelected(null);
              setYaml(stringify(initialConfiguration));
            }}
          >
            New profile
          </button>
          {profiles.map((profile) => (
            <button className="profile-card" key={profile.id} onClick={() => setProfile(profile)}>
              {profile.name} · v{profile.configuration_version}
              {profile.is_default ? " · Default" : ""}
              {profile.is_active ? " · Active" : " · Inactive"}
            </button>
          ))}
        </aside>
        <div>
          <h2>Configuration editor</h2>
          <p className="section-help">
            YAML sections: roles, locations, work authorization, compensation, skills, companies,
            weights, thresholds, and notifications.
          </p>
          <label className="yaml-editor" htmlFor="profile-yaml">
            Search profile YAML
            <textarea
              id="profile-yaml"
              value={yaml}
              onChange={(event) => setYaml(event.target.value)}
            />
          </label>
          <div className="claim-actions">
            <button onClick={save}>{selected ? "Save new version" : "Create profile"}</button>
            <button className="secondary" onClick={validate} disabled={!selected}>
              Validate
            </button>
            <button className="secondary" onClick={duplicate} disabled={!selected}>
              Duplicate
            </button>
            <button className="secondary" onClick={exportYaml}>
              Export YAML
            </button>
            <label className="file-button">
              Import YAML
              <input type="file" accept=".yaml,.yml,application/yaml" onChange={importYaml} />
            </label>
            <button disabled title="Job scoring is introduced in Task 014.">
              Preview score (coming soon)
            </button>
          </div>
          {selected && (
            <div className="claim-actions state-actions">
              <button onClick={() => setState(!selected.is_active, false)}>
                {selected.is_active ? "Deactivate" : "Activate"}
              </button>
              <button
                className="secondary"
                disabled={!selected.is_active || selected.is_default}
                onClick={() => setState(true, true)}
              >
                Set default
              </button>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
