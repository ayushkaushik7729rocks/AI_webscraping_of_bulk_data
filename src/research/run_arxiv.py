import asyncio

from src.crawler.base import AsyncCrawler
from src.research.arxiv import ArxivClient


async def main():

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    arxiv = ArxivClient(crawler)

    papers = await arxiv.search(
        query="cat:cs.AI",
        start=0,
        max_results=5,
    )

    for paper in papers:

        print("\n-----------------------------")

        print("Title:", paper["title"])

        print("Authors:", paper["authors"])

        print("Published:", paper["published_date"])

        print("URL:", paper["paper_url"])

        print("Summary:", paper["summary"][:200])

    await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())