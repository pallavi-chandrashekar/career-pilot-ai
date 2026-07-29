import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HomePage from "../app/page";
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
});
