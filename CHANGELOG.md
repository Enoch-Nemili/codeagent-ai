# Changelog

All notable changes to CodeAgent. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-09

First release.

### Added
- **Multi-agent review** of GitHub pull requests: logic, style and security specialist agents run in parallel (LangGraph fan-out/fan-in), and an orchestrator deduplicates findings and assigns final severity.
- **Structured findings**: every agent returns validated Pydantic models, so reports are consistent and machine-readable.
- **GitHub integration** (PyGithub): fetch PR diffs, and optionally post the review as a PR comment (`--post`).
- **CLI** (Click + Rich): `codeagent review <pr-url>`, `--verbose`, `codeagent check-config`.
- 28 tests (agents, fetcher, models, orchestrator) and CI running ruff, mypy and pytest with coverage.

[0.1.0]: https://github.com/Enoch-Nemili/codeagent-ai/releases/tag/v0.1.0
