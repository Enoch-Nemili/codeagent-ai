"""CLI entry point for CodeAgent."""

from __future__ import annotations

import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from codeagent.config import Config
from codeagent.github.commenter import post_review_comment
from codeagent.github.fetcher import parse_pr_url
from codeagent.graph.workflow import create_workflow
from codeagent.models.findings import Severity

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="codeagent")
def main() -> None:
    """CodeAgent — AI-powered multi-agent code review."""
    pass


@main.command()
@click.argument("pr_url")
@click.option("--post", is_flag=True, help="Post the review as a comment on the PR")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def review(pr_url: str, post: bool, verbose: bool) -> None:
    """Review a GitHub pull request.

    PR_URL is the full URL to a GitHub pull request.
    Example: https://github.com/owner/repo/pull/123
    """
    config = Config.from_env()

    # Validate config
    errors = config.validate()
    if errors:
        for error in errors:
            console.print(f"[red]✗[/red] {error}")
        console.print("\n[dim]Copy .env.example to .env and fill in your keys.[/dim]")
        sys.exit(1)

    # Validate URL format
    try:
        owner, repo_name, pr_number = parse_pr_url(pr_url)
    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
        sys.exit(1)

    console.print(
        Panel(
            f"[bold]Reviewing:[/bold] {owner}/{repo_name}#{pr_number}",
            title="🔍 CodeAgent",
            border_style="green",
        )
    )

    # Run the review workflow
    with console.status("[bold green]Fetching PR and running agents..."):
        workflow = create_workflow(config)
        result = workflow.invoke(
            {
                "pr_url": pr_url,
                "pr_title": "",
                "diff": "",
                "file_contents": {},
                "logic_findings": [],
                "style_findings": [],
                "security_findings": [],
                "final_report": None,
            }
        )

    report = result["final_report"]
    if report is None:
        console.print("[red]✗[/red] Review failed — no report generated.")
        sys.exit(1)

    # Display results
    _display_report(report, verbose)

    # Post to GitHub if requested
    if post:
        with console.status("[bold green]Posting review to GitHub..."):
            comment_url = post_review_comment(
                github_token=config.github_token,
                owner=owner,
                repo_name=repo_name,
                pr_number=pr_number,
                report=report,
            )
        console.print(f"\n[green]✓[/green] Review posted: {comment_url}")


def _display_report(report, verbose: bool) -> None:
    """Display the review report in the terminal."""
    console.print()
    console.print(f"[bold]{report.summary}[/bold]")
    console.print()

    if not report.findings:
        console.print("[green]✓ No issues found — code looks clean![/green]")
        return

    # Summary table
    table = Table(title="Review Summary", show_header=True, header_style="bold")
    table.add_column("Severity", style="bold", width=12)
    table.add_column("Count", justify="right", width=8)
    table.add_row("🔴 Critical", str(report.critical_count))
    table.add_row("🟡 Warning", str(report.warning_count))
    table.add_row("💡 Suggestion", str(report.suggestion_count))
    console.print(table)

    if verbose:
        console.print()
        # Detailed findings
        for finding in report.findings:
            severity_color = {
                Severity.CRITICAL: "red",
                Severity.WARNING: "yellow",
                Severity.SUGGESTION: "blue",
            }.get(finding.severity, "white")

            console.print(
                Panel(
                    f"[bold]{finding.message}[/bold]\n\n"
                    f"[dim]File:[/dim] {finding.file}:{finding.line}\n"
                    f"[dim]Category:[/dim] {finding.category.value}\n"
                    f"[dim]Agent:[/dim] {finding.agent}\n"
                    f"[dim]Confidence:[/dim] {finding.confidence:.0%}\n\n"
                    f"[green]Suggestion:[/green] {finding.suggestion}",
                    border_style=severity_color,
                    title=f"{finding.severity.value.upper()}",
                )
            )


@main.command()
def check_config() -> None:
    """Verify that all required configuration is set."""
    config = Config.from_env()
    errors = config.validate()

    if errors:
        for error in errors:
            console.print(f"[red]✗[/red] {error}")
        sys.exit(1)
    else:
        console.print("[green]✓[/green] All configuration looks good!")
        console.print(f"  [dim]Model:[/dim] {config.llm_model}")
        console.print(f"  [dim]Max findings per agent:[/dim] {config.max_findings_per_agent}")


if __name__ == "__main__":
    main()
