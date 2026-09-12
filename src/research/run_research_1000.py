import asyncio
import json
from pathlib import Path

from src.crawler.base import AsyncCrawler
from src.extraction.record import build_research_paper_record
from src.research.arxiv import ArxivClient
from src.research.paginator import ArxivPaginator
from src.research.resumable_collector import ResumableResearchCollector


QUERY = "cat:cs.AI"

TARGET_COUNT = 1000

CHECKPOINT_FILE = Path(
    "data/research_papers_checkpoint.json"
)

OUTPUT_FILE = Path(
    "data/research_papers_1000.json"
)


async def main():

    print("=" * 50)
    print("FRONTIERATLAS - RESEARCH PAPER COLLECTION")
    print("=" * 50)

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    try:

        # -----------------------------------------------------
        # 1. Create ArXiv client
        # -----------------------------------------------------

        client = ArxivClient(crawler)

        # -----------------------------------------------------
        # 2. Create paginator
        # -----------------------------------------------------

        paginator = ArxivPaginator(
            client=client,
            page_size=100,
            delay_seconds=3
        )

        # -----------------------------------------------------
        # 3. Create resumable collector
        # -----------------------------------------------------

        collector = ResumableResearchCollector(
            paginator=paginator,
            checkpoint_file=CHECKPOINT_FILE
        )

        # -----------------------------------------------------
        # 4. Collect 1,000 unique papers
        # -----------------------------------------------------

        papers = await collector.collect(
            query=QUERY,
            target_count=TARGET_COUNT
        )

    finally:

        await crawler.close()

    # ---------------------------------------------------------
    # 5. Convert to canonical research-paper records
    # ---------------------------------------------------------

    records = []

    for paper in papers:

        record = build_research_paper_record(
            paper
        )

        records.append(record)

    # ---------------------------------------------------------
    # 6. Save final dataset
    # ---------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False
        )

    # ---------------------------------------------------------
    # 7. Validate final dataset
    # ---------------------------------------------------------

    paper_urls = [
        record["content"]["paper_url"]
        for record in records
    ]

    unique_urls = set(paper_urls)

    print("\n" + "=" * 50)
    print("FINAL COLLECTION SUMMARY")
    print("=" * 50)

    print(
        "Target papers:",
        TARGET_COUNT
    )

    print(
        "Collected papers:",
        len(records)
    )

    print(
        "Unique paper URLs:",
        len(unique_urls)
    )

    print(
        "Output:",
        OUTPUT_FILE
    )

    # ---------------------------------------------------------
    # 8. Final checks
    # ---------------------------------------------------------

    if len(records) != TARGET_COUNT:

        print(
            "\nWARNING:"
            f" Expected {TARGET_COUNT} papers, "
            f"but collected {len(records)}."
        )

    else:

        print(
            "\nSUCCESS:"
            " Exactly 1,000 papers collected."
        )

    if len(unique_urls) != len(records):

        print(
            "WARNING: Duplicate paper URLs detected."
        )

    else:

        print(
            "SUCCESS: No duplicate paper URLs."
        )


if __name__ == "__main__":
    asyncio.run(main())