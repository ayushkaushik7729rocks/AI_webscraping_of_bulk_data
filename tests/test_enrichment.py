import pytest

from src.research.run_enrichment import enrich_paper


@pytest.mark.asyncio
async def test_enrichment_uses_paperswithcode_fallback(
    monkeypatch
):
    class FakeArxivClient:

        def __init__(self, crawler):
            pass

        async def get_github_urls(self, paper_url):
            return []


    class FakePapersWithCodeClient:

        def __init__(self, crawler):
            pass

        async def get_paper(self, arxiv_id):
            return {
                "github_urls": [
                    "https://github.com/example/project"
                ]
            }


    class FakeGitHubClient:

        def __init__(self, crawler):
            pass

        async def get_repository_metadata(
            self,
            github_url
        ):
            return {
                "name": "Example Project",
                "description": (
                    "Implementation of Example Project "
                    "for arXiv 1234.5678"
                ),
                "html_url": github_url,
                "stargazers_count": 42,
            }

    monkeypatch.setattr(
        "src.research.run_enrichment.ArxivClient",
        FakeArxivClient
    )

    monkeypatch.setattr(
        "src.research.run_enrichment.PapersWithCodeClient",
        FakePapersWithCodeClient
    )

    monkeypatch.setattr(
        "src.research.run_enrichment.GitHubClient",
        FakeGitHubClient
    )

    paper = {
        "title": "Example Project",
        "authors": ["Test Author"],
        "paper_url": (
            "https://arxiv.org/abs/1234.5678"
        ),
        "published_date": (
            "2026-01-01T00:00:00Z"
        ),
    }

    record = await enrich_paper(
        crawler=None,
        paper=paper
    )

    assert (
        record["content"]["github_url"]
        == "https://github.com/example/project"
    )

    assert (
        record["content"]["github_stars"]
        == 42
    )

    assert (
        record["content"]["repository_match"]
        ["discovery_source"]
        == "paperswithcode_source"
    )