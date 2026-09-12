import asyncio
import json
from pathlib import Path

from src.crawler.base import AsyncCrawler
from src.research.arxiv import ArxivClient
from src.research.paginator import ArxivPaginator
from src.extraction.record import build_research_paper_record


OUTPUT_FILE = Path("data/research_papers_100.json")


async def main():

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    try:

        client = ArxivClient(crawler)

        paginator = ArxivPaginator(
            client=client,
            page_size=10,
            delay_seconds=3
        )

        papers = await paginator.fetch_all(
            query="cat:cs.AI",
            max_papers=100
        )

        print("\nTotal unique papers:", len(papers))

        records = []

        for paper in papers:

            record = build_research_paper_record(
                paper
            )

            records.append(record)

        # Make sure the output directory exists.
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

        print(
            f"Saved {len(records)} records to "
            f"{OUTPUT_FILE}"
        )

        # Basic validation
        paper_urls = [
            record["content"]["paper_url"]
            for record in records
        ]

        unique_urls = set(paper_urls)

        print(
            "Unique paper URLs:",
            len(unique_urls)
        )

        if len(records) != 100:
            print(
                "\nWARNING: Expected 100 unique papers "
                f"but received {len(records)}."
            )
        else:
            print(
                "\nSUCCESS: Exactly 100 unique "
                "research papers collected."
            )

        if len(unique_urls) != len(records):
            print(
                "WARNING: Duplicate paper URLs detected."
            )
        else:
            print(
                "SUCCESS: No duplicate paper URLs."
            )

    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())