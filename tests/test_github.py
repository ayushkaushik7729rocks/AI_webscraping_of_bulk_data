import pytest

from src.github.client import GitHubClient


@pytest.mark.asyncio
async def test_get_repository_metadata():

    class FakeCrawler:
        async def fetch(self, url, headers=None):
            return {
                "status": 200,
                "html": """
                {
                    "name": "test-repo",
                    "full_name": "test-owner/test-repo",
                    "description": "A test repository",
                    "stargazers_count": 123,
                    "html_url": "https://github.com/test-owner/test-repo"
                }
                """,
                "error": None,
                "url": url,
            }

    client = GitHubClient(FakeCrawler())

    metadata = await client.get_repository_metadata(
        "https://github.com/test-owner/test-repo"
    )

    assert metadata["owner"] == "test-owner"
    assert metadata["repo"] == "test-repo"
    assert metadata["name"] == "test-repo"
    assert metadata["full_name"] == "test-owner/test-repo"
    assert metadata["description"] == "A test repository"
    assert metadata["stargazers_count"] == 123
    assert metadata["html_url"] == (
        "https://github.com/test-owner/test-repo"
    )