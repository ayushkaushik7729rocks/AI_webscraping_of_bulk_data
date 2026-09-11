from src.extraction.record import build_research_paper_record


def test_build_research_paper_record():

    paper = {
        "title": "Test Paper",
        "authors": [
            "Alice",
            "Bob"
        ],
        "paper_url": "https://arxiv.org/abs/1234.5678",
        "published_date": "2026-09-10T12:00:00Z",
        "summary": "Test summary"
    }

    record = build_research_paper_record(paper)

    assert record["schemaVersion"] == "1.0"

    assert record["recordType"] == "research_paper"

    assert record["source"]["name"] == "arXiv"

    assert record["content"]["title"] == "Test Paper"

    assert record["content"]["authors"] == [
        "Alice",
        "Bob"
    ]

    assert record["content"]["paper_url"] == \
        "https://arxiv.org/abs/1234.5678"

    assert record["content"]["github_url"] is None

    assert record["content"]["github_stars"] is None

    assert record["collectedAt"] is not None