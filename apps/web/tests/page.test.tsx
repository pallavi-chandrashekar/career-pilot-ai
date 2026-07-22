import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HomePage from "../app/page";

describe("HomePage", () => {
  it("shows the project and safety purpose", () => {
    render(<HomePage />);
    expect(screen.getByRole("heading", { name: "CareerPilot AI" })).toBeInTheDocument();
    expect(screen.getByText(/Human approval/i)).toBeInTheDocument();
  });
});
