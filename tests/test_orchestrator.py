"""Tests for the orchestrator's deduplication and prioritization logic."""

from codeagent.agents.orchestrator import (
    build_report,
    deduplicate_findings,
    prioritize_findings,
)
from codeagent.models.findings import Category, Finding, Severity


def _finding(
    file: str = "app/auth.py",
    line: int = 10,
    severity: Severity = Severity.WARNING,
    category: Category = Category.BUG,
    agent: str = "logic",
    confidence: float = 0.8,
) -> Finding:
    return Finding(
        file=file,
        line=line,
        severity=severity,
        category=category,
        agent=agent,
        message="Test",
        suggestion="Fix",
        confidence=confidence,
    )


class TestDeduplication:
    """Tests for finding deduplication."""

    def test_no_duplicates(self):
        findings = [
            _finding(line=10),
            _finding(line=20),
        ]
        result = deduplicate_findings(findings)
        assert len(result) == 2

    def test_same_location_different_category_kept(self):
        findings = [
            _finding(line=10, category=Category.BUG, agent="logic"),
            _finding(line=10, category=Category.SQL_INJECTION, agent="security"),
        ]
        result = deduplicate_findings(findings)
        assert len(result) == 2

    def test_same_location_same_category_deduped(self):
        findings = [
            _finding(line=10, category=Category.BUG, agent="logic", confidence=0.9),
            _finding(line=10, category=Category.BUG, agent="logic", confidence=0.5),
        ]
        result = deduplicate_findings(findings)
        assert len(result) == 1
        assert result[0].confidence == 0.9  # keeps higher confidence

    def test_higher_severity_wins(self):
        findings = [
            _finding(line=10, category=Category.BUG, severity=Severity.SUGGESTION),
            _finding(line=10, category=Category.BUG, severity=Severity.CRITICAL),
        ]
        result = deduplicate_findings(findings)
        assert len(result) == 1
        assert result[0].severity == Severity.CRITICAL


class TestPrioritization:
    """Tests for finding prioritization."""

    def test_critical_first(self):
        findings = [
            _finding(severity=Severity.SUGGESTION, line=1),
            _finding(severity=Severity.CRITICAL, line=2),
            _finding(severity=Severity.WARNING, line=3),
        ]
        result = prioritize_findings(findings)
        assert result[0].severity == Severity.CRITICAL
        assert result[1].severity == Severity.WARNING
        assert result[2].severity == Severity.SUGGESTION

    def test_same_severity_sorted_by_confidence(self):
        findings = [
            _finding(severity=Severity.WARNING, confidence=0.5, line=1),
            _finding(severity=Severity.WARNING, confidence=0.9, line=2),
        ]
        result = prioritize_findings(findings)
        assert result[0].confidence == 0.9


class TestBuildReport:
    """Tests for the full report builder."""

    def test_empty_findings(self):
        report = build_report(
            pr_url="https://github.com/o/r/pull/1",
            pr_title="Test PR",
            logic_findings=[],
            style_findings=[],
            security_findings=[],
        )
        assert report.total_findings == 0
        assert "looks good" in report.summary.lower()

    def test_critical_findings_warning_summary(self):
        report = build_report(
            pr_url="https://github.com/o/r/pull/1",
            pr_title="Test PR",
            logic_findings=[_finding(severity=Severity.CRITICAL)],
            style_findings=[],
            security_findings=[],
        )
        assert report.critical_count == 1
        assert "critical" in report.summary.lower()

    def test_combines_all_agents(self):
        report = build_report(
            pr_url="https://github.com/o/r/pull/1",
            pr_title="Test PR",
            logic_findings=[_finding(agent="logic", line=1, category=Category.BUG)],
            style_findings=[_finding(agent="style", line=2, category=Category.NAMING)],
            security_findings=[_finding(agent="security", line=3, category=Category.XSS)],
        )
        assert report.total_findings == 3
        agents = {f.agent for f in report.findings}
        assert agents == {"logic", "style", "security"}
