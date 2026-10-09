"""LangGraph workflow definition for the multi-agent code review pipeline."""

from __future__ import annotations

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from codeagent.agents.logic_agent import run_logic_agent
from codeagent.agents.orchestrator import build_report
from codeagent.agents.security_agent import run_security_agent
from codeagent.agents.style_agent import run_style_agent
from codeagent.config import Config
from codeagent.github.fetcher import fetch_pr
from codeagent.models.state import ReviewState


def create_workflow(config: Config) -> CompiledStateGraph:
    """Create and compile the LangGraph review workflow.

    The graph structure:
        fetch_pr → [logic, style, security] (parallel) → orchestrate → END

    Args:
        config: Application configuration

    Returns:
        Compiled LangGraph workflow ready to invoke
    """

    # --- Node functions ---
    # Each reads from state and returns only the fields it updates.

    def fetch_pr_node(state: ReviewState) -> dict:
        """Fetch the PR diff and file contents from GitHub."""
        pr_data = fetch_pr(config.github_token, state["pr_url"])
        return {
            "pr_title": pr_data.title,
            "diff": pr_data.diff,
            "file_contents": pr_data.file_contents,
        }

    def logic_node(state: ReviewState) -> dict:
        """Run the logic agent."""
        findings = run_logic_agent(config, state["diff"], state["file_contents"])
        return {"logic_findings": findings}

    def style_node(state: ReviewState) -> dict:
        """Run the style agent."""
        findings = run_style_agent(config, state["diff"], state["file_contents"])
        return {"style_findings": findings}

    def security_node(state: ReviewState) -> dict:
        """Run the security agent."""
        findings = run_security_agent(config, state["diff"], state["file_contents"])
        return {"security_findings": findings}

    def orchestrate_node(state: ReviewState) -> dict:
        """Merge, deduplicate, and prioritize all findings into a report."""
        report = build_report(
            pr_url=state["pr_url"],
            pr_title=state.get("pr_title", ""),
            logic_findings=state.get("logic_findings", []),
            style_findings=state.get("style_findings", []),
            security_findings=state.get("security_findings", []),
        )
        return {"final_report": report}

    # --- Build the graph ---
    graph = StateGraph(ReviewState)

    # Add nodes
    graph.add_node("fetch_pr", fetch_pr_node)
    graph.add_node("logic", logic_node)
    graph.add_node("style", style_node)
    graph.add_node("security", security_node)
    graph.add_node("orchestrate", orchestrate_node)

    # Entry point
    graph.set_entry_point("fetch_pr")

    # Fan-out: fetch_pr → all three agents in parallel
    graph.add_edge("fetch_pr", "logic")
    graph.add_edge("fetch_pr", "style")
    graph.add_edge("fetch_pr", "security")

    # Fan-in: all agents → orchestrator
    graph.add_edge("logic", "orchestrate")
    graph.add_edge("style", "orchestrate")
    graph.add_edge("security", "orchestrate")

    # End
    graph.add_edge("orchestrate", END)

    return graph.compile()
