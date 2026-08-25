"""Tests for the GitHub PR fetcher."""

import pytest

from codeagent.github.fetcher import parse_pr_url


class TestParsePrUrl:
    """Tests for PR URL parsing."""

    def test_valid_url(self):
        owner, repo, number = parse_pr_url(
            "https://github.com/microsoft/vscode/pull/42"
        )
        assert owner == "microsoft"
        assert repo == "vscode"
        assert number == 42

    def test_valid_url_with_trailing_slash(self):
        owner, repo, number = parse_pr_url(
            "https://github.com/owner/repo/pull/123/"
        )
        assert owner == "owner"
        assert repo == "repo"
        assert number == 123

    def test_valid_url_with_extra_path(self):
        owner, repo, number = parse_pr_url(
            "https://github.com/owner/repo/pull/456/files"
        )
        assert owner == "owner"
        assert repo == "repo"
        assert number == 456

    def test_invalid_url_no_pull(self):
        with pytest.raises(ValueError, match="Invalid GitHub PR URL"):
            parse_pr_url("https://github.com/owner/repo/issues/42")

    def test_invalid_url_random(self):
        with pytest.raises(ValueError, match="Invalid GitHub PR URL"):
            parse_pr_url("https://example.com/not-a-pr")

    def test_invalid_url_empty(self):
        with pytest.raises(ValueError, match="Invalid GitHub PR URL"):
            parse_pr_url("")
