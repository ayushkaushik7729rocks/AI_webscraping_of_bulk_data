import asyncio

from src.crawler.base import AsyncCrawler
from src.research.arxiv import ArxivClient
from src.research.paginator import ArxivPaginator
from src.extraction.record import build_research_paper_record


async def main():

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    client = ArxivClient(crawler)

    paginator = ArxivPaginator(
        client=client,
        page_size=10,
        delay_seconds=3
    )

    papers = await paginator.fetch_all(
        query="cat:cs.AI",
        max_papers=20
    )

    print("\nTotal papers:", len(papers))

    records = []

    for paper in papers:

        record = build_research_paper_record(
            paper
        )

        records.append(record)

        print("\n-----------------------------")
        print("Title:", record["content"]["title"])
        print("Authors:", record["content"]["authors"])
        print(
            "Published:",
            record["content"]["published_date"]
        )
        print(
            "Paper URL:",
            record["content"]["paper_url"]
        )
        print(
            "Links:",
            paper["links"]
        )
        print(
            "GitHub URL:",
            record["content"]["github_url"]
        )
        print(
            "GitHub Stars:",
            record["content"]["github_stars"]
        )
        print(
            "Collected At:",
            record["collectedAt"]
        )

    await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())