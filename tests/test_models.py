"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from codeagent.models.findings import (
    Category,
    Finding,
    ReviewReport,
    Severity,
)


class TestFinding:
    """Tests for the Finding model."""

    def test_valid_finding(self):
        finding = Finding(
            file="app/auth.py",
            line=10,
            severity=Severity.CRITICAL,
            category=Category.SQL_INJECTION,
            agent="security",
            message="SQL injection via string concatenation",
            suggestion="Use parameterized queries instead",
            confidence=0.95,
        )
        assert finding.file == "app/auth.py"
        assert finding.line == 10
        assert finding.severity == Severity.CRITICAL
        assert finding.confidence == 0.95

    def test_invalid_line_number(self):
        with pytest.raises((ValueError, ValidationError)):
            Finding(
                file="app/auth.py",
                line=0,  # must be >= 1
                severity=Severity.WARNING,
                category=Category.BUG,
                agent="logic",
                message="test",
                suggestion="test",
                confidence=0.5,
            )

    def test_invalid_confidence(self):
        with pytest.raises((ValueError, ValidationError)):
            Finding(
                file="app/auth.py",
                line=1,
                severity=Severity.WARNING,
                category=Category.BUG,
                agent="logic",
                message="test",
                suggestion="test",
                confidence=1.5,  # must be <= 1.0
            )

    def test_invalid_agent(self):
        with pytest.raises((ValueError, ValidationError)):
            Finding(
                file="app/auth.py",
                line=1,
                severity=Severity.WARNING,
                category=Category.BUG,
                agent="invalid_agent",  # must be logic, style, or security
                message="test",
                suggestion="test",
                confidence=0.5,
            )


class TestReviewReport:
    """Tests for the ReviewReport model."""

    def _make_finding(self, severity: Severity, category: Category, agent: str) -> Finding:
        return Finding(
            file="app/auth.py",
            line=10,
            severity=severity,
            category=category,
            agent=agent,
            message="Test finding",
            suggestion="Fix it",
            confidence=0.8,
        )

    def test_empty_report(self):
        report = ReviewReport(pr_url="https://github.com/o/r/pull/1")
        assert report.total_findings == 0
        assert report.critical_count == 0
        assert "CodeAgent Review" in report.format_markdown()

    def test_report_with_findings(self):
        findings = [
            self._make_finding(Severity.CRITICAL, Category.SQL_INJECTION, "security"),
            self._make_finding(Severity.WARNING, Category.NAMING, "style"),
            self._make_finding(Severity.SUGGESTION, Category.READABILITY, "style"),
        ]
        report = ReviewReport(
            pr_url="https://github.com/o/r/pull/1",
            total_findings=3,
            critical_count=1,
            warning_count=1,
            suggestion_count=1,
            findings=findings,
            summary="Found issues",
        )
        md = report.format_markdown()
        assert "1 critical" in md
        assert "1 warnings" in md
        assert "1 suggestions" in md

    def test_format_markdown_includes_findings(self):
        finding = self._make_finding(Severity.CRITICAL, Category.BUG, "logic")
        report = ReviewReport(
            pr_url="https://github.com/o/r/pull/1",
            total_findings=1,
            critical_count=1,
            findings=[finding],
            summary="Found a bug",
        )
        md = report.format_markdown()
        assert "app/auth.py:10" in md
        assert "bug" in md
