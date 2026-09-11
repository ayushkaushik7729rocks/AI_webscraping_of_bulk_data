from src.extraction.record import build_source_record


def test_build_source_record():

    extracted_data = {
        "url": "https://example.com/news",
        "title": "AI News",
        "description": "Example description",
        "canonical_url": None,
        "og_url": None,
        "published_date": (
            "2026-09-11T10:00:00+00:00"
        ),
        "main_text": "Example article text.",
    }

    record = build_source_record(
        extracted_data,
        "Example News"
    )

    assert record["source"]["name"] == "Example News"

    assert (
        record["source"]["url"]
        == "https://example.com/news"
    )

    assert (
        record["content"]["title"]
        == "AI News"
    )

    assert (
        record["content"]["published_date"]
        == "2026-09-11T10:00:00+00:00"
    )

    assert record["collected_at"] is not None