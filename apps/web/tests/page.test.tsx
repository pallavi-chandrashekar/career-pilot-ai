import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HomePage from "../app/page";

describe("HomePage", () => {
  it("shows claim review safety controls", () => {
    render(<HomePage />);
    expect(screen.getByRole("heading", { name: "Claim review" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Draft claims/i })).toBeInTheDocument();
    expect(screen.getByText(/evidence-grounded draft claims/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Approve selected" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Search profiles" })).toBeInTheDocument();
  });

  it("opens the search profile editor without removing claim review", () => {
    const view = render(<HomePage />);
    const page = within(view.container);
    fireEvent.click(page.getByRole("button", { name: "Search profiles" }));
    expect(page.getByRole("heading", { name: "Search profiles" })).toBeInTheDocument();
    expect(page.getByLabelText("Search profile YAML")).toBeInTheDocument();
    expect(page.getByRole("button", { name: /Preview score/ })).toBeDisabled();
  });
});
