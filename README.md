# 🔍 CodeAgent

**Multi-agent AI code review system** that analyzes GitHub pull requests using specialized AI agents for logic bugs, style issues, and security vulnerabilities.

[![CI](https://github.com/Enoch-Nemili/codeagent/actions/workflows/ci.yml/badge.svg)](https://github.com/Enoch-Nemili/codeagent/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## Architecture

CodeAgent uses a **fan-out/fan-in multi-agent architecture** powered by [LangGraph](https://github.com/langchain-ai/langgraph). Three specialist agents review code in parallel, and an orchestrator merges their findings into a single prioritized report.

```
                    ┌──────────────┐
                    │  GitHub PR   │
                    │  (diff +     │
                    │   context)   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ Orchestrator │
                    │  (routes &   │
                    │   merges)    │
                    └──┬───┬───┬───┘
                       │   │   │
              ┌────────┘   │   └────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Logic   │ │  Style   │ │ Security │
        │  Agent   │ │  Agent   │ │  Agent   │
        │          │ │          │ │          │
        │ bugs,    │ │ naming,  │ │ SQLi,    │
        │ edge     │ │ patterns,│ │ XSS,     │
        │ cases    │ │ idioms   │ │ secrets  │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │             │             │
             └─────────┬───┘─────────────┘
                       │
              ┌────────▼────────┐
              │  Final Report   │
              │  (deduplicated, │
              │   prioritized)  │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  Post to PR as  │
              │  review comment │
              └─────────────────┘
```

## Agents

| Agent | Focus | Example Findings |
|-------|-------|-----------------|
| **Logic Agent** | Bugs, edge cases, error handling | Off-by-one errors, null references, unhandled exceptions |
| **Style Agent** | Code quality, readability, best practices | Poor naming, high complexity, code duplication |
| **Security Agent** | Vulnerabilities, security risks | SQL injection, hardcoded secrets, path traversal |
| **Orchestrator** | Deduplication, prioritization, reporting | Merges overlapping findings, assigns final severity |

## Quick Start

### Prerequisites

- Python 3.11+
- An OpenAI API key (GPT-4o-mini recommended for cost efficiency)
- A GitHub personal access token with `repo` scope

### Installation

```bash
# Clone the repo
git clone https://github.com/Enoch-Nemili/codeagent.git
cd codeagent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Usage

```bash
# Review a pull request
codeagent review https://github.com/owner/repo/pull/123

# Review and post comments to the PR
codeagent review https://github.com/owner/repo/pull/123 --post

# Verbose output with detailed findings
codeagent review https://github.com/owner/repo/pull/123 -v

# Verify your configuration
codeagent check-config
```

### Example Output

```
╭──────────────────────────────────╮
│ 🔍 CodeAgent                    │
│ Reviewing: owner/repo#123       │
╰──────────────────────────────────╯

⚠️ Found 2 critical issue(s) that should be addressed before merging.
Review identified 7 total findings across logic, style, and security.

┌──────────────┬───────┐
│ Severity     │ Count │
├──────────────┼───────┤
│ 🔴 Critical  │     2 │
│ 🟡 Warning   │     3 │
│ 💡 Suggestion │     2 │
└──────────────┴───────┘
```

## Development

```bash
# Run tests
pytest tests/ -v

# Run linter
ruff check codeagent/ tests/

# Run type checker
mypy codeagent/ --ignore-missing-imports
```

## Project Structure

```
codeagent/
├── agents/           # Specialist review agents
│   ├── base.py       # Shared agent utilities
│   ├── logic_agent.py
│   ├── style_agent.py
│   ├── security_agent.py
│   └── orchestrator.py
├── graph/            # LangGraph workflow
│   ├── state.py
│   └── workflow.py
├── github/           # GitHub API integration
│   ├── fetcher.py    # PR diff retrieval
│   └── commenter.py  # Review comment posting
├── models/           # Pydantic schemas
│   ├── findings.py   # Finding & ReviewReport
│   └── state.py      # Shared ReviewState
├── cli.py            # Click CLI entry point
└── config.py         # Configuration management
```

## Tech Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** — Graph-based agent orchestration with parallel execution
- **[OpenAI GPT-4o-mini](https://openai.com/)** — LLM backbone for each specialist agent
- **[PyGithub](https://github.com/PyGithub/PyGithub)** — GitHub API integration for PR fetching and commenting
- **[Pydantic](https://docs.pydantic.dev/)** — Structured output validation and data models
- **[Click](https://click.palletsprojects.com/)** + **[Rich](https://rich.readthedocs.io/)** — CLI interface with formatted output
- **[Pytest](https://docs.pytest.org/)** — Testing framework with coverage reporting
- **[Ruff](https://docs.astral.sh/ruff/)** — Fast Python linter and formatter

## Design Decisions

**Why LangGraph over CrewAI?** LangGraph provides fine-grained control over error handling with per-node retries, built-in checkpointing for resumable reviews, and first-class support for parallel agent execution — all critical for a reliable code review pipeline.

**Why structured output?** Each agent returns findings as validated Pydantic models rather than free-form text. This ensures consistent formatting, enables programmatic deduplication, and makes the review parseable for downstream integrations.

**Why fan-out/fan-in?** Running agents in parallel reduces total review time by ~3x. The orchestrator's deduplication step prevents the same issue from being reported by multiple agents.

## License

MIT
