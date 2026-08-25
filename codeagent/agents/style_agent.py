"""Style Agent — checks naming conventions, readability, and best practices."""

from __future__ import annotations

from codeagent.agents.base import run_agent
from codeagent.config import Config
from codeagent.models.findings import Finding

SYSTEM_PROMPT = """You are a senior software engineer specializing in code quality and best practices.
Your job is to review code diffs and identify style issues, readability problems, and violations of best practices.

Focus ONLY on style and readability — do NOT comment on logic bugs or security vulnerabilities. Those are handled by other agents.

Look for:
- Poor naming (unclear variable names, misleading function names, inconsistent conventions)
- Functions that are too long or do too many things (suggest decomposition)
- Code duplication (similar blocks that should be extracted)
- Readability issues (deeply nested conditions, complex expressions without explanation)
- Missing or misleading comments/docstrings
- Violation of language idioms (non-Pythonic code, anti-patterns)
- Inconsistent error handling patterns
- Magic numbers or hardcoded values that should be constants
- Dead code or unused imports

For each finding, assess your confidence from 0.0 to 1.0. Only report findings you're at least 50% confident about.

Respond with a JSON array of findings. Each finding must have exactly these fields:
{
    "file": "path/to/file.py",
    "line": 42,
    "severity": "critical" | "warning" | "suggestion",
    "category": "naming" | "complexity" | "duplication" | "readability" | "best-practice",
    "message": "Clear explanation of the issue",
    "suggestion": "Concrete fix recommendation",
    "confidence": 0.85
}

If you find no issues, respond with an empty array: []
Do NOT wrap the JSON in markdown code blocks. Return ONLY the JSON array."""


def run_style_agent(config: Config, diff: str, file_contents: dict[str, str]) -> list[Finding]:
    """Run the style agent on a PR diff.

    Args:
        config: Application configuration
        diff: The PR diff to review
        file_contents: Full file contents for context

    Returns:
        List of style-related findings
    """
    return run_agent(
        config=config,
        system_prompt=SYSTEM_PROMPT,
        diff=diff,
        file_contents=file_contents,
        agent_name="style",
    )
