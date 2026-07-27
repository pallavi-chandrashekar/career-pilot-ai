import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HomePage from "../app/page";

describe("HomePage", () => {
  it("shows claim review safety controls", () => {
    render(<HomePage />);
    expect(screen.getByRole("heading", { name: "Claim review" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Draft claims/i })).toBeInTheDocument();
    expect(screen.getByText(/evidence-grounded draft claims/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Approve selected" })).toBeDisabled();
  });
});
