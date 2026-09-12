from src.research.dedup import ResearchPaperDeduplicator


def test_arxiv_versions_have_same_identity():
    paper_v1 = {
        "paper_url": "https://arxiv.org/abs/2605.12975v1"
    }

    paper_v2 = {
        "paper_url": "https://arxiv.org/abs/2605.12975v2"
    }

    id_v1 = ResearchPaperDeduplicator.get_identity(paper_v1)
    id_v2 = ResearchPaperDeduplicator.get_identity(paper_v2)

    assert id_v1 == "arxiv:2605.12975"
    assert id_v1 == id_v2


def test_different_arxiv_papers_have_different_ids():
    paper1 = {
        "paper_url": "https://arxiv.org/abs/2605.12975v1"
    }

    paper2 = {
        "paper_url": "https://arxiv.org/abs/2605.12976v1"
    }

    id1 = ResearchPaperDeduplicator.get_identity(paper1)
    id2 = ResearchPaperDeduplicator.get_identity(paper2)

    assert id1 != id2


def test_deduplication_removes_duplicate_versions():
    papers = [
        {
            "title": "Paper A",
            "paper_url": "https://arxiv.org/abs/2605.12975v1"
        },
        {
            "title": "Paper A Updated",
            "paper_url": "https://arxiv.org/abs/2605.12975v2"
        },
        {
            "title": "Paper B",
            "paper_url": "https://arxiv.org/abs/2605.12976v1"
        },
    ]

    unique = ResearchPaperDeduplicator.deduplicate(papers)

    assert len(unique) == 2
    assert unique[0]["title"] == "Paper A"
    assert unique[1]["title"] == "Paper B"


def test_deduplication_preserves_order():
    papers = [
        {
            "title": "Paper C",
            "paper_url": "https://arxiv.org/abs/2605.12977v1"
        },
        {
            "title": "Paper A",
            "paper_url": "https://arxiv.org/abs/2605.12975v1"
        },
        {
            "title": "Paper B",
            "paper_url": "https://arxiv.org/abs/2605.12976v1"
        },
        {
            "title": "Paper A duplicate",
            "paper_url": "https://arxiv.org/abs/2605.12975v2"
        },
    ]

    unique = ResearchPaperDeduplicator.deduplicate(papers)

    titles = [paper["title"] for paper in unique]

    assert titles == ["Paper C", "Paper A", "Paper B"]


def test_non_arxiv_urls_use_url_identity():
    paper1 = {
        "paper_url": "https://example.com/paper123/"
    }

    paper2 = {
        "paper_url": "https://example.com/paper123/"
    }

    id1 = ResearchPaperDeduplicator.get_identity(paper1)
    id2 = ResearchPaperDeduplicator.get_identity(paper2)

    assert id1 == id2
    assert id1 == "url:https://example.com/paper123"