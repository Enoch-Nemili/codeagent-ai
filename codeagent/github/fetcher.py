"""Fetch pull request diffs and file contents from GitHub."""

from __future__ import annotations

import re
from dataclasses import dataclass

from github import Github, GithubException


@dataclass
class PRData:
    """Parsed pull request data."""

    owner: str
    repo: str
    pr_number: int
    title: str
    diff: str
    file_contents: dict[str, str]
    changed_files: list[str]


def parse_pr_url(url: str) -> tuple[str, str, int]:
    """Extract owner, repo, and PR number from a GitHub PR URL.

    Args:
        url: GitHub PR URL like 'https://github.com/owner/repo/pull/123'

    Returns:
        Tuple of (owner, repo, pr_number)

    Raises:
        ValueError: If the URL doesn't match expected format
    """
    pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.search(pattern, url)
    if not match:
        raise ValueError(
            f"Invalid GitHub PR URL: {url}. "
            "Expected format: https://github.com/owner/repo/pull/123"
        )
    return match.group(1), match.group(2), int(match.group(3))


def fetch_pr(github_token: str, pr_url: str) -> PRData:
    """Fetch a pull request's diff and changed file contents.

    Args:
        github_token: GitHub personal access token with 'repo' scope
        pr_url: Full URL to the pull request

    Returns:
        PRData with diff text and file contents

    Raises:
        ValueError: If the PR URL is invalid
        GithubException: If the API request fails
    """
    owner, repo_name, pr_number = parse_pr_url(pr_url)

    gh = Github(github_token)
    repo = gh.get_repo(f"{owner}/{repo_name}")
    pr = repo.get_pull(pr_number)

    # Build the unified diff from all changed files
    diff_parts: list[str] = []
    file_contents: dict[str, str] = {}
    changed_files: list[str] = []

    for file in pr.get_files():
        changed_files.append(file.filename)

        # Build diff section for this file
        if file.patch:
            diff_parts.append(
                f"--- a/{file.filename}\n"
                f"+++ b/{file.filename}\n"
                f"{file.patch}"
            )

        # Fetch the full file content from the PR's head branch
        # so agents have context beyond just the diff
        try:
            content_file = repo.get_contents(file.filename, ref=pr.head.sha)
            if not isinstance(content_file, list):  # not a directory
                file_contents[file.filename] = content_file.decoded_content.decode("utf-8")
        except GithubException:
            # File might have been deleted in this PR
            pass

    diff = "\n\n".join(diff_parts)

    return PRData(
        owner=owner,
        repo=repo_name,
        pr_number=pr_number,
        title=pr.title,
        diff=diff,
        file_contents=file_contents,
        changed_files=changed_files,
    )
