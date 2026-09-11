from src.research.repository_resolver import RepositoryResolver


def test_repository_resolver_without_repository():

    resolver = RepositoryResolver()

    paper = {
        "title": "Test Paper",
        "authors": ["Alice"],
        "paper_url": "https://arxiv.org/abs/1234.5678",
        "github_url": None
    }

    result = resolver.resolve(paper)

    assert result["github_url"] is None
    assert result["confidence"] == 0.0
    assert result["evidence"] is None


def test_repository_resolver_with_explicit_repository():

    resolver = RepositoryResolver()

    paper = {
        "title": "Test Paper",
        "authors": ["Alice"],
        "paper_url": "https://arxiv.org/abs/1234.5678",
        "github_url": "https://github.com/example/test-project"
    }

    result = resolver.resolve(paper)

    assert result["github_url"] == \
        "https://github.com/example/test-project"

    assert result["confidence"] == 1.0

    assert result["evidence"] == "explicit_source"