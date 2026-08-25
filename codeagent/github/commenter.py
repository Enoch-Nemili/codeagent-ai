"""Post review comments back to GitHub pull requests."""

from __future__ import annotations

from github import Github

from codeagent.models.findings import ReviewReport


def post_review_comment(
    github_token: str,
    owner: str,
    repo_name: str,
    pr_number: int,
    report: ReviewReport,
) -> str:
    """Post the review report as a comment on the pull request.

    Args:
        github_token: GitHub personal access token
        owner: Repository owner
        repo_name: Repository name
        pr_number: Pull request number
        report: The finalized review report

    Returns:
        URL of the created comment
    """
    gh = Github(github_token)
    repo = gh.get_repo(f"{owner}/{repo_name}")
    pr = repo.get_pull(pr_number)

    comment = pr.create_issue_comment(report.format_markdown())
    return comment.html_url


def post_inline_comments(
    github_token: str,
    owner: str,
    repo_name: str,
    pr_number: int,
    report: ReviewReport,
    commit_sha: str,
) -> int:
    """Post individual findings as inline review comments on specific lines.

    Args:
        github_token: GitHub personal access token
        owner: Repository owner
        repo_name: Repository name
        pr_number: Pull request number
        report: The finalized review report
        commit_sha: The head commit SHA of the PR

    Returns:
        Number of inline comments posted
    """
    gh = Github(github_token)
    repo = gh.get_repo(f"{owner}/{repo_name}")
    pr = repo.get_pull(pr_number)
    commit = repo.get_commit(commit_sha)

    posted = 0
    for finding in report.findings:
        severity_icon = {
            "critical": "🔴",
            "warning": "🟡",
            "suggestion": "💡",
        }.get(finding.severity.value, "")

        body = (
            f"{severity_icon} **{finding.category.value}** "
            f"({finding.agent} agent)\n\n"
            f"{finding.message}\n\n"
            f"> **Suggestion:** {finding.suggestion}"
        )

        try:
            pr.create_review_comment(
                body=body,
                commit=commit,
                path=finding.file,
                line=finding.line,
            )
            posted += 1
        except Exception:
            # Line might not be part of the diff — skip silently
            continue

    return posted
