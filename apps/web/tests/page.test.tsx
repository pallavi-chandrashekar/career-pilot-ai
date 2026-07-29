import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HomePage from "../app/page";
import { JobInbox } from "../app/job-inbox";
import { ResumeEditor } from "../app/resume-editor";
import { SearchProfileEditor } from "../app/search-profile-editor";

describe("HomePage", () => {
  it("starts with secure account onboarding", () => {
    render(<HomePage />);
    expect(
      screen.getByRole("heading", { name: /verified job-search workspace/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign in" })).toBeInTheDocument();
  });

  it("offers account registration", () => {
    render(<HomePage />);
    fireEvent.click(screen.getAllByRole("button", { name: "Create an account" }).at(-1)!);
    expect(screen.getAllByRole("heading", { name: "Create account" }).at(-1)).toBeInTheDocument();
    expect(screen.getAllByLabelText("Display name").at(-1)).toBeInTheDocument();
  });

  it("provides guided search profile fields while keeping advanced YAML optional", () => {
    render(<SearchProfileEditor token="test-token" />);
    expect(screen.getByRole("heading", { name: "What are you looking for?" })).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Target role"), {
      target: { value: "Platform Engineer" },
    });
    expect(screen.getByLabelText("Target role")).toHaveValue("Platform Engineer");
    expect(screen.getByText("Advanced YAML configuration")).toBeInTheDocument();
  });

  it("lets the user add a job without submitting it externally", () => {
    render(<JobInbox token="test-token" />);
    expect(screen.getByRole("heading", { name: "Add a job" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Import from URL" })).toBeInTheDocument();
    expect(screen.getByText(/Nothing is submitted to an employer/i)).toBeInTheDocument();
    expect(screen.queryByText("Profile-based score preview")).not.toBeInTheDocument();
  });

  it("describes the master resume as evidence-backed structured content", () => {
    render(<ResumeEditor token="test-token" />);
    expect(screen.getByRole("heading", { name: "Master resume" })).toBeInTheDocument();
    expect(screen.getByText(/not free-form text/i)).toBeInTheDocument();
  });
});
