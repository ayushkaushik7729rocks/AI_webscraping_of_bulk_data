from datetime import datetime, timezone


def build_source_record(
    extracted_data,
    source_name
):

    return {
        "source": {
            "name": source_name,
            "url": extracted_data["url"],
        },
        "content": extracted_data,
        "collected_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def build_research_paper_record(paper):

    return {
        "schemaVersion": "1.0",
        "recordType": "research_paper",

        "source": {
            "name": "arXiv",
            "url": paper["paper_url"],
        },

        "content": {
            "title": paper["title"],
            "authors": paper["authors"],
            "paper_url": paper["paper_url"],
            "github_url": None,
            "github_stars": None,
            "published_date": paper["published_date"],
        },

        "collectedAt": datetime.now(
            timezone.utc
        ).isoformat(),
    }