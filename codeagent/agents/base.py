"""Base agent utilities shared across all specialist agents."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from codeagent.config import Config
from codeagent.models.findings import Finding


def create_llm(config: Config) -> ChatOpenAI:
    """Create a configured LLM instance."""
    return ChatOpenAI(
        model=config.llm_model,
        temperature=config.llm_temperature,
        api_key=config.openai_api_key,
    )


def run_agent(
    config: Config,
    system_prompt: str,
    diff: str,
    file_contents: dict[str, str],
    agent_name: str,
) -> list[Finding]:
    """Run a specialist agent and return its findings.

    Args:
        config: Application configuration
        system_prompt: The agent's specialized system prompt
        diff: The PR diff to review
        file_contents: Full file contents for context
        agent_name: Name of the agent ('logic', 'style', or 'security')

    Returns:
        List of validated findings, capped at max_findings_per_agent
    """
    llm = create_llm(config)

    # Build the context message
    context_parts = [f"## Pull Request Diff\n\n```diff\n{diff}\n```\n"]
    for filename, content in file_contents.items():
        context_parts.append(
            f"## Full file: {filename}\n\n```\n{content[:5000]}\n```\n"
        )
    context = "\n".join(context_parts)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=context),
    ]

    response = llm.invoke(messages)

    # Parse the structured output
    findings = _parse_findings(response.content, agent_name)

    # Cap findings and filter low-confidence ones
    findings = [f for f in findings if f.confidence >= 0.5]
    return findings[: config.max_findings_per_agent]


def _parse_findings(response_text: Any, agent_name: str) -> list[Finding]:
    """Parse LLM response into validated Finding objects.

    Expects the LLM to return a JSON array of finding objects.
    Gracefully handles malformed output.
    """
    if not isinstance(response_text, str):
        return []

    # Try to extract JSON from the response
    text = response_text.strip()

    # Handle markdown code blocks
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start)
        text = text[start:end].strip()
    elif "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        text = text[start:end].strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Try to find a JSON array in the response
        bracket_start = text.find("[")
        bracket_end = text.rfind("]")
        if bracket_start != -1 and bracket_end != -1:
            try:
                data = json.loads(text[bracket_start : bracket_end + 1])
            except json.JSONDecodeError:
                return []
        else:
            return []

    if not isinstance(data, list):
        data = [data]

    findings: list[Finding] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        # Inject the agent name
        item["agent"] = agent_name
        try:
            findings.append(Finding.model_validate(item))
        except ValidationError:
            # Skip malformed findings
            continue

    return findings
