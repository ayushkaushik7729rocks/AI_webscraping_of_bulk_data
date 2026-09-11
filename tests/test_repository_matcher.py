from src.research.repository_matcher import RepositoryMatcher


def test_strong_repository_match():

    matcher = RepositoryMatcher()

    paper = {
        "title": "Vision Transformer for Medical Imaging",
        "paper_url": (
            "https://arxiv.org/abs/2305.12345v1"
        )
    }

    repository = {
        "name": "vision-transformer-medical-imaging",
        "description": (
            "Implementation of Vision Transformer "
            "for medical imaging. arXiv 2305.12345"
        )
    }

    result = matcher.score_repository(
        paper,
        repository
    )

    assert result["accepted"] is True
    assert result["score"] >= 70
    assert "arxiv_id_match" in result["evidence"]


def test_unrelated_repository_is_rejected():

    matcher = RepositoryMatcher()

    paper = {
        "title": "Vision Transformer for Medical Imaging",
        "paper_url": (
            "https://arxiv.org/abs/2305.12345v1"
        )
    }

    repository = {
        "name": "unrelated-project",
        "description": (
            "A cryptocurrency trading bot."
        )
    }

    result = matcher.score_repository(
        paper,
        repository
    )

    assert result["accepted"] is False
    assert result["score"] < 70

def test_extract_arxiv_id():

    assert RepositoryMatcher.extract_arxiv_id(
        "https://arxiv.org/abs/2305.12345v1"
    ) == "2305.12345"

    assert RepositoryMatcher.extract_arxiv_id(
        "https://arxiv.org/abs/2305.12345v2"
    ) == "2305.12345"

    assert RepositoryMatcher.extract_arxiv_id(
        "https://arxiv.org/pdf/2305.12345v1"
    ) == "2305.12345"

def test_select_best_repository():

    matcher = RepositoryMatcher()

    paper = {
        "title": "Vision Transformer for Medical Imaging",
        "paper_url": (
            "https://arxiv.org/abs/2305.12345v1"
        )
    }

    repositories = [
        {
            "name": "unrelated-project",
            "description": (
                "A cryptocurrency trading bot."
            )
        },
        {
            "name": "vision-transformer-medical-imaging",
            "description": (
                "Implementation of Vision Transformer "
                "for medical imaging. arXiv 2305.12345"
            )
        }
    ]

    result = matcher.select_best_repository(
        paper,
        repositories
    )

    assert result is not None

    assert (
        result["repository"]["name"]
        == "vision-transformer-medical-imaging"
    )

    assert result["score"] >= 70

def test_select_best_repository_returns_none_when_all_are_weak():

    matcher = RepositoryMatcher()

    paper = {
        "title": "Vision Transformer for Medical Imaging",
        "paper_url": (
            "https://arxiv.org/abs/2305.12345v1"
        )
    }

    repositories = [
        {
            "name": "crypto-bot",
            "description": "Cryptocurrency trading bot."
        },
        {
            "name": "weather-app",
            "description": "Weather forecasting application."
        }
    ]

    result = matcher.select_best_repository(
        paper,
        repositories
    )

    assert result is None

def test_explicit_paper_source_is_accepted():
    matcher = RepositoryMatcher()

    paper = {
        "title": "Retrieval is Cheap, Show Me the Code",
        "paper_url": "http://arxiv.org/abs/2605.12975v1",
    }

    repository = {
        "name": "PyRAG",
        "description": "Code for retrieval augmented generation",
        "html_url": "https://github.com/GasolSun36/PyRAG",
        "stargazers_count": 26,
        "source": "explicit_paper_source",
    }

    result = matcher.score_repository(
        paper,
        repository
    )

    assert result["accepted"] is True
    assert result["score"] == 100
    assert "explicit_paper_source" in result["evidence"]