"""Shared state definition for the LangGraph review workflow."""

from __future__ import annotations

from typing import Annotated, TypedDict

from codeagent.models.findings import Finding, ReviewReport


def merge_findings(
    existing: list[Finding], new: list[Finding]
) -> list[Finding]:
    """Reducer that accumulates findings from multiple agents."""
    return existing + new


class ReviewState(TypedDict):
    """Shared state that flows through the LangGraph review pipeline.

    Each agent reads the fields it needs and returns only the fields it updates.
    LangGraph uses the annotated reducers to merge updates from parallel nodes.
    """

    # Input
    pr_url: str
    pr_title: str
    diff: str
    file_contents: dict[str, str]

    # Agent outputs — annotated with merge reducer for parallel fan-in
    logic_findings: Annotated[list[Finding], merge_findings]
    style_findings: Annotated[list[Finding], merge_findings]
    security_findings: Annotated[list[Finding], merge_findings]

    # Orchestrator output
    final_report: ReviewReport | None
