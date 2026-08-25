"""Orchestrator — deduplicates findings, assigns severity, and generates the final report."""

from __future__ import annotations

from codeagent.models.findings import Finding, ReviewReport, Severity


def deduplicate_findings(findings: list[Finding]) -> list[Finding]:
    """Remove duplicate findings that point to the same file and line.

    When multiple agents flag the same location, keep the one with higher
    severity. If severity is equal, keep the one with higher confidence.
    """
    # Group by (file, line)
    by_location: dict[tuple[str, int], list[Finding]] = {}
    for finding in findings:
        key = (finding.file, finding.line)
        by_location.setdefault(key, []).append(finding)

    severity_rank = {
        Severity.CRITICAL: 3,
        Severity.WARNING: 2,
        Severity.SUGGESTION: 1,
    }

    deduped: list[Finding] = []
    for _key, group in by_location.items():
        if len(group) == 1:
            deduped.append(group[0])
        else:
            # Keep findings from different categories even at the same line
            seen_categories: set[str] = set()
            sorted_group = sorted(
                group,
                key=lambda f: (severity_rank.get(f.severity, 0), f.confidence),
                reverse=True,
            )
            for finding in sorted_group:
                if finding.category.value not in seen_categories:
                    deduped.append(finding)
                    seen_categories.add(finding.category.value)

    return deduped


def prioritize_findings(findings: list[Finding]) -> list[Finding]:
    """Sort findings by severity (critical first), then by confidence."""
    severity_rank = {
        Severity.CRITICAL: 3,
        Severity.WARNING: 2,
        Severity.SUGGESTION: 1,
    }
    return sorted(
        findings,
        key=lambda f: (severity_rank.get(f.severity, 0), f.confidence),
        reverse=True,
    )


def build_report(
    pr_url: str,
    pr_title: str,
    logic_findings: list[Finding],
    style_findings: list[Finding],
    security_findings: list[Finding],
) -> ReviewReport:
    """Build the final review report from all agent findings.

    Args:
        pr_url: The pull request URL
        pr_title: The pull request title
        logic_findings: Findings from the logic agent
        style_findings: Findings from the style agent
        security_findings: Findings from the security agent

    Returns:
        A consolidated, deduplicated, and prioritized ReviewReport
    """
    # Combine all findings
    all_findings = logic_findings + style_findings + security_findings

    # Deduplicate and prioritize
    deduped = deduplicate_findings(all_findings)
    prioritized = prioritize_findings(deduped)

    # Count by severity
    critical = sum(1 for f in prioritized if f.severity == Severity.CRITICAL)
    warnings = sum(1 for f in prioritized if f.severity == Severity.WARNING)
    suggestions = sum(1 for f in prioritized if f.severity == Severity.SUGGESTION)

    # Generate summary
    if critical > 0:
        summary = (
            f"⚠️ Found {critical} critical issue(s) that should be addressed before merging. "
            f"Review identified {len(prioritized)} total findings across "
            f"logic, style, and security."
        )
    elif warnings > 0:
        summary = (
            f"Found {warnings} warning(s) worth reviewing. "
            f"No critical issues detected. "
            f"{len(prioritized)} total findings."
        )
    else:
        summary = (
            "Code looks good overall. "
            f"Found {suggestions} minor suggestion(s) for improvement."
        )

    return ReviewReport(
        pr_url=pr_url,
        pr_title=pr_title,
        total_findings=len(prioritized),
        critical_count=critical,
        warning_count=warnings,
        suggestion_count=suggestions,
        findings=prioritized,
        summary=summary,
    )
