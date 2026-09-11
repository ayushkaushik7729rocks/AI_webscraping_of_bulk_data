from src.github.client import GitHubClient


def test_parse_repository_url():

    owner, repo = GitHubClient.parse_repository_url(
        "https://github.com/openai/gpt-2"
    )

    assert owner == "openai"
    assert repo == "gpt-2"


def test_parse_repository_url_with_git_suffix():

    owner, repo = GitHubClient.parse_repository_url(
        "https://github.com/openai/gpt-2.git"
    )

    assert owner == "openai"
    assert repo == "gpt-2"


def test_extract_star_count():

    repository = {
        "name": "test-project",
        "full_name": "example/test-project",
        "html_url": "https://github.com/example/test-project",
        "stargazers_count": 123
    }

    assert repository["stargazers_count"] == 123