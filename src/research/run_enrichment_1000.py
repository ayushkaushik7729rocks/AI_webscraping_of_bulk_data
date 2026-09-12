import asyncio
import json
from pathlib import Path

from src.crawler.base import AsyncCrawler
from src.research.enrichment_checkpoint import (
    EnrichmentCheckpoint
)
from src.research.run_enrichment import enrich_papers


INPUT_FILE = Path(
    "data/research_papers_1000.json"
)

OUTPUT_FILE = Path(
    "data/research_papers_1000_enriched.json"
)

CHECKPOINT_FILE = Path(
    "data/research_enrichment_checkpoint.json"
)

BATCH_SIZE = 50

MAX_CONCURRENCY = 5


def convert_record_to_paper(record):
    """
    Convert our canonical research-paper record into
    the input format expected by enrich_papers().
    """

    content = record["content"]

    return {
        "title": content["title"],
        "authors": content["authors"],
        "paper_url": content["paper_url"],
        "published_date": content["published_date"],
        "github_url": content.get("github_url"),
        "github_stars": content.get("github_stars"),
        "links": [],
    }


async def enrich_batch(
    crawler,
    papers
):
    """
    Enrich one bounded batch.
    """

    return await enrich_papers(
        crawler=crawler,
        papers=papers,
        max_concurrency=MAX_CONCURRENCY
    )


async def main():

    print("=" * 50)
    print("FRONTIERATLAS - 1,000 PAPER GITHUB ENRICHMENT")
    print("=" * 50)

    # ---------------------------------------------------------
    # 1. Load original 1,000-paper dataset
    # ---------------------------------------------------------

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        original_records = json.load(file)

    print(
        f"\nLoaded {len(original_records)} papers."
    )

    # ---------------------------------------------------------
    # 2. Load enrichment checkpoint
    # ---------------------------------------------------------

    checkpoint = EnrichmentCheckpoint(
        CHECKPOINT_FILE
    )

    enriched_records = checkpoint.load()

    print(
        f"Checkpoint contains "
        f"{len(enriched_records)} enriched papers."
    )

    # ---------------------------------------------------------
    # 3. Build lookup of already-enriched URLs
    # ---------------------------------------------------------

    enriched_urls = {
        record["content"]["paper_url"]
        for record in enriched_records
        if record.get("content", {}).get("paper_url")
    }

    # ---------------------------------------------------------
    # 4. Find papers still needing enrichment
    # ---------------------------------------------------------

    remaining_records = [
        record
        for record in original_records
        if record["content"]["paper_url"]
        not in enriched_urls
    ]

    print(
        f"Papers remaining: "
        f"{len(remaining_records)}"
    )

    if not remaining_records:

        print(
            "\nAll papers are already enriched."
        )

        return

    # ---------------------------------------------------------
    # 5. Start crawler
    # ---------------------------------------------------------

    crawler = AsyncCrawler(
        max_concurrency=MAX_CONCURRENCY
    )

    await crawler.start()

    try:

        # -----------------------------------------------------
        # 6. Process bounded batches
        # -----------------------------------------------------

        for batch_start in range(
            0,
            len(remaining_records),
            BATCH_SIZE
        ):

            batch_records = remaining_records[
                batch_start:
                batch_start + BATCH_SIZE
            ]

            batch_number = (
                batch_start // BATCH_SIZE
            ) + 1

            total_batches = (
                (len(remaining_records) + BATCH_SIZE - 1)
                // BATCH_SIZE
            )

            print(
                f"\n----------------------------------------"
            )

            print(
                f"Batch {batch_number}/{total_batches}"
            )

            print(
                f"Processing "
                f"{len(batch_records)} papers..."
            )

            papers = [
                convert_record_to_paper(record)
                for record in batch_records
            ]

            batch_results = await enrich_batch(
                crawler,
                papers
            )

            # -------------------------------------------------
            # 7. Add successful results
            # -------------------------------------------------

            enriched_records.extend(
                batch_results
            )

            # -------------------------------------------------
            # 8. Save immediately after the batch
            # -------------------------------------------------

            checkpoint.save(
                enriched_records
            )

            print(
                f"Checkpoint saved."
            )

            print(
                f"Total enriched so far: "
                f"{len(enriched_records)}/"
                f"{len(original_records)}"
            )

    finally:

        await crawler.close()

    # ---------------------------------------------------------
    # 9. Save final enriched dataset
    # ---------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            enriched_records,
            file,
            indent=2,
            ensure_ascii=False
        )

    # ---------------------------------------------------------
    # 10. Calculate statistics
    # ---------------------------------------------------------

    github_found = sum(
        1
        for record in enriched_records
        if record["content"].get("github_url")
    )

    stars_found = sum(
        1
        for record in enriched_records
        if record["content"].get("github_stars")
        is not None
    )

    unique_urls = {
        record["content"]["paper_url"]
        for record in enriched_records
    }

    # ---------------------------------------------------------
    # 11. Final summary
    # ---------------------------------------------------------

    print("\n" + "=" * 50)
    print("FINAL ENRICHMENT SUMMARY")
    print("=" * 50)

    print(
        "Input papers:",
        len(original_records)
    )

    print(
        "Enriched records:",
        len(enriched_records)
    )

    print(
        "Unique paper URLs:",
        len(unique_urls)
    )

    print(
        "GitHub repositories found:",
        github_found
    )

    print(
        "GitHub star counts found:",
        stars_found
    )

    print(
        "Output:",
        OUTPUT_FILE
    )

    if len(enriched_records) == len(original_records):

        print(
            "\nSUCCESS: All 1,000 papers enriched."
        )

    else:

        print(
            "\nWARNING: Some papers were not enriched."
        )


if __name__ == "__main__":
    asyncio.run(main())