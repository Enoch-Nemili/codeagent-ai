"""Configuration management for CodeAgent."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    """Application configuration loaded from environment variables."""

    openai_api_key: str = ""
    github_token: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    max_findings_per_agent: int = 10

    @classmethod
    def from_env(cls) -> Config:
        """Load configuration from .env file and environment variables."""
        load_dotenv()
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            github_token=os.getenv("GITHUB_TOKEN", ""),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
            max_findings_per_agent=int(os.getenv("MAX_FINDINGS_PER_AGENT", "10")),
        )

    def validate(self) -> list[str]:
        """Return a list of configuration errors, empty if valid."""
        errors: list[str] = []
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is not set")
        if not self.github_token:
            errors.append("GITHUB_TOKEN is not set")
        return errors
