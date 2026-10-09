# Contributing to CodeAgent

Issues and pull requests are welcome.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env            # add your keys
codeagent check-config
```

## Before opening a pull request

```bash
ruff check codeagent/ tests/
mypy codeagent/ --ignore-missing-imports
pytest tests/ -v
```

Tests use fixtures and mocks, so no API keys or network are needed. New agents or orchestrator rules should come with tests in `tests/`.

## Conventions

- One branch and one pull request per change; reference issues with `Closes #N`.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, ...).
- Security issues: see [SECURITY.md](SECURITY.md).
