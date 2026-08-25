"""Tests for the agent base parsing utilities."""

from codeagent.agents.base import _parse_findings


class TestParseFindingsOutput:
    """Tests for parsing LLM response text into Finding objects."""

    def test_valid_json_array(self):
        text = """[
            {
                "file": "app/auth.py",
                "line": 10,
                "severity": "critical",
                "category": "sql-injection",
                "message": "SQL injection risk",
                "suggestion": "Use parameterized queries",
                "confidence": 0.95
            }
        ]"""
        findings = _parse_findings(text, "security")
        assert len(findings) == 1
        assert findings[0].file == "app/auth.py"
        assert findings[0].agent == "security"

    def test_json_in_markdown_code_block(self):
        text = """Here are my findings:

```json
[
    {
        "file": "app/auth.py",
        "line": 5,
        "severity": "warning",
        "category": "naming",
        "message": "Variable name unclear",
        "suggestion": "Rename to something descriptive",
        "confidence": 0.7
    }
]
```"""
        findings = _parse_findings(text, "style")
        assert len(findings) == 1
        assert findings[0].agent == "style"

    def test_empty_array(self):
        findings = _parse_findings("[]", "logic")
        assert len(findings) == 0

    def test_malformed_json(self):
        findings = _parse_findings("this is not json at all", "logic")
        assert len(findings) == 0

    def test_partial_valid_findings(self):
        text = """[
            {
                "file": "app/auth.py",
                "line": 10,
                "severity": "critical",
                "category": "bug",
                "message": "Valid finding",
                "suggestion": "Fix it",
                "confidence": 0.9
            },
            {
                "invalid": "missing required fields"
            }
        ]"""
        findings = _parse_findings(text, "logic")
        assert len(findings) == 1

    def test_non_string_input(self):
        findings = _parse_findings(None, "logic")
        assert len(findings) == 0
        findings = _parse_findings(123, "logic")
        assert len(findings) == 0
